"""生成产品需求文档（PRD）"""
import os, sys
sys.path.insert(0, '.')
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# 设置默认字体
style = doc.styles['Normal']
style.font.name = 'Microsoft YaHei'
style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
style.font.size = Pt(10.5)

def add_heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
        if level == 1:
            run.font.color.rgb = RGBColor(26, 35, 126)
            run.font.size = Pt(18)
        elif level == 2:
            run.font.color.rgb = RGBColor(40, 53, 147)
            run.font.size = Pt(14)

def add_para(text='', bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(10.5)
    r.font.name = 'Microsoft YaHei'
    r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    r.bold = bold
    return p

def add_bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    r = p.add_run(text)
    r.font.size = Pt(10.5)
    return p

def add_image(path, width_inches=None, caption=''):
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        w = Inches(width_inches) if width_inches else None
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        try:
            run.add_picture(abs_path, width=w)
        except Exception as e:
            p.text = f'[图片加载失败: {e}]'
        if caption:
            cap_p = doc.add_paragraph(caption)
            cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in cap_p.runs:
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(100, 100, 100)
    else:
        add_para(f'[图片缺失: {path}]')

def add_table(rows_data, header=True):
    """rows_data: list of lists, first row is header"""
    t = doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
    t.style = 'Table Grid'
    for i, row in enumerate(rows_data):
        cells = t.rows[i].cells
        for j, text in enumerate(row):
            cells[j].text = str(text)
            for para in cells[j].paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9)
                    run.font.name = 'Microsoft YaHei'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
                    if header and i == 0:
                        run.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
            # 表头背景色
            if header and i == 0:
                shading = cells[j]._element.get_or_add_tcPr()
                from lxml import etree
                shd = etree.SubElement(shading, qn('w:shd'))
                shd.set(qn('w:fill'), '1A237E')
    return t

def add_note(text):
    p = doc.add_paragraph()
    r = p.add_run(f'💡 {text}')
    r.font.size = Pt(9.5)
    r.font.italic = True
    r.font.color.rgb = RGBColor(21, 101, 192)
    # 背景色
    shd = p._element.get_or_add_pPr().makeelement(qn('w:pPr'), {})
    pass

# ==================== 正文开始 ====================
# 封面
for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('微信公众号爆款内容发布系统')
r.bold = True
r.font.size = Pt(24)
r.font.color.rgb = RGBColor(26, 35, 126)
r.font.name = 'Microsoft YaHei'

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('产品需求文档（PRD）')
r.font.size = Pt(16)
r.font.color.rgb = RGBColor(102, 102, 102)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('WeChat-Publisher v1.0 | 2026-04-13')
r.font.size = Pt(12)
r.font.color.rgb = RGBColor(136, 136, 136)

doc.add_page_break()

# 一、项目概述
add_heading('一、项目概述')
add_para('本项目是一个面向微信公众号的全自动爆款内容生产与发布系统，通过AI技术实现从热点抓取、文章撰写、配图生成到一键发布的完整闭环。目标用户为个人自媒体运营者，核心价值在于大幅降低公众号运营成本，实现日更3篇的高频稳定产出。')
add_para()

add_table([
    ['项目名称', '微信公众号爆款内容发布系统'],
    ['技术栈', 'Python 3.x + Flask + YAML配置 + Playwright截图'],
    ['运行端口', 'http://127.0.0.1:8080（本地管理面板）'],
    ['发布频率', '每日 3 篇（08:00 / 12:30 / 18:30 三个时段）'],
    ['当前状态', '✅ 全部模块开发完成，待配置AppID/Secret后可正式发布'],
])

# 二、系统架构
add_heading('二、系统架构')
add_heading('2.1 核心流水线', level=2)
add_para('系统采用五步流水线架构，每一步均可独立运行或串联执行：')

add_table([
    ['步骤', '模块名称', '功能描述'],
    ['① 抓取', 'HotTopicFetcher', '从多平台抓取当日热点话题，筛选高流量、高质量话题'],
    ['② 写作', 'ArticleGenerator', '基于热点话题撰写第一人称+娱乐性风格文章（AI评分<40）'],
    ['③ 配图', 'ImageGenModule', '生成横版1280×720高清AI配图，中文标题封面图'],
    ['④ 预览', 'HTML Preview', '生成微信公众号风格HTML预览页面，支持长截图导出'],
    ['⑤ 发布', 'WeChatPublisher', '通过微信API一键发布到指定公众号'],
])

# 三、界面需求
add_heading('三、界面需求')
add_heading('3.1 管理仪表盘（首页）', level=2)
add_para('用户登录后的主界面，展示系统状态和快捷操作入口。采用深色主题设计。')
add_image('../output/dashboard_screenshot_viewport.png', width_inches=5.5, caption='【图1】管理仪表盘界面 — 深色主题，展示今日发布进度、快捷操作按钮、最近记录')

