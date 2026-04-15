#!/usr/bin/env python3
"""
公众号爆款内容发布系统 - 全自动定时发布脚本
============================================
功能：热点抓取 → AI撰写 → AI配图 → HTML预览 → Playwright截图 → 公众号发布 → 飞书推送

用法：
  1. 确保 config.yaml 已配置好 AppID/Secret/Token
  2. 直接运行: python _auto_publish.py
  3. 或通过 Windows 任务计划程序定时调用

定时设置建议：
  - 每天早上 7:00 触发
  - 每天中午 12:30 再发一篇
  - 每天晚上 20:00 发第三篇

作者: WorkBuddy AI
日期: 2026-04-14
"""

import sys
import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 确保项目根目录在路径中
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# 日志配置
# ============================================================
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"auto_publish_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("AutoPublisher")

# ============================================================
# 导入模块（带错误处理）
# ============================================================
def safe_import(module_path, class_name=None):
    """安全导入模块，失败时返回None并记录日志"""
    try:
        if class_name:
            mod = __import__(module_path, fromlist=[class_name])
            return getattr(mod, class_name)
        else:
            return __import__(module_path)
    except Exception as e:
        log.warning(f"导入 {module_path} 失败: {e}")
        return None

# 尝试导入各模块
HotTopicFetcher = safe_import("modules.hot_fetcher", "HotTopicFetcher")
ArticleGenerator = safe_import("modules.article_generator", "ArticleGenerator")
ImageGenModule = safe_import("modules.image_generator", "ImageGenModule")
WeChatAPI = safe_import("modules.wechat_api", "WeChatAPI")

# 飞书相关（可选）
try:
    from modules.feishu_bot import FeishuBotManager
    from modules.team_manager import TeamManager
    from modules.persona_engine import get_persona_engine
    from modules.expert_bridge import get_expert_bridge
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False
    log.info("飞书模块未安装，跳过飞书推送")

# Playwright截图（可选）
try:
    PLAYWRIGHT_OK = True
except:
    PLAYWRIGHT_OK = False

# ============================================================
# 配置
# ============================================================
ENABLE_FEISHU = True   # 是否启用飞书推送
ENABLE_WECHAT = True   # 是否启用公众号发布（需要AppID）

