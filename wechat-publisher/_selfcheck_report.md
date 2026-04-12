# 微信公众号爆款内容发布系统 — 全面自检报告

> 检查时间：2026-04-09 16:04  
> 检查范围：全部模块代码审查（16个Python文件 + 配置 + 前端）

---

## 📋 总览

| 模块 | 状态 | 说明 |
|------|------|------|
| 🔥 热点抓取 | ✅ 正常 | 3个源+内置兜底，8s超时 |
| 📝 文章生成 | ⚠️ 可用 | 模板引擎，非AI，质量一般 |
| 🖼️ AI文生图(server.py) | ✅ 正常 | Pollinations.ai + 重试/缓存 |
| 🖼️ AI文生图(web/app.py) | ❌ 问题 | 还在用旧版Pillow占位图 |
| 🌐 外网连接 | ✅ 正常 | urllib标准库，多源降级 |
| 🔗 微信绑定 | ⏳ 待配置 | AppID/Secret为空，需用户填写 |
| 📤 一键发布(server.py) | ❌ 缺失 | 无发布API接口 |
| 📤 一键发布(web/app.py) | ⚠️ 有接口 | 但有代码bug |
| ⏰ 定时任务 | ⚠️ 部分可用 | 调度器完整但依赖旧配图模块 |
| 🌐 前端页面 | ✅ 存在 | 6个模板 + 2个独立HTML |

---

## 一、绑定账号（微信公众号）

### 当前状态：⏳ 待配置（非代码问题）

**文件**：`config.yaml` 第30-32行
```yaml
WECHAT_APPID: ""
WECHAT_SECRET: ""
WECHAT_TOKEN: ""
```

**文件**：`modules/wechat_api.py`

| 功能 | 状态 | 说明 |
|------|------|------|
| `is_configured()` | ✅ | 正确检测AppID/Secret是否为空 |
| `_get_access_token()` | ✅ | 自动获取+缓存token，提前5分钟刷新 |
| `upload_image()` | ✅ | 上传永久素材，带缓存 |
| `upload_temp_image()` | ✅ | 上传临时素材(3天有效)，返回URL |
| `_save_draft()` | ✅ | 保存草稿接口正确 |

### 🐛 发现的Bug

**Bug #1 — 严重**：`_publish_free()` 方法引用了未定义变量

位置：`modules/wechat_api.py` 第190-192行

```python
if publish_now:
    # 免费订阅号不支持直接发布，只能通过草稿+群发接口
    result = self._publish_free(account_data)  # ❌ account_data 未定义！
```

问题：`account_data` 这个变量在作用域内不存在。应该先调用 `_save_draft()` 获取 media_id，再用 media_id 调用群发接口。

修复建议：
```python
if publish_now:
    # 先保存草稿获取 media_id
    draft_result = self._save_draft(token, article_data)
    media_id = draft_result.get('media_id', '')
    result = self._publish_free(token, media_id)
```

---

## 二、一键发布功能

### server.py（主服务器，端口8080）

**❌ 缺少发布相关API接口**

当前 `server.py` 只有以下接口：
- `GET /` — 首页
- `GET /topics` — 话题页面
- `GET /editor` — 编辑器页面
- `POST /api/article/generate` — 生成文章
- `POST /api/image/generate` — 生成图片
- `GET /api/topics/fetch` — 抓取热点
- `GET /article/styles` — 写作风格列表
- `GET /publish` — 发布页面（仅渲染模板）
- `GET /settings` — 设置页面（仅渲染模板）

**缺少的关键接口：**
- ❌ `POST /api/publish` — 发布文章到公众号
- ❌ `POST /api/settings/wechat` — 保存微信配置
- ❌ `GET/POST /api/scheduler/*` — 定时任务控制

### web/app.py（Web管理面板）

**⚠️ 接口齐全但有问题**

已有接口：
- ✅ `POST /api/publish` — 发布文章
- ✅ `POST /api/settings/wechat` — 保存配置
- ✅ `GET/POST /api/scheduler/*` — 定时任务

