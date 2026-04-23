# 糖渍游记 (Tangzi Travel VLOG)

> AI动画宠物IP VLOG项目 — 抖音竖屏短视频系列

## 项目简介

**糖渍**（Tangzi）是一只中华田园橘猫，浅奶油色橘虎斑花色。本项目用AI技术（Kling v2.6图生视频）制作糖渍的拟人化旅行VLOG，发布于抖音平台。

**账号名**: 糖渍游记
**赛道**: AI动画宠物IP VLOG（竖屏9:16）
**主角**: 糖渍（雪团子）— 双足直立拟人化猫咪

---

## 目录结构

```
douyin-project/
├── README.md                    # 本文件 - 项目说明与资源索引
├── six-views/                   # 角色六视图（I2V参考图核心）
│   ├── cell_0_0.png            # [0,0] 正面 ← **主要参考图**
│   ├── cell_0_1.png            # [0,1] 正面偏左30°
│   ├── cell_0_2.png            # [0,2] 左侧面
│   ├── cell_1_0.png            # [1,0] 正面偏右30°
│   ├── cell_1_1.png            # [1,1] 背面偏右30°
│   ├── cell_1_2.png            # [1,2] 右侧面
│   └── tangzi_6view_small.png  # 六视图缩略总览
│
├── assets/                      # I2V输入素材
│   ├── tangzi_front_view.png   # 正面站姿（已推送到GitHub ✅）
│   └── tangzi_sitting_front.png# 坐姿正面（毛线球场景专用）
│
├── videos/                      # 最终版视频输出
│   ├── tangzi_blink_wave_v5.mp4     # ⭐ 眨眼+举手+摇尾（动作验证通过）
│   └── tangzi_yarnball_v6b.mp4      # ⭐ 毛线球砸头场景（草地+互动）
│
├── videos/archive/              # 历史版本存档
│
├── scripts/                     # 工具脚本
│   ├── gen_video_v3.py          # COS URL方案生成器
│   └── gen_video_v4.py          # 多图床上传+自动降级方案
│
├── reference/                   # AI生成参考图
│   ├── tangzi_reference.png     # 综合参考图
│   └── tangzi_front_portrait.png # 正面肖像
│
├── docs/                        # 项目文档
│   ├── 00_项目总览.md           # 项目整体规划
│   ├── 01_角色设定_糖渍.md      # 角色详细设定
│   ├── 02_全12集_机甲设计大全.md # 机甲装备设计
│   ├── 03_E01-上集_成都VLOG_分镜.md
│   ├── 04_E01-下集_熊猫机甲觉醒_分镜.md
│   ├── E01上集_视频生成中文提示词.md
│   ├── E01上集_视频生成提示词_豆包适配版.md
│   ├── 竞品知识库_抖音AI动画宠物赛道.md
│   └── keyframes/E01/           # E01关键帧图片
│
├── reference-cats/              # 竞品角色参考库
│   ├── lihua/                   # 灰狸花参考（30张）
│   └── orange/                  # 橘猫参考（33张）
│
├── output/                      # E01成片输出
│   ├── E01_上集_成都观光篇.mp4
│   └── E01_下集_锦里吃货篇.mp4
│
└── episodes_data.json           # 全12集数据
```

---

## 角色设定：糖渍

### 基础信息
| 属性 | 描述 |
|------|------|
| 名字 | 糖渍（雪团子） |
| 品种 | 中华田园橘猫 |
| 花色 | 浅奶油色橘虎斑 |
| 体态 | 圆润Q弹，微胖 |

### 核心外观特征
- **面部**：圆脸、粉色鼻头、琥珀色大眼睛
- **毛发**：浅奶油底色 + 淡橘色虎斑条纹
- **配饰**：
  - 白色鸭舌帽
  - 牛仔蓝背包（带熊猫挂件+鱼吊坠）
  - 红帆布鞋
  - 粉壳手机
  - 红围兜（粽子刺绣）

