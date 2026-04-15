const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, ImageRun, PageBreak, LevelFormat } = require('docx');
const fs = require('fs');

// 图片路径
const imgDir = 'c:/Users/v_junshshi/WorkBuddy/Claw/output';

// 读取图片
function readImg(name) {
    const p = `${imgDir}/${name}`;
    if (fs.existsSync(p)) return fs.readFileSync(p);
    console.warn(`Missing: ${p}`);
    return null;
}

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cell = (content, opts) => new TableCell({
    borders, width: { size: opts.width || 4680, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: typeof content === 'string' ? [new TextRun(content)] : content })]
});
const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 400, after: 200 },
    children: [new TextRun({ text: t, bold: true, size: 32, color: "1a237e" })] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 300, after: 150 },
    children: [new TextRun({ text: t, bold: true, size: 26, color: "283593" })] });
const h3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 100 },
    children: [new TextRun({ text: t, bold: true, size: 22 })] });
const p = (t, opts) => new Paragraph({ spacing: { after: 120 }, ...opts,
    children: [new TextRun({ text: t, size: 21 })] });
const bullet = (text, ref) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60 },
    children: [new TextRun({ text, size: 21 })] });
const imgPara = (name, w, h) => {
    const data = readImg(name);
    if (!data) return p(`[图片缺失: ${name}]`);
    return new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 150, after: 200 },
        children: [new ImageRun({ type: 'png', data, transformation: { width: w, height: h },
            altText: { title: name, description: name, name: name } })]
    });
};
const note = t => new Paragraph({ shading: { fill: "E8F0FE", type: ShadingType.CLEAR },
    indent: { left: 360, right: 360 }, spacing: { before: 100, after: 100 },
    children: [new TextRun({ text: `💡 ${t}`, size: 20, italics: true, color: "1565C0" })] });