add_table([
    ['UI元素', '需求说明'],
    ['今日已发布', '显示今日发布进度：已完成/目标（如 0/3），下方显示发布时段'],
    ['成功发布', '累计成功发布的文章数量'],
    ['微信状态', '显示公众号绑定状态：✅ 已连接 / ⚠ 未配置（引导去设置页填写AppID）'],
    ['定时任务', '显示定时任务开关状态、发布时段配置、自动定时发布开关'],
    ['快捷按钮组', '三个主要操作：🔥抓取热门话题 / ✏️创建新文章 / 🚀一键生成+发布'],
    ['最近发布记录', '显示最近N篇发布历史，空态时展示引导文案'],
    ['底部功能卡片', '四个步骤提示卡片：①抓取热点 → ②AI写作 → ③配图生成 → ④一键发布'],
    ['顶部导航栏', '五个Tab切换：仪表盘 | 热门话题 | 文章编辑 | 发布管理 | 设置'],
])

add_heading('3.2 文章预览页面', level=2)
add_para('文章生成完成后的预览界面，模拟微信公众号文章的真实阅读效果。手机端宽度适配（430px）。')
add_image('../output/article_preview_screen.png', width_inches=4, caption='【图2】文章预览界面 — 公众号风格排版，横版配图嵌入段落间')

add_table([
    ['UI元素', '需求说明'],
    ['头部区域', '深蓝色渐变背景 + 文章标题（支持emoji前缀增强吸引力）'],
    ['封面图', '横版1280×720杂志风格封面图，全中文标题文字'],
    ['正文内容', '分段排版（4-6段），绿色竖线标注小标题，段落间嵌入配图'],
    ['段落配图', '横版约16:9比例（1376×768），嵌入段落之间不喧宾夺主'],
    ['底部区域', '口语化结尾互动（"你怎么看？评论区聊聊"等）'],
])

add_para()
add_para('⚠ 重要：预览页面不得暴露任何"AI生成"痕迹！禁止显示：生成时间、AI写作标识、工具信息等。', bold=False)

# 四、功能需求清单
doc.add_page_break()
add_heading('四、功能需求清单')

add_heading('4.1 热点采集模块（R1-R3）', level=2)
for item in [
    "R1：每日自动抓取TOP 10热点话题，覆盖微博/百度/知乎等多平台",
    "R2：每条话题附带热度指数、来源链接、摘要描述",
    "R3：支持手动触发抓取和定时自动抓取两种模式",
]:
    add_bullet(item)

add_heading('4.2 AI文章生成模块（R4-R12）', level=2)
for item in [
    "R4：基于热点话题自动生成1200-2000字公众号风格文章",
    'R5：第一人称叙述视角（"我""我觉得""说实话"等口语化表达）',
    "R6：娱乐化/评论化写作风格，避免新闻通稿体",
    "R7：目标AI评分控制在40分以下（人写风格）",
    "R8：法律风险自动检测——政治敏感词阻断、人身权益警告、商业合规提醒",
    "R9：文章结构包含：吸引眼球的标题 + 分段正文(4-6段) + 口语化结尾互动",
    'R10：禁止使用AI套路表达（首先/其次/综上所述/让我们共同期待等）',
    "R11：注入主观态度和个人观点（'以我的经验来看''最让我意外的是'）",
    "R12：文末自动添加免责声明（仅供参考，不构成投资建议）",
]:
    add_bullet(item)

add_heading('4.3 配图生成模块（R13-R19）', level=2)
for item in [
    "R13：封面图为横版1280×720像素（16:9比例）",
    "R14：段落配图为横版约1376×768像素（约16:9比例）",
    "R15：所有配图必须包含中文文字标题（面向国内受众）",
    "R16：配图中严禁出现人物、人脸、政治敏感内容",
    "R17：科技风/未来感视觉风格，贴合文章话题内容",
    "R18：图片安全后缀强制追加：no people, no human, no face, safe for work",
    "R19：Pollinations占位图自动检测并重试机制（MD5签名识别）",
]:
    add_bullet(item)

add_heading('4.4 竞品分析系统（R20-R27）', level=2)
for item in [
    "R20：每小时自动执行一轮竞品数据采集（08:00-23:00）",
    "R21：每轮采集10个热点 × 每个热点3篇竞品文章 = 30篇/轮",
    "R22：对每篇文章进行6维度AI评分检测（0-100分）",
    "R23：AI分类标准：<30分人写 / 30-50疑似AI / 50-70很可能AI / >70几乎确定AI",
    "R24：数据持久化存储为JSON文件，按日期归档",
    "R25：补跑模式——每次对话打开自动检测缺失小时段并补齐",
    "R26：可视化简报——热力图、AI分布、账号排行、高低AI文章TOP榜单",
    "R27：重点追踪低AI评分(<40)文章的写作特征，反哺优化自身写作风格",
]:
    add_bullet(item)

add_heading('4.5 自动化调度模块（R28-R31）', level=2)
for item in [
    "R28：定时任务支持按小时触发（FREQ=HOURLY;INTERVAL=1）",
    "R29：支持一次性定时任务（scheduleType=once + scheduledAt）",
    "R30：任务有效期控制（validFrom / validUntil参数）",
    "R31：单次执行超时保护（maxDurationMinutes限制）",
]:
    add_bullet(item)