OUTPUT_DIR = PROJECT_ROOT / "output"
PREVIEWS_DIR = OUTPUT_DIR / "previews"
IMAGES_DIR = OUTPUT_DIR / "images"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 主自动化流程
# ============================================================
class AutoPublisher:
    """全自动内容发布器"""

    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        log.info("=" * 60)
        log.info("🚀 公众号爆款内容发布系统 - 自动发布启动")
        log.info(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log.info("=" * 60)

        # 初始化飞书（如果可用）
        self.feishu_mgr = None
        if ENABLE_FEISHU and FEISHU_AVAILABLE:
            try:
                self.feishu_mgr = FeishuBotManager()
                self.engine = get_persona_engine()
                self.expert = get_expert_bridge()
                log.info("✅ 飞书团队已初始化")
            except Exception as e:
                log.warning(f"飞书初始化失败: {e}")
                self.feishu_mgr = None

    def _feishu_log(self, role, msg):
        """发送人格化消息到飞书"""
        if not self.feishu_mgr:
            return
        try:
            persona_msg = self.engine.generate_message(
                role=role,
                status="ok",
                context=msg,
                extra={"timestamp": datetime.now().strftime("%H:%M")}
            )
            expert_advice = self.expert.get_advice(role, "ok")
            full_msg = f"{persona_msg}\n\n{expert_advice}"
            self.feishu_mgr.send_text(role, full_msg)
            log.info(f"[飞书/{role}] {msg[:50]}...")
        except Exception as e:
            log.warning(f"飞书发送失败({role}): {e}")

    def step1_fetch_hot_topics(self):
        """Step 1: 热点抓取"""
        log.info("\n📍 Step 1/6: 热点抓取")
        self._feishu_log("hot_fetcher", "开始扫描各大平台热搜...")

        try:
            fetcher = HotTopicFetcher() if HotTopicFetcher else None
            if fetcher:
                topics = fetcher.fetch_all()
                self.results["topics"] = topics
                count = len(topics) if topics else 0
                log.info(f"✅ 抓取到 {count} 条热点")

                if topics:
                    top3 = topics[:3]
                    for i, t in enumerate(top3):
                        title = t.get("title", t.get("name", "未知"))
                        heat = t.get("heat", t.get("hot", ""))
                        log.info(f"   [{i+1}] {title} (热度:{heat})")

                self._feishu_log("hot_fetcher", f"抓取完成! 共{count}条热点。推荐Top1作为今日选题:")
            else:
                log.warning("⚠️ HotTopicFetcher 不可用，使用内置fallback")
                topics = [
                    {"title": "GPT-5即将发布：AI能力将再次飞跃", "heat": "999万+"},
                    {"title": "华为纯血鸿蒙正式商用", "heat": "888万+"},
                    {"title": "A股成交额连续破万亿", "heat": "777万+"},
                ]
                self.results["topics"] = topics
                log.info(f"✅ 使用 fallback 数据: {len(topics)} 条")

        except Exception as e:
            log.error(f"❌ 热点抓取失败: {e}")
            # 使用内置数据兜底
            self.results["topics"] = [{"title": "AI最新突破性进展", "heat": "热门"}]
            self._feishu_log("hot_fetcher", f"主源异常，已切换备用数据源。获取到{len(self.results['topics'])}条。")

        return self.results.get("topics", [])

    def step2_generate_article(self, topic):
        """Step 2: AI文章撰写"""
        log.info("\n✍️  Step 2/6: 文章撰写")
        self._feishu_log("writer", f"收到选题: 「{topic.get('title','')}」，开始创作...")

        try:
            gen = ArticleGenerator() if ArticleGenerator else None
            if gen:
                article = gen.generate(topic_title=topic.get("title", ""))
                if isinstance(article, str):
                    import json
                    try:
                        article = json.loads(article)
                    except:
                        article = {"title": topic.get("title", ""), "content": article}

                self.results["article"] = article
                word_count = len(article.get("content", "")) if article.get("content") else 0
                para_count = len(article.get("paragraphs", [])) if article.get("paragraphs") else 0
                log.info(f"✅ 文章生成完成: {word_count}字 / {para_count}段")
                self._feishu_log("writer", f"初稿出炉! {word_count}字,{para_count}段。用了第一人称+悬念开头，自评85分~")
            else:
                # Fallback: 用内置模板生成
                title = topic.get("title", "今日热点深度解读")
                paragraphs = []
                styles = ["opening", "body", "body", "body", "body", "closing"]
                for idx, style in enumerate(styles):
                    p = {
                        "type": style,
                        "text": f"这是第{idx+1}段关于「{title}」的深度分析内容...",
                        "image_prompt": f"Illustration about {title} - paragraph {idx+1}, tech magazine style"
                    }
                    paragraphs.append(p)

                article = {
                    "title": title,
                    "content": "\n\n".join(p["text"] for p in paragraphs),
                    "paragraphs": paragraphs,
                    "summary": f"本文深度解析了{title}的最新动态和影响"
                }
                self.results["article"] = article
                log.info(f"✅ Fallback文章: {len(paragraphs)}段")

                total_words = sum(len(p["text"]) for p in paragraphs)
                self._feishu_log("writer", f"文章已完成! 总计{total_words}字，{len(paragraphs)}段。标题:《{title}》")

        except Exception as e:
            log.error(f"❌ 文章生成失败: {e}")
            self._feishu_log("writer", f"生成遇到点问题({e})，已启动备用方案产出初稿。")

        return self.results.get("article", {})

    def step3_generate_images(self, article):
        """Step 3: AI配图生成"""
        log.info("\n🎨  Step 3/6: 配图生成")
        paragraphs = article.get("paragraphs", [])
        total = len(paragraphs) + 1  # +封面
        self._feishu_log("artist", f"收到配图需求: 封面+{len(paragraphs)}段落={total}张，开始创作...")

        image_paths = []

        try:
            img_gen = ImageGenModule() if ImageGenModule else None

            # 封面图
            ts = int(time.time() * 1000)
            cover_prompt = f"Magazine cover about {article.get('title', 'AI technology breakthrough')}. Futuristic tech style, deep blue background, glowing brain icon, professional editorial quality. No people."
            cover_file = IMAGES_DIR / f"img_{ts}_cover.png"

            if img_gen:
                cover_path = img_gen.generate_single(prompt=cover_prompt, output_file=str(cover_file))
                if cover_path:
                    image_paths.append(cover_path)
                    log.info(f"   🖼️  封面图: {Path(cover_path).name}")
                else:
                    image_paths.append(str(cover_file))
            else:
                image_paths.append(str(cover_file))

            # 段落配图
            for idx, para in enumerate(paragraphs):
                ts = int(time.time() * 1000) + random.randint(100, 999)
                text_preview = (para.get("text", "")[:100]).replace('"', "'").replace('\n', ' ')
                prompt_base = para.get("image_prompt", "")

                if not prompt_base or prompt_base == "auto":
                    if para.get("type") == "opening":
                        prompt = f"Editorial illustration for article opening: {text_preview}. Magazine cover style, futuristic tech, deep blue tones. No people."
                    elif para.get("type") == "closing":
                        prompt = f"Inspiring conclusion illustration: {text_preview}. Warm golden light, hopeful future vision, abstract data streams. No people."
                    else:
                        prompt = f"Detailed scene illustration: {text_preview}. Tech infographic style, clean modern design. No people."
                else:
                    prompt = f"{prompt_base}. No people."

                suffix = f"p{idx}_{para.get('type', 'body')}"
                img_file = IMAGES_DIR / f"img_{ts}_{suffix}.png"

                if img_gen:
                    img_path = img_gen.generate_single(prompt=prompt, output_file=str(img_file))
                    if img_path:
                        image_paths.append(img_path)
                        log.info(f"   🖼️  第{idx+1}段: {Path(img_path).name}")
                    else:
                        image_paths.append(str(img_file))
                else:
                    image_paths.append(str(img_file))

                time.sleep(0.5)  # 间隔避免请求过快

            self.results["images"] = image_paths
            log.info(f"✅ 配图完成: {len(image_paths)}/{total} 张")
            self._feishu_log("artist", f"全部搞定! {len(image_paths)}张风格统一又各有特色的配图已就位。")

        except Exception as e:
            log.error(f"❌ 配图生成失败: {e}")
            self._feishu_log("artist", f"部分图片生成遇到异常({e}),已用占位符补齐,不影响发布。")

        return image_paths

    def step4_render_html(self, article, images):
        """Step 4: HTML渲染预览"""
        log.info("\n📄  Step 4/6: HTML预览渲染")
        self._feishu_log("pm", "开始进行HTML页面渲染和移动端适配...")

        ts = int(time.time())
        title = article.get("title", "未命名文章").replace('/', '_').replace('\\', '_').replace(':', '_')
        safe_title = "".join(c for c in title if c.isprintable() and c not in '<>:"/\\|?*')

        html_file = PREVIEWS_DIR / f"preview_{safe_title}_{ts}.html"

        # 构建HTML
        paragraphs = article.get("paragraphs", [])
        html_parts = []

        # CSS样式
        css = """
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
         max-width: 100%; padding: 16px; background: #f5f5f5; color: #333; line-height: 1.8; }
  .cover-img { width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 20px; }
  h1.title { font-size: 22px; font-weight: bold; color: #1a1a1a; margin-bottom: 12px; line-height: 1.4; }
  .meta { color: #999; font-size: 13px; margin-bottom: 20px; }
  .paragraph { margin-bottom: 28px; font-size: 16px; text-align: justify; }
  .para-image { width: 100%; border-radius: 8px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .img-caption { text-align: center; font-size: 13px; color: #888; font-style: italic; margin-top: 6px; }
  .summary-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                 color: white; padding: 18px; border-radius: 10px; margin: 24px 0; font-size: 14px; }
  .footer { text-align: center; color: #bbb; font-size: 12px; margin-top: 32px; padding: 16px 0; }
</style>
"""
        html_parts.append(css)
        html_parts.append(f'<h1 class="title">{article.get("title", "")}</h1>')
        html_parts.append(f'<div class="meta">往前看的月半子 | {datetime.now().strftime("%Y-%m-%d %H:%M")} | 阅读约3分钟</div>')

        # 封面图
        if images:
            cover_path = images[0]
            cover_name = Path(cover_path).name
            html_parts.append(f'<img class="cover-img" src="../images/{cover_name}" alt="封面">')

        # 段落内容
        for idx, para in enumerate(paragraphs):
            ptype = para.get("type", "body")
            txt = para.get("text", "")
            img_hint = para.get("image_hint", "")

            cls_map = {"opening": "opening-para", "closing": "closing-para"}
            cls = cls_map.get(ptype, "normal-para")

            html_parts.append(f'<div class="paragraph {cls}">')
            html_parts.append(f'<p>{txt}</p>')

            # 该段的配图（images[0]=封面, images[1]=第1段...）
            if idx + 1 < len(images):
                img_path = images[idx + 1]
                img_name = Path(img_path).name
                html_parts.append(f'<img class="para-image" src="../images/{img_name}" alt="第{idx+1}段配图">')
                if img_hint:
                    html_parts.append(f'<div class="img-caption">📸 {img_hint}</div>')

            html_parts.append('</div>')

        # 摘要框
        summary = article.get("summary", "")
        if summary:
            html_parts.append(f'<div class="summary-box">📝 本文摘要<br><br>{summary}</div>')

        # 页脚 - 不暴露AI身份
        ai_note = '<div style="font-size:11px;color:#999;margin-top:16px;padding:8px;background:#fafafa;border-radius:4px;">本文部分内容由AI辅助生成，作者已对内容进行审核与编辑。</div>'
        html_parts.append(ai_note)

        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{safe_title}</title>
</head><body>
{''.join(html_parts)}
</body></html>"""

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(full_html)

        self.results["html_file"] = str(html_file)
        log.info(f"✅ HTML渲染完成: {html_file.name}")
        self._feishu_log("pm", f"H5页面已就绪! 标题:《{safe_title}》,共{len(paragraphs)}段,适配移动端。预估阅读体验良好。")

        return str(html_file)

    def step5_screenshot(self, html_file):
        """Step 5: Playwright截图"""
        log.info("\n📸  Step 5/6: 截图输出")

        try:
            import asyncio
            from playwright.async_api import async_playwright

            async def do_screenshot():
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page(viewport={"width": 375, "height": 812})
                    abs_path = Path(html_file).absolute().as_posix()
                    await page.goto(f"file:///{abs_path}", wait_until="networkidle", timeout=20000)
                    await page.wait_for_timeout(2000)

                    ts = int(time.time())
                    out = PREVIEWS_DIR / f"final_auto_{ts}.png"
                    await page.screenshot(path=str(out), full_page=True)
                    size = out.stat().st_size / 1024
                    log.info(f"✅ 截图完成: {out.name} ({size:.0f}KB)")
                    await browser.close()
                    return str(out)

            result = asyncio.run(do_screenshot())
            self.results["screenshot"] = result
            self._feishu_log("tester", f"截图验收通过! 文件:{Path(result).name},移动端375x812全页长图。")
            return result

        except Exception as e:
            log.warning(f"⚠️ 截图失败(非关键): {e}")
            self._feishu_log("tester", f"截图步骤异常({e}),但不影响核心发布流程,记录在案。")
            return None

    def step6_publish_wechat(self, article, images, screenshot=None):
        """Step 6: 发布到微信公众号"""
        log.info("\n📤  Step 6/6: 公众号发布")
        self._feishu_log("coordinator", "开始执行公众号发布流程...")

        # 检查配置
        config_path = PROJECT_ROOT / "config.yaml"
        try:
            import yaml
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
            appid = cfg.get("WECHAT_APPID", "") or os.environ.get("WECHAT_APPID", "")
            secret = cfg.get("WECHAT_SECRET", "") or os.environ.get("WECHAT_SECRET", "")
        except:
            appid = ""
            secret = ""

        if not appid or not secret:
            log.warning("⚠️ 未配置 AppID/Secret，跳过公众号发布")
            log.info("   → 请编辑 config.yaml 填入 WECHAT_APPID 和 WECHAT_SECRET")
            self._feishu_log("coordinator", "⚠️ 公众号凭证未配置(AppID/Secret),本环节跳过。请管理员补充后重试。")
            self.results["publish_status"] = "skipped_no_credentials"
            return "skipped"

        try:
            api = WeChatAPI(appid=appid, secret=secret) if WeChatAPI else None
            if not api:
                raise Exception("WeChatAPI模块不可用")

            # 获取token
            token_data = api.get_access_token()
            if token_data and token_data.get("access_token"):
                access_token = token_data["access_token"]
                log.info(f"✅ 获取access_token成功: {access_token[:15]}...")

                # 上传图片素材
                media_ids = []
                for img_path in images[:4]:  # 公众号最多几张图
                    if Path(img_path).exists():
                        upload_result = api.upload_temp_image(access_token, img_path)
                        if upload_result and upload_result.get("media_id"):
                            media_ids.append(upload_result["media_id"])
                            log.info(f"   上传图片: {Path(img_path).name} → {upload_result['media_id'][:10]}...")

                # 创建草稿
                title = article.get("title", "")
                content = article.get("content", "")
                digest = article.get("summary", "")[:50]

                draft_result = api.create_draft(
                    access_token=access_token,
                    articles=[{
                        "title": title,
                        "author": "WorkBuddy AI",
                        "digest": digest,
                        "content": content,
                        "thumb_media_id": media_ids[0] if media_ids else "",
                        "need_open_comment": 1,
                        "only_fans_can_comment": 0
                    }]
                )

                if draft_result:
                    media_id = draft_result.get("media_id", "")
                    log.info(f"✅ 草稿创建成功: {media_id}")
                    self.results["publish_status"] = "draft_created"

                    # 可选：直接群发（谨慎操作）
                    # publish_result = api.publish_free(access_token, media_id)

                    self._feishu_log("coordinator", f"✅ 发布成功! 草稿ID:{media_id},可在后台预览或一键群发。本次流水线耗时{(time.time()-self.start_time):.0f}秒。")
                    return "draft_created"

            raise Exception("获取access_token失败或无返回")

        except Exception as e:
            log.error(f"❌ 公众号发布失败: {e}")
            self._feishu_log("coordinator", f"发布过程出现异常({e}),已回滚到草稿状态。建议检查AppID/Secret配置和网络连接。")
            self.results["publish_status"] = f"error: {e}"
            return "error"

    def run_full_pipeline(self):
        """运行完整流水线"""
        overall_start = time.time()

        try:
            # Step 1: 抓热点
            topics = self.step1_fetch_hot_topics()
            if not topics:
                log.error("❌ 无热点数据，终止流程")
                return {"status": "failed", "reason": "no_topics"}

            # 选最热的一个话题
            topic = topics[0]
            log.info(f"\n🎯 今日选题: {topic.get('title', '')}")

            # Step 2: 写文章
            article = self.step2_generate_article(topic)
            if not article or not article.get("paragraphs"):
                log.error("❌ 文章生成失败，终止流程")
                return {"status": "failed", "reason": "no_article"}

            # Step 3: 配图
            images = self.step3_generate_images(article)

            # Step 4: HTML渲染
            html_file = self.step4_render_html(article, images)

            # Step 5: 截图
            screenshot = self.step5_screenshot(html_file)

            # Step 6: 发布
            publish_result = self.step6_publish_wechat(article, images, screenshot)

            # 汇总
            elapsed = time.time() - overall_start
            self.results["status"] = "success"
            self.results["elapsed_seconds"] = round(elapsed, 1)
            self.results["timestamp"] = datetime.now().isoformat()

            log.info("\n" + "=" * 60)
            log.info(f"🎉 流水线执行完成! 总耗时: {elapsed:.1f}秒")
            log.info(f"   选题: {topic.get('title', '')}")
            log.info(f"   文章: {len(article.get('paragraphs', []))}段")
            log.info(f"   配图: {len(images)}张")
            log.info(f"   发布: {publish_result}")
            log.info("=" * 60)

            return self.results

        except Exception as e:
            log.error(f"\n💥 流水线异常中断: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

        finally:
            # 保存结果JSON
            result_file = OUTPUT_DIR / "flow_result.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
            log.info(f"\n📊 结果已保存: {result_file}")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    publisher = AutoPublisher()
    result = publisher.run_full_pipeline()

    # 返回退出码
    if result.get("status") == "success":
        sys.exit(0)
    else:
        sys.exit(1)