const doc = new Document({
    styles: {
        default: { document: { run: { font: "Microsoft YaHei", size: 21 } } },
        paragraphStyles: [
            { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 32, bold: true, font: "Microsoft YaHei", color: "1a237e" },
                paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
            { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 26, bold: true, font: "Microsoft YaHei", color: "283593" },
                paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
            { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 22, bold: true, font: "Microsoft YaHei" },
                paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
        ]
    },
    numbering: {
        config: [
            { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
                alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
            { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
                alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
            { reference: "reqs", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "R%1.",
                alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
            { reference: "ui-nums", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
                alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        ]
    },
    sections: [{
        properties: {
            page: { size: { width: 11906, height: 16838 }, margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } }
        },
        headers: {
            default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
                children: [new TextRun({ text: "微信公众号爆款内容发布系统 \u2014 产品需求文档", size: 18, color: "999999" })] })] })
        },
        footers: {
            default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "第 ", size: 18 }), new TextRun({ children: [require('docx').PageNumber.CURRENT], size: 18 }),
                    new TextRun({ text: " 页 | 机密文档", size: 18 })] })] })
        },
        children: [
            // ========== 封面 ==========
            new Paragraph({ spacing: { before: 1200 } }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
                children: [new TextRun({ text: "微信公众号爆款内容发布系统", bold: true, size: 48, color: "1a237e" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
                children: [new TextRun({ text: "产品需求文档（PRD）", size: 28, color: "666666" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
                children: [new TextRun({ text: "WeChat-Publisher v1.0", size: 24, color: "888888" })] }),

            h1("一、项目概述"),
            p("本项目是一个面向微信公众号的全自动爆款内容生产与发布系统，通过AI技术实现从热点抓取、文章撰写、配图生成到一键发布的完整闭环。目标用户为个人自媒体运营者，核心价值在于大幅降低公众号运营成本，实现日更3篇的高频稳定产出。"),

            // 核心数据表格
            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [2500, 7226], rows: [
                new TableRow({ children: [cell("项目名称", { width: 2500, fill: "E8EAF6" }), cell("微信公众号爆款内容发布系统")] }),
                new TableRow({ children: [cell("技术栈", { width: 2500, fill: "E8EAF6" }), cell("Python 3.x + Flask + YAML配置 + Playwright截图")] }),
                new TableRow({ children: [cell("运行端口", { width: 2500, fill: "E8EAF6" }), cell("http://127.0.0.1:8080（本地管理面板）")] }),
                new TableRow({ children: [cell("发布频率", { width: 2500, fill: "E8EAF6" }), cell("每日 3 篇（08:00 / 12:30 / 18:30 三个时段）")] }),
                new TableRow({ children: [cell("当前状态", { width: 2500, fill: "E8EAF6" }), cell("\u2705 全部模块开发完成，待配置AppID/Secret后可正式发布")] }),
            ]}),

            h1("二、系统架构"),
            h2("2.1 核心流水线"),
            p("系统采用五步流水线架构，每一步均可独立运行或串联执行："),
            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [1300, 2200, 6226], rows: [
                new TableRow({ children: [
                    cell("步骤", { width: 1300, fill: "1A237E" }),
                    cell("模块名称", { width: 2200, fill: "1A237E" }),
                    cell("功能描述", { width: 6226, fill: "1A237E" })
                ].map(c => {
                    c.children[0].children[0].children[0] = new TextRun({ text: c.children[0].children[0].children[0].text || "", bold: true, color: "FFFFFF", size: 20 });
                    return c;
                }) }),
                new TableRow({ children: [cell("\u2460 抓取"), cell("HotTopicFetcher"), cell("从多个平台抓取当日热点话题，筛选高流量、高质量话题，输出TOP 10热点列表")] }),
                new TableRow({ children: [cell("\u2461 写作"), cell("ArticleGenerator"), cell("基于热点话题，用第一人称+娱乐性风格撰写公众号文章（目标AI评分<40）")] }),
                new TableRow({ children: [cell("\u2462 配图"), cell("ImageGenModule"), cell("为每篇文章生成横版1280\u00D7720高清AI配图，中文标题封面图")] }),
                new TableRow({ children: [cell("\u2463 预览"), cell("HTML Preview"), cell("生成微信公众号风格的HTML预览页面，支持长截图导出")] }),
                new TableRow({ children: [cell("\u2464 发布"), cell("WeChatPublisher"), cell("通过微信API将文章一键发布到指定公众号（需AppID/Secret）")] }),
            ]}),

            h1("三、界面需求"),
            h2("3.1 管理仪表盘（首页）"),
            p("用户登录后的主界面，展示系统状态和快捷操作入口。采用深色主题设计。"),

            imgPara("dashboard_screenshot_viewport.png", 480, 310),
            p("[图1] 管理仪表盘界面", { alignment: AlignmentType.CENTER, spacing: { after: 200 } }),

            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [2400, 7326], rows: [
                new TableRow({ children: [cell("UI元素", { width: 2400, fill: "E8EAF6" }), cell("需求说明", { width: 7326, fill: "E8EAF6" }).setChildren([new Paragraph({children:[new TextRun({text:"需求说明",bold:true,size:20})]})])] }),
                new TableRow({ children: [cell("今日已发布"), cell("显示今日发布进度，格式：已完成/目标（如 0/3），下方显示发布时段")] }),
                new TableRow({ children: [cell("成功发布"), cell("累计成功发布的文章数量")] }),
                new TableRow({ children: [cell("微信状态"), cell("显示公众号绑定状态：\u2705 已连接 / \u26A0 未配置（引导去设置页填写AppID）")] }),
                new TableRow({ children: [cell("定时任务"), cell("显示定时任务开关状态、发布时段配置、自动定时发布开关")] }),
                new TableRow({ children: [cell("快捷按钮组"), cell("三个主要操作按钮：\uD83D\uDD25抓取热门话题 / \u270F\uFE0F创建新文章 /\uD83D\uDE80一键生成+发布")] }),
                new TableRow({ children: [cell("最近发布记录"), cell("显示最近N篇发布历史，空态时展示引导文案")] }),
                new TableRow({ children: [cell("底部功能卡片"), cell("四个步骤提示卡片：①抓取热点 ②AI写作 ③配图生成 ④一键发布")] }),
                new TableRow({ children: [cell("顶部导航栏"), cell("五个Tab切换：仪表盘 | 热门话题 | 文章编辑 | 发布管理 | 设置")] }),
            ]}),

            h2("3.2 文章预览页面"),
            p("文章生成完成后的预览界面，模拟微信公众号文章的真实阅读效果。手机端宽度适配（430px）。"),

            imgPara("article_preview_screen.png", 380, 650),
            p("[图2] 文章预览界面（首屏视图）", { alignment: AlignmentType.CENTER, spacing: { after: 200 } }),

            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [2600, 7126], rows: [
                new TableRow({ children: [cell("UI元素", { width: 2600, fill: "E8EAF6" }), cell("需求说明", { width: 7126, fill: "E8EAF6" })] }),
                new TableRow({ children: [cell("头部区域"), cell("深蓝色渐变背景，显示系统名称+\"AI自动生成\"标签（可选隐藏）")] }),
                new TableRow({ children: [cell("文章标题"), cell("大字加粗显示，支持emoji前缀增强吸引力")] }),
                new TableRow({ children: [cell("封面图"), cell("横版1280\u00D7720杂志风格封面图，全中文标题文字")] }),
                new TableRow({ children: [cell("正文内容"), cell("分段排版，每段独立显示；段落间嵌入配图；绿色竖线标注小标题")] }),
                new TableRow({ children: [cell("段落配图"), cell("横版1376\u00D7768（约16:9比例），嵌入段落之间，不喧宾夺主")] }),
                new TableRow({ children: [cell("底部区域"), cell("引导互动文案（\"你怎么看？评论区聊聊\"等口语化结尾）")] }),
            ]}),

            note("重要：预览页面不得暴露任何\"AI生成\"痕迹给读者！禁止显示：生成时间、AI写作标识、工具信息等。"),

            h1("四、功能需求清单"),
            h2("4.1 热点采集模块（R1-R3）"),
            bullet("R1：每日自动抓取TOP 10热点话题，覆盖微博/百度/知乎等多平台", "reqs"),
            bullet("R2：每条话题附带热度指数、来源链接、摘要描述", "reqs"),
            bullet("R3：支持手动触发抓取和定时自动抓取两种模式", "reqs"),

            h2("4.2 AI文章生成模块（R4-R12）"),
            bullet("R4：基于热点话题自动生成1200-2000字公众号风格文章", "reqs"),
            bullet("R5：第一人称叙述视角（\"我\"\"我觉得\"\"说实话\"等口语化表达）", "reqs"),
            bullet("R6：娱乐化/评论化写作风格，避免新闻通稿体", "reqs"),
            bullet("R7：目标AI评分控制在40分以下（人写风格）", "reqs"),
            bullet("R8：法律风险自动检测——政治敏感词阻断、人身权益警告、商业合规提醒", "reqs"),
            bullet("R9：文章结构包含：吸引眼球的标题、分段正文（4-6段）、口语化结尾互动", "reqs"),
            bullet("R10：禁止使用AI套路表达（首先/其次/综上所述/让我们共同期待等）", "reqs"),
            bullet("R11：注入主观态度和个人观点（\"以我的经验来看""最让我意外的是\"）", "reqs"),
            bullet("R12：文末自动添加免责声明（仅供参考，不构成投资建议）", "reqs"),

            h2("4.3 配图生成模块（R13-R19）"),
            bullet("R13：封面图为横版1280\u00D7720像素（16:9比例）", "reqs"),
            bullet("R14：段落配图为横版1376\u00D7768像素（约16:9比例）", "reqs"),
            bullet("R15：所有配图必须包含中文文字标题（面向国内受众）", "reqs"),
            bullet("R16：配图中严禁出现人物、人脸、政治敏感内容", "reqs"),
            bullet("R17：科技风/未来感视觉风格，贴合文章话题内容", "reqs"),
            bullet("R18：图片安全后缀强制追加：no people, no human, no face, safe for work", "reqs"),
            bullet("R19：Pollinations占位图自动检测并重试机制（MD5签名识别）", "reqs"),

            h2("4.4 竞品分析系统（R20-R27）"),
            bullet("R20：每小时自动执行一轮竞品数据采集（08:00-23:00）", "reqs"),
            bullet("R21：每轮采集10个热点 \u00D7 每个热点3篇竞品文章 = 30篇/轮", "reqs"),
            bullet("R22：对每篇文章进行6维度AI评分检测（0-100分）", "reqs"),
            bullet("R23：AI分类标准：<30分人写 / 30-50疑似AI / 50-70很可能AI / >70几乎确定AI", "reqs"),
            bullet("R24：数据持久化存储为JSON文件，按日期归档", "reqs"),
            bullet("R25：补跑模式——每次对话打开自动检测缺失小时段并补齐", "reqs"),
            bullet("R26：可视化简报——热力图、AI分布、账号排行、高低AI文章TOP榜单", "reqs"),
            bullet("R27：重点追踪低AI评分(<40)文章的写作特征，反哺优化自身写作风格", "reqs"),

            h2("4.5 自动化调度模块（R28-R31）"),
            bullet("R28：定时任务支持按小时触发（FREQ=HOURLY;INTERVAL=1）", "reqs"),
            bullet("R29：支持一次性定时任务（scheduleType=once + scheduledAt）", "reqs"),
            bullet("R30：任务有效期控制（validFrom / validUntil参数）", "reqs"),
            bullet("R31：单次执行超时保护（maxDurationMinutes限制）", "reqs"),

            h2("4.6 安全与合规（R32-R36）"),
            bullet("R32：config.yaml（含AppID/Secret）绝不入库Git，已在.gitignore排除", "reqs"),
            bullet("R33：政治敏感词命中直接阻断（台独/法轮功/领导人评价等）", "reqs"),
            bullet("R34：商业推荐类内容必须附加\"不构成投资建议\"免责声明", "reqs"),
            bullet("R35：人身攻击/隐私泄露类表述自动标记警告", "reqs"),
            bullet("R36：所有对外可见内容不得暴露AI工具使用痕迹", "reqs"),

            h1("五、交互体验需求"),
            h2("5.1 可点击元素提亮反馈"),
            p("所有可交互元素在鼠标悬停时必须有明显的视觉反馈，让用户一眼识别出可操作区域："),

            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [2300, 3200, 4226], rows: [
                new TableRow({ children: [
                    cell("元素类型", { width: 2300, fill: "E8EAF6" }),
                    cell("悬停效果", { width: 3200, fill: "E8EAF6" }),
                    cell("视觉变化", { width: 4226, fill: "E8EAF6" })
                ]}),
                new TableRow({ children: [cell("概览卡片(stat-card)"), cell("上浮+放大1.03倍"), cell("蓝色阴影光晕+亮度提升+pointer手型")] }),
                new TableRow({ children: [cell("时间标签(hour-tag)"), cell("上浮+发光边框"), cell("对应颜色发光+阴影扩散+z-index提升")] }),
                new TableRow({ children: [cell("热点列表项(topic-item)"), cell("右滑4px+蓝条指示器"), cell("蓝色阴影+浅蓝底色背景")] }),
                new TableRow({ children: [cell("表格行(table-row)"), cell("微缩放"), cell("黄色阴影光晕突出行")] }),
                new TableRow({ children: [cell("评分标签(score-badge)"), cell("放大1.1倍"), cell("同色系加深背景+彩色投影")] }),
                new TableRow({ children: [cell("AI进度条(ai-bar-fill)"), cell("纵向放大1.15倍"), filter("亮度提升+阴影")]),
                new TableRow({ children: [cell("发现框(finding-box)"), cell("右滑4px"), cell("左边框加粗+阴影光晕")] }),
                new TableRow({ children: [cell("头部区域(header)"), cell("-"), cell("蓝色阴影扩散加深")] }),
            ]}),

            h2("5.2 简报可视化交互"),
            p("竞品分析全景简报页面包含以下交互能力："),

            bullet("时段热力图：鼠标悬浮显示该小时的具体数据（轮次/文章数/平均AI分）", "ui-nums"),
            bullet("账号排行表：点击可展开该账号的所有文章详情", "ui-nums"),
            bullet("AI分布柱状图：悬浮显示各区间的具体文章数和占比", "ui-nums"),
            bullet("高/低AI文章列表：点击可查看全文和详细评分报告", "ui-nums"),
            bullet("全局过渡动画：所有元素状态变化都有0.2s平滑过渡", "ui-nums"),

            new PageBreak(),

            h1("六、数据规格"),
            h2("6.1 竞品分析数据规模（截至2026-04-13）"),

            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [3000, 3300, 3426], rows: [
                new TableRow({ children: [cell("指标", { width: 3000, fill: "E8EAF6" }), cell("数值", { width: 3300, fill: "E8EAF6" }), cell("说明", { width: 3426, fill: "E8EAF6" })] }),
                new TableRow({ children: [cell("总采集轮次"), cell("59 轮"), cell("覆盖04-11至04-13共3天")] }),
                new TableRow({ children: [cell("总文章数"), cell("1,695 篇"), cell("每轮10热点\u00D73竞品=30篇")] }),
                new TableRow({ children: [cell("监控账号数"), cell("30+ 个"), cell("涵盖各领域头部公众号")] }),
                new TableRow({ children: [cell("平均AI评分"), cell("46.3 分"), cell("中等偏人写水平")] }),
                new TableRow({ children: [cell("人写风格(<40)"), cell("478篇 (28.2%)"), cell("\u2705 学习模仿对象")] }),
                new TableRow({ children: [cell("确认AI(>70)"), cell("267篇 (15.8%)"), cell("\u26A0 反面教材避坑")] }),
                new TableRow({ children: [cell("模糊地带(40-70)"), cell("950篇 (56.0%)", {width:3300}), cell("\uD83C\uDFAF 我们的目标区间")] }),
            ]}),

            h2("6.2 时段覆盖率"),
            p("04-13当天实现了全天候24时段全覆盖（00:00-23:00），无任何缺口。自动化补跑模式运行稳定。"),

            h1("七、商业化规划"),
            h2("7.1 收入预期（基于行业数据分析）"),

            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [1800, 2100, 2100, 2100, 1626], rows: [
                new TableRow({ children: [
                    cell("阶段", { width: 1800, fill: "1A237E" }),
                    cell("日收入预估", { width: 2100, fill: "1A237E" }),
                    cell("月收入预估", { width: 2100, fill: "1A237E" }),
                    cell("关键条件", { width: 2100, fill: "1A237E" }),
                    cell("周期", { width: 1626, fill: "1A237E" })
                ].map(c => {
                    const r = c.children[0].children[0];
                    if(r.children && r.children.length)r.children[0]=new TextRun({text:r.children[0].text||"",bold:true,color:"#FFF",size:18})
                    return c;
                }) }),
                new TableRow({ children: [cell("起步期"), cell("\uFFE515-\uFF50/天"), cell("\uFFE5360-\uFFE51,440/月"), cell("新号纯流量主"), cell("1-2月")] }),
                new TableRow({ children: [cell("成长期"), cell("\uFFE5135-\uFFE5360/天"), cell("\uFFE54,050-\uFFE510,800/月"), cell("有粉丝基础+原创"), cell("3-6月")] }),
                new TableRow({ children: [cell("成熟期"), cell("\uFFE5600-\uFFE53,000+/天"), cell("\uFFE518,000-\uFFE590,000/月"), cell("爆款+品牌广告"), cell("6月+")] }),
            ]}),

            h2("7.2 矩阵账号策略"),
            p("根据2025年3月最新规则，注册限制如下："),

            new Table({ width: { size: 9726, type: WidthType.DXA }, columnWidths: [2800, 2200, 4726], rows: [
                new TableRow({ children: [cell("主体类型", { width: 2800, fill: "E8EAF6" }), cell("可注册数量", { width: 2200, fill: "E8EAF6" }), cell("建议方案", { width: 4726, fill: "E8EAF6" })] }),
                new TableRow({ children: [cell("个人（身份证）"), cell("仅1个"), cell("作为主号，先跑通变现流程")] }),
                new TableRow({ children: [cell("企业/公司"), cell("仅2个"), cell("可申请提额到5-10个")] }),
                new TableRow({ children: [cell("个体工商户"), cell("仅2个"), cell("性价比最高，注册简单+可提额")] }),
                new TableRow({ children: [cell("推荐组合"), cell("6个号"), cell("1个人号 + 1个体户(5个号)，分不同垂直领域")] }),
            ]}),

            note("建议路径：先用1个号跑通全流程验证变现能力（目标月入3000+），再考虑矩阵扩量。"),

            new Paragraph({ spacing: { before: 600, after: 200 } }),
            new Paragraph({ alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "\u2014\u2014 文档结束 \u2014\u2014", size: 20, color: "999999" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100 },
                children: [new TextRun({ text: "最后更新：2026年4月13日 20:19", size: 18, color: "AAAAAA" })] }),
        ]
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('c:/Users/v_junshshi/WorkBuddy/Claw/output/PRD_微信公众号爆款内容发布系统.docx', buffer);
    console.log('DOCX created OK');
}).catch(e => console.error('ERROR:', e.message));