### 性格特点
- 好奇心强 → 什么都想摸一摸
- 爱吃 → 见到食物走不动路
- 有点憨 → 经常出糗但自己不觉得
- 乐观 → 遇到倒霉事也能自嘲

### 拟人化风格
- 双足直立行走
- 前爪当手使用（拿东西、比手势）
- 可穿戴人类配饰和服装
- 保持猫脸不变（萌点核心）
- 写实摄影质感（毛发物理级渲染）

---

## 视频生成管线（已验证可用）

### 技术栈
```
多模态内容生成技能 → connect_cloud_service(获取凭证)
→ buddy-cloud.py → 腾讯云混元 → Kling v2.6 图生视频(I2V)
```

### 标准流程（6步）

| 步骤 | 操作 | 关键要点 |
|------|------|---------|
| 1 | 准备参考图 | 使用 `assets/tangzi_front_view.png`（原始六视图正面） |
| 2 | 上传到GitHub | `git push` 到仓库 → jsDelivr CDN加速 |
| 3 | 构造图片URL | `cdn.jsdelivr.net/gh/jasonclup/AI_gzh@master/douyin-project/assets/xxx.png` ⚠️ 用 `@master` 不是 `@main` |
| 4 | 获取凭证 | 调 `connect_cloud_service` → 拿 tempToken（每次必须重新获取） |
| 5 | 提交任务 | `buddy-cloud.py video "PROMPT" --image URL --aspect-ratio 9:16 --duration 10 --token XXX` |
| 6 | 下载结果 | status轮询 → result_url → curl下载 |

### Prompt写作规范

#### 防幻觉铁律
- 必须写 `one tail only` / `one cat only` / `single cat`
- 动作拆解为步骤：先A → 再B → 最后C
- 每步只描述1-2个具体肢体部位

#### Prompt模板结构
```
[角色外观描述：品种/毛色/配饰] +
[环境场景设定] +
[分步动作序列] +
[防幻觉约束] +
[一致性要求]
```

#### 示例Prompt（眨眼挥手）
```
A cute cream-colored tabby cat (Chinese village cat) with light orange-cream fur
and pale ginger stripes, wearing a white baseball cap and a red bandana.
The cat blinks twice slowly, then raises both front paws in a cute wave gesture,
then sways its tail left and right two times.
One cat only, one tail only, no other animals.
The cat maintains the same face, same white cap, same red bandana.
```

---

## GitHub资源URL速查表

### 图片资源（jsDeliv CDN）

| 文件 | jsDeliv URL | 用途 |
|------|------------|------|
| 正面站姿 | `.../assets/tangzi_front_view.png` | **主要I2V参考图** |
| 坐姿正面 | `.../assets/tangzi_sitting_front.png` | 坐姿场景参考 |
| 六视图[0,0] | `.../six-views/cell_0_0.png` | 原始六视图正面 |

> 完整URL前缀：`https://cdn.jsdelivr.net/gh/jasonclup/AI_gzh@master/douyin-project/`

### 已验证通过的成品视频

| 版本 | 文件 | 场景 | 状态 |
|------|------|------|------|
| V5 | `videos/tangzi_blink_wave_v5.mp4` | 眨眼×2 + 举双手 + 摇尾×2 | ✅ 通过 |
| V6B | `videos/tangzi_yarnball_v6b.mp4` | 草地 + 毛线球砸头→摸头→扒开→舔手 | ✅ 通过 |

---

## 开发历史

| 日期 | 里程碑 |
|------|--------|
| 2026-04-21 | 项目启动，确定糖渍角色设定和六视图设计 |
| 2026-04-22 | E01分镜完成，关键帧生成，首次尝试视频生成 |
| 2026-04-23 | **管线突破日** — jsDeliv CDN方案验证 + I2V角色一致性解决 + V5/V6B通过 |

---

## 相关链接

- GitHub仓库: https://github.com/jasonclup/AI_gzh/tree/master/douyin-project
- 抖音账号: 糖渍游记
- 底层引擎: Kling v2.6 (腾讯云混元)

---
*最后更新: 2026-04-23*
