# -*- coding: utf-8 -*-
"""
智能配图模块 v3 — 真实图片优先，AI补位（2026-04-15升级）

核心规则（用户确认，后续严禁违反）：
  1. 涉及真实产品/品牌 → 从网上搜索真实产品图片（不AI生图）
  2. 虚拟/抽象概念 → AI生成配图
  3. 一篇文章：封面1张 + 配图0-3张（宁少勿乱配）
  4. 真图和AI图混合搭配使用

调用流程：
  Agent模式（当前）：
    1. Agent分析文章内容 → _detect_real_products() 判断真/AI
    2. 真产品 → get_real_image_search_query() 返回搜索关键词 → Agent去网上搜图下载
    3. 虚拟概念 → get_ai_prompt() 返回prompt → Agent用image_gen生成
"""

import os
import logging
import re
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger('WechatPublisher.ImageGenV3')


class ImageGenModuleV3:
    """智能配图 v3 — 真实图片优先"""

    # ════════════════════════════════════════════════
    # 真实产品/品牌检测词库
    # 匹配到这些关键词 → 应该搜真图，不要AI生图
    # ════════════════════════════════════════════════

    REAL_PRODUCT_PATTERNS = {
        'phone': [
            r'iPhone\s*\d+[A-Za-z]?|iPhone\s*(Pro|Plus|Max)?',
            r'华为[\s\w]*(?:Pura|Mate|Nova|畅享|Pocket|折叠屏)',
            r'小米[\s\w]*(?:MIX|Civi|\d+\s*Pro|Redmi|红米)',
            r'OPPO[\s\w]*(?:Find|Reno)|vivo[\s\w]*[XSV]\d+|iQOO',
            r'Samsung.*Galaxy.*S\d|三星Galaxy',
        ],
        'car': [
            r'Tesla|特斯拉\s*(Model\s*[XYZSD]|Cybertruck)',
            r'比亚迪.*(汉|唐|宋|秦|海豹|海鸥|仰望|腾势|方程豹)',
            r'理想\s*L[6789]|蔚来\s*ES[5678]|小鹏\s*P[6789]|问界\s*M[5679]',
            r'宝马|奔驰|奥迪|丰田|本田|大众|福特|吉利|长城|五菱',
        ],
        'tech_hardware': [
            r'英伟达.*(RTX\s*\d+\s*(Ti|Super)?|GeForce)|NVIDIA',
            r'Apple.*(Vision\s*Pro|M[1-5]\s*芯片|iPad\s*Pro|MacBook)',
            r'(芯片|处理器|GPU|显卡|固态硬盘|SSD)',
        ],
        'person': [
            r'(马斯克|任正非|雷军|余承东|黄仁勋|库克|马云|马化腾)',
            r'(姚安娜|刘立荣|李子柒)',
        ],
        'location': [
            r'(广交会|车展|CES|MWC|WWDC|苹果发布会)',
            r'(特斯拉工厂|比亚迪工厂|富士康)',
        ],
    }

    def __init__(self, config: dict):
        self.config = config
        self.output_dir = config.get('OUTPUT_DIR', './output')
        _output_abs = os.path.abspath(self.output_dir)
        self.images_dir = os.path.join(_output_abs, 'images')
        os.makedirs(self.images_dir, exist_ok=True)

    # ────────────────────────────────────────
    # 核心方法：分析话题，返回配图方案
    # ────────────────────────────────────────

    def analyze_topic_for_images(self, topic: str, title: str,
                                  article_text: str = '') -> Dict:
        """
        分析文章内容，输出完整的配图方案

        Returns:
            {
                'cover': { 'type': 'real'|'ai', 'search_query'|'ai_prompt': ... },
                'paragraphs': [
                    { 'type': 'real', 'search_query': '...', 'position': 1 },
                    { 'type': 'ai', 'ai_prompt': '...', 'position': 2 },
                    ...
                ]
            }
        """
        combined_text = f"{topic} {title} {article_text}"

        real_matches = self._detect_real_products(combined_text)

        logger.info(f"配图分析: 话题=[{topic}], 真实产品匹配={real_matches}")

        # 封面策略
        cover_plan = self._plan_cover(topic, title, real_matches)

        # 段落配图策略（1-3张）
        para_plans = self._plan_paragraph_images(
            topic, real_matches, max_count=3
        )

        return {
            'cover': cover_plan,
            'paragraphs': para_plans,
            'real_products_found': real_matches,
        }

    def _detect_real_products(self, text: str) -> List[Dict]:
        """
        检测文本中涉及的真实产品/品牌

        Returns:
            [ {'category': 'phone', 'match': '华为Pura X Max', 'keyword': '华为Pura'}, ... ]
        """
        results = []
        seen = set()

        for category, patterns in self.REAL_PRODUCT_PATTERNS.items():
            for pat in patterns:
                match = re.search(pat, text)
                if match and match.group() not in seen:
                    matched_text = match.group()
                    # 限制匹配长度（避免抓到整篇文章）
                    if len(matched_text) > 30:
                        matched_text = matched_text[:30]
                    seen.add(matched_text)
                    results.append({
                        'category': category,
                        'match': matched_text,
                        'keyword': self._extract_search_keyword(matched_text),
                    })
                    break  # 每个category只取第一个匹配

        return results

    def _extract_search_keyword(self, matched_text: str) -> str:
        """从匹配文本提取适合搜索图片的关键词"""
        # 清理多余字符，保留核心产品名
        cleaned = matched_text.strip()

        # 如果太短（<3字），补充常见搜索词
        if len(cleaned) < 3:
            return f"{cleaned} 产品 官方图"

        return cleaned

    def _plan_cover(self, topic: str, title: str,
                     real_matches: List[Dict]) -> Dict:
        """规划封面图"""
        if real_matches:
            # 有真实产品 → 用最强匹配的产品做封面
            best_match = real_matches[0]
            return {
                'type': 'real',
                'search_query': f"{best_match['keyword']} 官方产品图 高清",
                'source_product': best_match['match'],
                'reason': f"封面匹配到真实产品: {best_match['match']}",
            }
        else:
            # 无真实产品 → AI生成概念封面
            return {
                'type': 'ai',
                'ai_prompt': self._build_cover_ai_prompt(topic, title),
                'reason': '无真实产品匹配，使用AI概念封面',
            }

    def _plan_paragraph_images(self, topic: str,
                                real_matches: List[Dict],
                                max_count: int = 3) -> List[Dict]:
        """
        规划段落配图（0-3张）

        策略：
          - 有多个真产品 → 前1-2张用真图（不同产品），剩余用AI场景图
          - 无真产品或只有1个 → 全部AI生成
        """
        plans = []

        if len(real_matches) >= 2:
            # 多个产品 → 封面用了第1个，段落可以用第2个的真图
            plans.append({
                'type': 'real',
                'search_query': f"{real_matches[1]['keyword']} 实拍 使用场景",
                'position': 1,
            })
            remaining = max_count - len(plans)

        elif real_matches:
            # 只有1个产品 → 封面已用它，段落全用AI场景
            remaining = max_count
        else:
            remaining = max_count

        # 补充AI生成的场景图
        ai_scenes = self._build_para_ai_prompts(topic, remaining)
        start_pos = len(plans) + 1
        for i, prompt in enumerate(ai_scenes):
            plans.append({
                'type': 'ai',
                'ai_prompt': prompt,
                'position': start_pos + i,
            })

        return plans[:max_count]

    # ────────────────────────────────────────
    # AI Prompt 构建（给image_gen工具用的）
    # ────────────────────────────────────────

    def _build_cover_ai_prompt(self, topic: str, title: str) -> str:
        """构建AI封面prompt（仅当无真实产品时调用）"""
        # 从标题/话题提取视觉关键词
        keywords = self._extract_visual_keywords(f"{topic} {title}")

        base_prompt = (
            "Professional magazine cover style photography, "
            "clean elegant composition with ample negative space, "
            "high quality editorial aesthetic. "
        )

        if any(k in topic for k in ['AI', '芯片', '科技', '算力', '大模型']):
            scene = (
                "abstract technology theme with subtle digital elements, "
                "blue and white gradient background"
            )
        elif any(k in topic for k in ['汽车', '新能源', '电动车', '智驾']):
            scene = (
                "modern electric vehicle on a scenic road at golden hour, "
                "no visible license plate, no people in frame"
            )
        elif any(k in topic for k in ['股票', '基金', '财经', '投资']):
            scene = (
                "financial data on screen with charts and graphs, "
                "modern office environment, professional business feel"
            )
        else:
            scene = (
                f"editorial photograph related to {keywords}, "
                f"documentary style, clean composition"
            )

        privacy_suffix = (
            ". No people, no faces, no text overlay, "
            "no license plates, no phone numbers, no personal information."
        )

        return f"{base_prompt}{scene}{privacy_suffix}"

    def _build_para_ai_prompts(self, topic: str, count: int) -> List[str]:
        """构建段落AI配图的prompt列表（每张不同）"""
        prompts = []

        # 根据话题类型选择不同的场景方向
        scenes = []

        if any(k in topic for k in ['汽车', '新能源', '电动车']):
            scenes = [
                "Realistic photograph of modern EV charging station at night, "
                "illuminated chargers with cars plugged in, urban setting. "
                "No people, no faces, no license plates. Professional documentary photography.",

                "Realistic photograph of highway with multiple new energy vehicles driving, "
                "clear daytime weather, road perspective view. "
                "No people visible, no identifiable license plates. Wide angle automotive photo.",

                "Realistic photograph of solar panels and wind turbines along a modern highway, "
                "clean energy infrastructure, bright sunny day. "
                "No people, no text. Environmental photography style.",
            ]
        elif any(k in topic for k in ['AI', '科技', '芯片', '算力']):
            scenes = [
                "Realistic photograph of server racks in a modern data center, "
                "blue LED indicator lights, clean organized cables. "
                "No people, no faces. Technology infrastructure photography.",

                "Realistic photograph of a busy tech startup open-plan office, "
                "multiple monitors showing code and data, bright daylight. "
                "No visible faces, no screens with readable text. Business documentary style.",

                "Realistic photograph of semiconductor fabrication facility interior, "
                "clean room environment with yellow lighting, automated equipment. "
                "No people visible. Industrial photography.",
            ]
        elif any(k in topic for k in ['金融', '股票', '投资', '基金']):
            scenes = [
                "Realistic photograph of stock market trading floor display board, "
                "red and green numbers showing price changes, professional finance environment. "
                "No people, no readable specific company names. Financial photography.",

                "Realistic photograph of modern city skyline at dusk with financial district buildings illuminated, "
                "reflecting in water below. Cityscape photography. No text overlays.",
            ]
        elif any(k in topic for k in ['广交会', '展览', '展会', '贸易']):
            scenes = [
                "Realistic photograph of large international trade exhibition hall interior, "
                "bright lighting, wide aisles, product display booths. "
                "No people visible in frame. Commercial event photography.",

                "Realistic photograph of shipping containers at a port terminal with cranes, "
                "global trade logistics concept, clear daytime weather. "
                "No workers visible. Industrial documentary style.",
            ]
        else:
            # 通用场景
            scenes = [
                "Realistic photograph of modern Chinese city street scene at day, "
                "clean architecture, urban life atmosphere. No people, no faces. Documentary style.",

                "Realistic photograph of contemporary workspace or cafe environment, "
                "natural lighting, warm tones. No visible faces, no text. Lifestyle photography.",
            ]

        # 确保有足够的场景，不够就循环
        for i in range(count):
            idx = i % len(scenes)
            prompts.append(scenes[idx])

        return prompts[:count]

    def _extract_visual_keywords(self, text: str) -> str:
        """从文本中提取可用于构建视觉描述的关键词"""
        visual_words = []
        known_visual = [
            '新能源车', '电动汽车', '充电桩', '自动驾驶',
            'AI', '芯片', '数据中心', '服务器', '机器人',
            '智能手机', '折叠屏', '笔记本电脑',
            '股票', '交易大厅', '城市天际线', '港口',
            '工厂', '生产线', '展厅', '展览馆',
        ]

        lower = text.lower()
        for kw in known_visual:
            if kw.lower() in lower:
                visual_words.append(kw)

        return ', '.join(visual_words[:5]) if visual_words else 'modern lifestyle'

    # ────────────────────────────────────────
    # 工具方法
    # ────────────────────────────────────────

    def get_image_path(self, filename: str) -> str:
        """获取图片的完整存储路径"""
        return os.path.join(self.images_dir, filename)

    def list_existing_images(self) -> List[str]:
        """列出已存在的所有图片文件"""
        if not os.path.exists(self.images_dir):
            return []
        return [f for f in os.listdir(self.images_dir)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]


# 向后兼容的别名
ImageGenModule = ImageGenModuleV3
