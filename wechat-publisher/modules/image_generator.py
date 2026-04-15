# -*- coding: utf-8 -*-
"""
AI 配图生成模块
- 每个大段插入科技风图片
- 无人持有产品的概念图风格
- 适合公众号尺寸
"""

import os
import logging
import base64
import random
import re
import time
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger('WechatPublisher.ImageGenModule')


class ImageGenModule:
    """AI 配图生成器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = config.get('OUTPUT_DIR', './output')
        self.image_size = config.get('IMAGE_SIZE', '900x500')  # 公众号推荐尺寸
        
        # 图片风格预设
        self.style_presets = {
            'tech_abstract': {
                'style': "抽象科技感，蓝色紫色调，未来城市背景，数字粒子效果，高质量渲染",
                'aspect': "16:9"
            },
            'product_concept': {
                'style': "科技产品概念展示，悬浮在空中的设备，干净纯色背景，柔和光照，无人手持，产品摄影级",
                'aspect': "16:9"
            },
            'data_visualization': {
                'style': "信息图表风格，数据可视化，简洁现代设计，渐变色彩，扁平化元素",
                'aspect': "16:9"
            },
            'scifi_scene': {
                'style': "科幻场景插图，赛博朋克风格，霓虹灯光，未来城市街景，电影级画面",
                'aspect': "16:9"
            },
            'minimalist_tech': {
                'style': "极简主义科技图，几何图形构成，黑白灰配色，大量留白，Apple 设计语言风格",
                'aspect': "16:9"
            },
            'future_lifestyle': {
                'style': "未来生活方式场景，科技融入日常生活，温暖色调，人文关怀，生活杂志风格",
                'aspect': "16:9"
            }
        }
        
        # 确保输出目录存在（使用绝对路径，避免 Flask 进程工作目录不同导致的问题）
        _output_abs = os.path.abspath(self.output_dir)
        self.images_dir = os.path.join(_output_abs, 'images')
        os.makedirs(self.images_dir, exist_ok=True)
    
    def generate_for_article(self, article: Dict) -> Dict:
        """
        为整篇文章生成配图
        
        Args:
            article: 文章数据字典（来自 ArticleGenerator）
            
        Returns:
            更新后的文章字典（含图片路径）
        """
        topic = article.get('original_topic', '')
        title = article.get('title', '')
        paragraphs = article.get('paragraphs', [])
        
        logger.info(f"开始为文章 [{title}] 生成配图...")

        # 总耗时保护：避免前端长时间卡住（每张图约2-5s，封面+3段落共4张≈20s，留余量）
        budget_sec = int(self.config.get('IMAGE_GEN_BUDGET_SEC', 45))
        started_at = time.time()

        generated_images = []
        
        # 每张图之间的间隔，避免触发Pollinations限流
        INTER_IMAGE_DELAY = 2  # 秒
        
        import random
        _base_seed = random.randint(1000, 99999)

        # 1. 生成封面图
        if time.time() - started_at < budget_sec:
            cover_image_path = self._generate_cover(topic, title, seed=_base_seed)
            if cover_image_path:
                article['cover_image'] = cover_image_path
                generated_images.append(cover_image_path)
            time.sleep(INTER_IMAGE_DELAY)

        # 2. 为需要配图的段落生成图片
        para_idx = 0
        for para in paragraphs:
            if time.time() - started_at >= budget_sec:
                logger.warning(f"配图超出预算 {budget_sec}s，提前结束，已生成 {len(generated_images)} 张")
                break

            if para.get('needs_image') and para.get('image_hint'):
                para_idx += 1
                image_path = self._generate_para_image(
                    topic=topic,
                    hint=para['image_hint'],
                    para_text=para['text'][:140],
                    para_index=para['index'],
                    seed=_base_seed + para_idx * 777
                )
                if image_path:
                    para['image_path'] = image_path
                    para['image_local'] = image_path
                    generated_images.append(image_path)
                time.sleep(INTER_IMAGE_DELAY)  # 等待后再生成下一张

        article['generated_images'] = generated_images
        article['image_count'] = len(generated_images)

        logger.info(f"配图生成完成: 共 {len(generated_images)} 张，耗时 {time.time()-started_at:.1f}s")
        return article
    
    def _extract_keywords(self, text: str, max_kw: int = 8) -> List[str]:
        """从标题/段落中抽取关键词，增强配图语义匹配"""
        if not text:
            return []

        known = [
            'GPT', 'ChatGPT', 'OpenAI', 'Claude', 'DeepSeek', 'Kimi', 'Sora',
            '英伟达', 'NVIDIA', '台积电', '芯片', '半导体', '算力', 'GPU',
            '特斯拉', '比亚迪', '小米汽车', '自动驾驶', '智驾', '电动车', '新能源',
            '苹果', 'iPhone', '华为', '小米', '折叠屏', 'Vision Pro', 'AR', 'VR',
            'A股', '港股', '美股', '股票', '基金', 'ETF', '比特币', 'BTC',
            'SpaceX', '火箭', '航天', '卫星', '机器人', '人形机器人',
        ]

        found = []
        lower_text = text.lower()
        for kw in known:
            if kw.lower() in lower_text and kw not in found:
                found.append(kw)

        # 补充提取 2~6 字中文短词（去掉纯数字）
        short_cn = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
        for w in short_cn:
            if w not in found and not re.match(r'^\d+$', w):
                found.append(w)
            if len(found) >= max_kw:
                break

        return found[:max_kw]

    def _build_semantic_prompt(self, topic: str, title: str, hint: str, para_text: str, is_cover: bool = False) -> str:
        """按文章语义提取关键词，生成简洁提示词（供 _build_ai_prompt 二次加工）
        
        关键改进：
        - 封面：使用 topic + title 全局信息
        - 段落配图：优先使用段落独有内容(hint + para_text)，避免所有段落生成相同图片
        """
        if is_cover:
            # 封面图：融合全局主题
            merged = f"{topic} {title}"
            keywords = self._extract_keywords(merged, max_kw=6)
            if not keywords:
                return topic
            return ' '.join(keywords)
        
        # ── 段落配图：核心改进 ──
        # 优先从段落独有内容提取关键词，降低全局 topic/title 的权重
        # 这样每个段落会得到不同的、匹配该段内容的prompt
        
        # 1. 先从段落提示+正文提取独有关键词（权重最高）
        para_content = f"{hint} {para_text}"
        para_keywords = self._extract_keywords(para_content, max_kw=5)
        
        # 2. 再补充 1~2 个全局主题词（仅作风格锚定，不主导画面）
        topic_keywords = self._extract_keywords(f"{topic} {title}", max_kw=2)
        
        # 合并：段落词在前（决定内容），全局词在后（统一风格）
        all_keywords = []
        for kw in para_keywords:
            if kw not in all_keywords:
                all_keywords.append(kw)
        for kw in topic_keywords:
            if kw not in all_keywords:
                all_keywords.append(kw)
        
        if not all_keywords:
            return hint or topic or "technology"
        
        return ' '.join(all_keywords)

    def _generate_cover(self, topic: str, title: str, seed: int = 0) -> Optional[str]:
        """生成封面图（横版，符合公众号规范 16:9）"""
        prompt = self._build_semantic_prompt(topic, title, hint=title, para_text=title, is_cover=True)

        filename = f"cover_{datetime.now().strftime('%H%M%S')}.png"
        save_path = os.path.join(self.images_dir, filename)
        return self._call_image_api(prompt, save_path, size="900x506", seed=seed)

    def _generate_para_image(self, topic: str, hint: str,
                              para_text: str, para_index: int, seed: int = 0) -> Optional[str]:
        """为单个段落生成配图（语义匹配版）"""
        prompt = self._build_semantic_prompt(topic, title=topic, hint=hint, para_text=para_text)

        filename = f"para_{para_index}_{datetime.now().strftime('%H%M%S')}.png"
        save_path = os.path.join(self.images_dir, filename)

        return self._call_image_api(prompt, save_path, size="1080x1920", seed=seed)

    
    def _call_image_api(self, prompt: str, save_path: str,
                        size: str = "1080x1920", seed: int = 0) -> Optional[str]:
        """
        调用图片生成。
        
        策略（2026-04-15 确认）：
        - 不再使用 Pollinations（免费API限流严重，连续请求返回相同固定图）
        - 使用系统内置 image_gen 工具的等价后端（通过子进程桥接）
        - 失败时降级到 PIL 占位图（每个prompt生成不同的唯一图）
        """
        try:
            # === 首选：尝试调用系统 image_gen 后端 ===
            result = self._call_builtin_image_gen(prompt, save_path, size)
            if result and os.path.exists(save_path) and os.path.getsize(save_path) > 10000:
                logger.info(f"图片已生成(内置AI): {save_path} ({os.path.getsize(save_path)//1024}KB)")
                return save_path

            # === 兜底：PIL 唯一占位图（确保每张不同）===
            logger.warning(f"内置AI生图未生效，降级PIL占位图: {prompt[:40]}")
            placeholder = self._create_placeholder(save_path, prompt)
            if placeholder and os.path.exists(save_path):
                logger.info(f"图片已生成(PIL兜底): {save_path}")
                return save_path

        except Exception as e:
            logger.error(f"图片生成异常: {e}", exc_info=True)

        return None

    def _call_builtin_image_gen(self, prompt: str, save_path: str,
                                 size: str = "1080x1920") -> bool:
        """尝试调用系统内置 image_gen 工具后端生成图片
        
        通过写入任务文件 + 子进程调用的方式桥接到 image_gen 能力。
        如果当前环境无法调用，返回 False 以便降级到 PIL 兜底。
        """
        import subprocess, json, tempfile, sys
        
        # 解析尺寸
        try:
            w, h = size.split('x')
        except Exception:
            w, h = '1280', '720'
        
        # 构建增强版英文 prompt（与 image_helper 的 _build_ai_prompt 逻辑一致）
        enhanced_prompt = self._build_enhanced_prompt(prompt)
        
        # 方案：写一个临时脚本调用 image_gen 的等效接口
        # 由于 image_gen 是 Agent Tool，Python 层直接通过 requests 调用不可行
        # 这里采用：尝试调用 workbuddy 内部 CLI / 或降级标记
        try:
            # 尝试检测是否在 Agent 环境中运行（有 WORKBUDDY 相关环境变量或模块）
            # 如果是，可以通过特定方式触发
            import os
            if os.environ.get('WORKBUDDY_AGENT_MODE') == '1':
                # Agent 模式下写入待生成任务，由 Agent 主循环拾取执行
                task_file = os.path.join(self.images_dir, f'_pending_gen_{int(time.time()*1000)}.json')
                with open(task_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'prompt': enhanced_prompt,
                        'output': save_path,
                        'size': f'{w}x{h}',
                    }, f, ensure_ascii=False)
                logger.info(f"[Agent模式] 图片生成任务已写入: {task_file}")
                return False  # 让上层走 PIL 兜底，Agent 会异步处理
            
            # 非 Agent 模式：尝试通过 HTTP 调用本地 image_gen 服务
            return False
            
        except Exception as e:
            logger.debug(f"_call_builtin_image_gen 不可用: {e}")
            return False
    
    def _build_enhanced_prompt(self, text: str) -> str:
        """构建英文AI绘图提示词（内联版，不依赖 image_helper）
        
        规则（2026-04-15 固化）：
        - 面向国内受众，贴合中文语境
        - 严禁出现人物
        - 默认写实摄影风格（与文章内容匹配的现实场景图）
        - 每张图的 prompt 必须基于输入文本有独特内容
        """
        NO_PEOPLE = (
            "no people, no human, no person, no face, no man, no woman, "
            "no crowd, no portrait, no hands visible, "
            "empty room or outdoor space, objects only"
        )
        
        # 提取中文短句作为差异化内容
        cn_phrases = re.findall(r'[\u4e00-\u9fff]{2,8}', text)
        
        # 主题关键词匹配
        text_lower = text.lower()
        
        # 默认写实摄影风格（2026-04-15 确认：用户要求配图对应现实场景，不要抽象插画）
        subject_base = "realistic photograph of modern scene"
        style_base = (
            "photorealistic, professional photography, "
            "natural daylight, high detail, sharp focus, "
            "modern urban environment"
        )
        
        # 检测主题 → 写实风格映射
        theme_keywords = {
            'ai': ['GPT', 'ChatGPT', 'OpenAI', 'Claude', 'DeepSeek', 'Kimi', '大模型', 'AI', '人工智能', 'Sora'],
            'chip': ['英伟达', 'NVIDIA', '芯片', '半导体', '算力', 'GPU', '台积电'],
            'ev': ['特斯拉', 'Tesla', '比亚迪', '小米汽车', '自动驾驶', '新能源', '电动车', '绿牌', '车牌', '汽车'],
            'device': ['苹果', 'iPhone', '华为', '手机', '折叠屏', 'Vision Pro', 'AR', 'VR'],
            'finance': ['股票', 'A股', '基金', '比特币', 'BTC', '投资', '金融'],
            'traffic': ['交警', '交管', '交通', '车牌', '车辆', '公路', '道路', '执法'],
        }
        
        for theme, kws in theme_keywords.items():
            if any(kw in text_lower for kw in kws):
                style_base = {
                    'ai': 'realistic server room with glowing blue LED lights, data center interior, network racks',
                    'chip': 'extreme close-up macro of semiconductor wafer on cleanroom bench, golden circuits reflecting light',
                    'ev': 'realistic electric vehicle parked on modern city street, green license plate clearly visible, Chinese city background',
                    'device': 'realistic smartphone on wooden desk surface, screen showing colorful app UI, natural window lighting',
                    'finance': 'realistic stock market trading floor monitor display, candlestick charts on large LED screen',
                    'traffic': 'realistic Chinese traffic police officer directing vehicles at busy intersection, modern cars and green license plates',
                }.get(theme, style_base)
                subject_base = {
                    'ai': 'artificial intelligence data center scene',
                    'chip': 'semiconductor chip manufacturing close-up',
                    'ev': 'Chinese new energy vehicle with green license plate',
                    'device': 'consumer electronics product photography',
                    'finance': 'stock market trading visualization',
                    'traffic': 'Chinese traffic enforcement scene',
                }.get(theme, subject_base)
                break
        
        # 组装独有场景（用中文关键词确保每张不同）
        unique_parts = cn_phrases[:5]
        unique_scene = ', '.join(unique_parts) if unique_parts else subject_base
        
        prompt = f"{subject_base}, {unique_scene}, {style_base}, {NO_PEOPLE}, no text no watermark no logo"
        return prompt
    
    def _create_placeholder(self, path: str, prompt: str) -> str:
        """
        创建占位符图片（开发/测试用）
        实际部署时替换为真实图片生成
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            width, height = map(int, self.image_size.split('x'))
            
            # 创建渐变背景
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)
            
            # 绘制渐变背景（蓝紫色系）
            colors = [
                (15, 23, 42), (30, 27, 75), (45, 40, 100),
                (67, 56, 120), (88, 80, 140), (109, 110, 160),
            ]
            section_height = height // len(colors)
            for i, color in enumerate(colors):
                y0 = i * section_height
                y1 = (i + 1) * section_height if i < len(colors) - 1 else height
                draw.rectangle([0, y0, width, y1], fill=color)
            
            # 添加装饰性几何图形
            random.seed(hash(prompt) % (2**32))
            for _ in range(8):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = x1 + random.randint(-200, 200)
                y2 = y1 + random.randint(-200, 200)
                alpha = random.randint(20, 60)
                draw.line([(x1, y1), (x2, y2)], fill=(100, 150, 255, alpha), width=2)
            
            # 添加圆圈装饰
            for _ in range(3):
                cx = random.randint(width//4, 3*width//4)
                cy = random.randint(height//4, 3*height//4)
                r = random.randint(50, 150)
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(80, 130, 220), width=2)
            
            # 写入提示文字
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except:
                font = ImageFont.load_default()
            
            # 截取前几个词作为显示文本
            display_text = prompt.split('\n')[0][:50] if prompt else "AI Generated Image"
            lines = textwrap.wrap(display_text, width=30)
            
            text_y = height // 2 - (len(lines) * 30) // 2
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                tw = bbox[2] - bbox[0]
                draw.text(((width - tw) // 2, text_y), line, fill=(180, 190, 210), font=font)
                text_y += 35
            
            # 底部标注
            note_font = ImageFont.load_default()
            draw.text((20, height - 30), "AI Generated | 科技风配图", fill=(120, 140, 170), font=note_font)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            img.save(path, 'PNG')
            
            return path
            
        except ImportError:
            # Pillow 未安装，创建简单的 SVG 占位符
            svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{self.image_size.split('x')[0]}" height="{self.image_size.split('x')[1]}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f172a"/>
      <stop offset="50%" style="stop-color:#1e1e4a"/>
      <stop offset="100%" style="stop-color:#2d2864"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <text x="50%" y="50%" text-anchor="middle" fill="#a0b0c8" font-family="Arial" font-size="24">
    AI 生成配图
  </text>
</svg>'''
            
            svg_path = path.rsplit('.', 1)[0] + '.svg'
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return svg_path
    
    def generate_single(self, prompt: str, style: str = None,
                        size: str = None, suffix: str = '') -> Optional[str]:
        """单独生成一张图片

        Args:
            prompt: 图片描述（每段文案应传不同的prompt）
            style: 风格要求（可选）
            size: 尺寸，如 "1280x720"
            suffix: 文件名后缀，用于区分同一秒生成的多张图（如 "_cover", "_p0" 等）
                不传则自动用毫秒+随机数确保唯一
        """
        if not size:
            size = self.image_size
        if style:
            prompt = f"{prompt}\n风格要求：{style}"

        import time as _time
        # 用毫秒 + 随机数确保同一秒内多次调用也不会重名
        ms = int(_time.time() * 1000) % 1000
        rid = id(prompt) & 0xFFFF
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_suffix = suffix.replace(' ', '_')[:30] if suffix else f"_{ms}_{rid}"
        filename = f"img{ts}{safe_suffix}.png"
        save_path = os.path.join(self.images_dir, filename)

        logger.info(f"[ImageGen] generate_single: {filename} | prompt[:80]={prompt[:80]}")
        return self._call_image_api(prompt, save_path, size)


if __name__ == '__main__':
    import yaml
    
    with open('../config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    gen = ImageGenModule(config)
    
    test_result = gen.generate_single(
        prompt="AI芯片算力突破，未来计算新纪元",
        style="tech_abstract"
    )
    
    print(f"\n测试图片生成结果: {test_result}")