但这个应用和 `server.py` 是**两个独立的Flask应用**，端口冲突（都用8080）。

---

## 三、连接外网（热点抓取）

### 当前状态：✅ 正常

**文件**：`modules/hot_topics.py`

| 数据源 | 类型 | 状态 | 备注 |
|--------|------|------|------|
| 今日头条 | JSON API | ✅ 主要源 | toutiao.com/hot-event/hot-board |
| 百度热搜 | HTML解析 | ✅ 备选 | top.baidu.com/board |
| Tophub微博 | HTML解析 | ✅ 备选 | tophub.today |
| 内置兜底 | 静态数据 | ✅ 保底 | 20条科技热点 |

**设计亮点：**
- 所有请求8秒超时，不会卡死
- urllib标准库，无额外依赖
- 自动编码检测(UTF-8/GBK/GB2312)
- 标题去重 + 科技优先排序
- 任意源失败不影响整体

---

## 四、AI文生图（图片生成）

### ⚠️ 双轨制问题 — 这是最大的架构问题！

项目中存在**两套图片生成系统**：

#### 系统 A：`tools/image_helper.py`（v3，新，✅ 推荐）

```
策略链：缓存检查 → Pollinations.ai(AI文生图) → Pillow兜底
特性：重试机制、模型轮换、MD5缓存、11种主题风格映射
输出尺寸：1080x1920 竖屏（符合规范）
```

**被谁使用**：`server.py` 的文章生成和图片生成API

#### 系统 B：`modules/image_generator.py`（旧，❌ 已过时）

```
策略：Pillow画渐变背景+几何图形（占位符）
输出尺寸：900x500 横屏（不符合竖屏规范）
说明：注释写着"实际部署时替换为真实图片生成"
```

**被谁使用**：`web/app.py` 和 `modules/scheduler.py`

### 具体影响

| 调用路径 | 使用哪个系统 | 图片质量 |
|----------|-------------|---------|
| server.py → /api/article/generate | ✅ image_helper.py (v3) | AI真实照片 |
| server.py → /api/image/generate | ✅ image_helper.py (v3) | AI真实照片 |
| web/app.py → /api/article/generate | ❌ image_generator.py (旧) | 枕头占位图 |
| scheduler.py → _scheduled_publish | ❌ image_generator.py (旧) | 枕头占位图 |

### Pollinations.ai 详细状态

| 项目 | 状态 |
|------|------|
| API地址 | https://image.pollinations.ai/prompt/{prompt} |
| API Key | 不需要（免费） |
| 支持模型 | flux, flux-realism, flux-cablyai, flux-anime, turbo (5种) |
| 重试机制 | 每模型3次，指数退避，最大等待30秒 |
| 缓存机制 | MD5(prompt\|size) → .image_cache/ 目录 |
| 输出验证 | PIL.Image.verify() + 文件大小>5KB检查 |
| 兜底方案 | Pillow渐变背景图 |

---

## 五、文章生成（写作引擎）

### 当前状态：⚠️ 模板引擎（非AI生成）

**文件**：`modules/article_generator.py`（57KB，非常详细）

| 特性 | 详情 |
|------|------|
| 引擎类型 | 模板填充（非LLM/AI） |
| 写作风格 | 4种：客观分析、深度解读、热点评论、科普讲解 |
| 段落结构 | 开头→背景→经过→分析→展望→结尾（固定6段） |
| 内容分类 | AI/科技/汽车/芯片/金融/加密货币/社会（7大类） |
| 填充词库 | 每类100+个填充变量，按话题智能匹配 |
| 高亮提取 | 自动识别 **加粗** 内容作为重点 |
| 配图提示 | 每段自动生成image_hint |
| 爆款标题 | 每个话题生成10种爆款标题变体 |

**优点：**
- ⚡ 毫秒级生成，无需外部API
- 💰 零成本，无API费用
- 🔄 确定性输出，相同输入风格稳定
- 📦 离线可用