add_heading('4.6 安全与合规（R32-R36）', level=2)
for item in [
    "R32：config.yaml（含AppID/Secret）绝不入库Git，已在.gitignore排除",
    "R33：政治敏感词命中直接阻断（台独/法轮功/领导人评价等）",
    'R34：商业推荐类内容必须附加"不构成投资建议"免责声明',
    "R35：人身攻击/隐私泄露类表述自动标记警告",
    "R36：所有对外可见内容不得暴露AI工具使用痕迹",
]:
    add_bullet(item)

# 五、交互体验需求
doc.add_page_break()
add_heading('五、交互体验需求')
add_heading('5.1 可点击元素提亮反馈', level=2)
add_para('所有可交互元素在鼠标悬停时必须有明显的视觉反馈，让用户一眼识别可操作区域：')

add_table([
    ['元素类型', '悬停效果', '视觉变化'],
    ['概览卡片', '上浮+放大1.03倍', '蓝色阴影光晕+亮度提升+pointer手型'],
    ['时间标签', '上浮+发光边框', '对应颜色发光+阴影扩散+z-index提升'],
    ['热点列表项', '右滑4px+蓝条指示器', '蓝色阴影+浅蓝底色背景'],
    ['表格行', '微缩放', '黄色阴影光晕突出行'],
    ['评分标签', '放大1.1倍', '同色系加深背景+彩色投影'],
    ['AI进度条', '纵向放大1.15倍', '亮度提升+阴影'],
    ['发现框', '右滑4px', '左边框加粗+阴影光晕'],
    ['头部区域', '-', '蓝色阴影扩散加深'],
])

add_heading('5.2 简报可视化交互', level=2)
for item in [
    "时段热力图：鼠标悬浮显示该小时的具体数据（轮次/文章数/平均AI分）",
    "账号排行表：点击可展开该账号的所有文章详情",
    "AI分布柱状图：悬浮显示各区间的具体文章数和占比",
    "高/低AI文章列表：点击可查看全文和详细评分报告",
    "全局过渡动画：所有元素状态变化都有0.2s平滑过渡",
]:
    add_bullet(item)

# 六、数据规格
add_heading('六、数据规格')
add_heading('6.1 竞品分析数据规模（截至2026-04-13）', level=2)

add_table([
    ['指标', '数值', '说明'],
    ['总采集轮次', '59 轮', '覆盖04-11至04-13共3天'],
    ['总文章数', '1,695 篇', '每轮10热点×3竞品=30篇'],
    ['监控账号数', '30+ 个', '涵盖各领域头部公众号'],
    ['平均AI评分', '46.3 分', '中等偏人写水平'],
    ['人写风格(<40)', '478篇 (28.2%)', '✅ 学习模仿对象'],
    ['确认AI(>70)', '267篇 (15.8%)', '⚠ 反面教材避坑'],
    ['模糊地带(40-70)', '950篇 (56.0%)', '🎯 我们的目标区间'],
])

add_heading('6.2 时段覆盖率', level=2)
add_para('04-13当天实现了全天候24时段全覆盖（00:00-23:00），无任何缺口。自动化补跑模式运行稳定。')

# 七、商业化规划
doc.add_page_break()
add_heading('七、商业化规划')
add_heading('7.1 收入预期（基于行业数据分析）', level=2)

add_table([
    ['阶段', '日收入预估', '月收入预估', '关键条件', '周期'],
    ['起步期', '¥15-50/天', '¥360-1,440/月', '新号纯流量主', '1-2月'],
    ['成长期', '¥135-360/天', '¥4,050-10,800/月', '有粉丝基础+原创', '3-6月'],
    ['成熟期', '¥600-3,000+/天', '¥18,000-90,000/月', '爆款+品牌广告', '6月+'],
])

add_heading('7.2 矩阵账号策略', level=2)
add_para('根据2025年3月最新规则，注册限制如下：')

add_table([
    ['主体类型', '可注册数量', '建议方案'],
    ['个人（身份证）', '仅1个', '作为主号，先跑通变现流程'],
    ['企业/公司', '仅2个', '可申请提额到5-10个'],
    ['个体工商户', '仅2个', '性价比最高，注册简单+可提额'],
    ['推荐组合', '6个号', '1个人号 + 1个体户(5个号)，分不同垂直领域'],
])

add_para()
add_para('💡 建议路径：先用1个号跑通全流程验证变现能力（目标月入3000+），再考虑矩阵扩量。')

# 结尾
doc.add_paragraph()
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('—— 文档结束 ——')
r.font.color.rgb = RGBColor(153, 153, 153)
r.font.size = Pt(10)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('最后更新：2026年4月13日 20:19 | 机密文档')
r.font.color.rgb = RGBColor(170, 170, 170)
r.font.size = Pt(9)

# 保存
output_path = r'c:\Users\v_junshshi\WorkBuddy\Claw\output\PRD_微信公众号爆款内容发布系统.docx'
doc.save(output_path)
print(f'DOCX saved to {output_path}')