**缺点：**
- 🤖 不是真正的AI写作，内容偏"模板感"
- 🔄 同一话题多次生成变化有限（受限于随机种子+日期）
- 📰 无法结合实时事件细节（填充词是预设的）

---

## 六、其他发现的问题

### 🐛 Bug #2 — 中等：server.py 设置页面硬编码

位置：`server.py` 第312行
```python
def settings_page():
    return render_template('settings.html', configured=False, appid='', secret='')
```
始终显示"未配置"，不会读取实际config.yaml的值。

### 🐛 Bug #3 — 低：socket.setdefaulttimeout 全局污染

位置：`modules/hot_topics.py` 第69行
```python
socket.setdefaulttimeout(timeout)
```
这会设置全局socket超时，可能影响其他网络操作。

### ⚠️ 架构问题 #1 — 双Flask应用混乱

`server.py` 和 `web/app.py` 是两个独立的Flask app：
- `server.py`：轻量级，直接服务静态HTML，使用新的image_helper
- `web/app.py`：重量级，使用Jinja2模板，使用旧的image_generator
- 两者都用端口8080，不能同时运行
- 功能分布不清晰，用户不知道该启动哪个

### ⚠️ 架构问题 #2 — image_generator.py 是死代码

`modules/image_generator.py` 只生成Pillow占位图，已被 `tools/image_helper.py` 完全取代。
但 `web/app.py` 和 `scheduler.py` 仍然在导入它。

### ⚠️ 功能缺失 — server.py 没有"发布"按钮的后端

前端可能有发布按钮，但 server.py 没有对应的发布API。
用户在 server.py 环境下无法完成"一键发布"操作。

---

## 七、优先级修复建议

### 🔴 P0 — 必须修复（影响核心功能）

| # | 问题 | 修复方式 | 工作量 |
|---|------|---------|--------|
| 1 | wechat_api.py `_publish_free` 变量未定义 | 修正参数传递逻辑 | 10min |
| 2 | web/app.py 使用旧版配图模块 | 改为调用 tools/image_helper.py | 30min |
| 3 | server.py 缺少发布/设置API | 从 web/app.py 移植或统一入口 | 1h |

### 🟡 P1 — 应该修复（影响体验）

| # | 问题 | 修复方式 | 工作量 |
|---|------|---------|--------|
| 4 | 双Flask应用混乱 | 合并为一个入口，或明确分工 | 2h |
| 5 | scheduler.py 使用旧版配图 | 同#2，改为 image_helper.py | 20min |
| 6 | settings_page 硬编码 | 读取 config.yaml 实际值 | 10min |

### 🟢 P2 — 可以优化（锦上添花）

| # | 问题 | 修复方式 | 工作量 |
|---|------|---------|--------|
| 7 | socket全局超时污染 | 改为逐请求设置timeout参数 | 10min |
| 8 | image_generator.py 死代码 | 删除或标记deprecated | 5min |
| 9 | 文章生成非AI | 接入LLM API（可选） | 按需 |

---

## 八、启动使用指南

### 当前可用的方式

```bash
cd wechat-publisher
python server.py
# 访问 http://127.0.0.1:8080
```

### 可以正常工作的流程

1. ✅ 打开首页 → 查看仪表盘
2. ✅ 进入 /topics → 抓取热点（外网或内置兜底）
3. ✅ 选择话题 → 生成文章（6段模板文章）
4. ✅ 自动配图（AI文生图，Pollinations.ai）
5. ✅ 在编辑器预览/编辑文章和图片
6. ❌ **发布到公众号** → 缺少后端接口
7. ❌ **绑定微信账号** → 缺少设置保存接口

### 要完整使用需要做的（按顺序）

1. **修复 Bug #1**（wechat_api.py 第192行）
2. **给 server.py 补上发布和设置API**
3. **在 config.yaml 填入真实的 AppID 和 Secret**
4. 启动 server.py → 设置页绑定账号 → 选话题 → 生成 → 发布

---

*报告完成。如需立即修复某个具体问题，告诉我编号即可动手。*
