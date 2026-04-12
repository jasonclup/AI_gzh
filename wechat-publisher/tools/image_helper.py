# -*- coding: utf-8 -*-
"""图片生成辅助工具 v3 — AI文生图 + 网络图片匹配

策略优先级：
1. Pollinations.ai 免费AI文生图（无需API Key，Flux模型）+ 重试机制
2. 备选：Pillow 渐变背景兜底

特性：
- 自动重试（429限流时自动等待重试）
- 多模型轮换（Flux → Turbo → Schnell）
- 图片缓存（相同prompt不重复下载）

输出：竖屏 1080x1920 PNG / JPG
"""

import os
import sys
import re
import time
import hashlib
import logging
import tempfile
from typing import List, Tuple, Dict, Optional
from urllib.parse import quote

log = logging.getLogger('image_helper')

DEFAULT_SIZE = "1080x1920"
DEFAULT_W, DEFAULT_H = 1080, 1920

# 超时设置（AI生图需要5-15秒生成时间）
DOWNLOAD_TIMEOUT = 25  # 单次下载超时(秒)
RETRY_MAX = 2          # 最大重试次数
RETRY_DELAY_BASE = 3   # 重试基础延迟(秒)

# Pollinations 模型列表（多模型fallback提高成功率）
POLLINATION_MODELS = ['flux', 'turbo', 'schnell']

# ── 已知的Pollinations限流占位图特征（MD5+文件大小）──
# 当IP被限流时，无论传什么prompt都返回同一张固定图片
# 这些值通过实际测试获得，如果Pollinations更新占位图需要同步更新
_PLACEHOLDER_SIGNATURES = {
    # 隧道/管道图（最常见）：122628字节
    'dd12e9e08638': 122628,
}
# 占位图文件大小容差（±2KB，防止微小差异导致误判）
_PLACEHOLDER_SIZE_TOLERANCE = 2048


# ══════════════════════════════════════
#  提示词增强：根据话题生成英文AI绘图提示词
# ══════════════════════════════════════

def _build_ai_prompt(text: str) -> str:
    """将中文话题/段落摘要转换为高质量的英文AI绘图提示词
    
    核心规则（2026-04-10 用户确认）：
    - 面向国内受众：配图风格贴合中文语境
    - 严禁出现人物：所有场景必须无人物、无面部、无人体
    - 每张图必须有独有内容：确保不同段落生成不同的图
    
    全局约束（每次都追加）：
    NO_PEOPLE_CONSTRAINT = "no people no human no person no face no man no woman \
    no crowd no portrait, empty scene, object only"
    """
    
    # ── 全局约束：绝对禁止出现人物 ──
    NO_PEOPLE = ("no people, no human, no person, no face, no man, no woman, "
                 "no crowd, no portrait, no hands visible, "
                 "empty room or outdoor space, objects only")
    
    # === 主题关键词 → 视觉风格映射（全无人）===
    theme_styles = {
        # AI / 大模型 — 无人的科技场景
        'ai': {
            'keywords': ['GPT', 'ChatGPT', 'OpenAI', 'Claude', 'DeepSeek', 'Kimi', '大模型', 'AI', '人工智能',
                        'Sora', '文生图', 'AIGC', 'LLM', '语言模型', 'AGI', '智能'],
            'style_base': ('futuristic technology scene, blue and purple neon lighting, '
                          'glowing digital brain hologram floating in dark space, '
                          'data center server racks with blue LED lights, '
                          'neural network visualization as glowing nodes and connections, '
                          'empty high-tech laboratory equipment, '
                          'cinematic composition, highly detailed, 8K quality'),
            'subject_base': 'artificial intelligence technology visualization',
        },
        # 芯片 / 算力 — 微距硬件特写
        'chip': {
            'keywords': ['英伟达', 'NVIDIA', '芯片', '半导体', '算力', 'GPU', 'CPU', '处理器', '台积电',
                        '量子', 'Quantum', '光刻', '晶圆'],
            'style_base': ('extreme close-up macro of semiconductor wafer with golden circuits, '
                          'GPU die on black motherboard with RGB glow, '
                          'silicon chip under microscope, precision manufacturing robot arm, '
                          'cleanroom interior with automated machinery only, '
                          'dark background with accent lighting, photorealistic product shot'),
            'subject_base': 'semiconductor chip hardware close-up',
        },
        # 新能源车 / 汽车 — 只有车和城市
        'ev': {
            'keywords': ['特斯拉', 'Tesla', 'FSD', '新能源', '电动车', 'EV', '比亚迪',
                        '小米汽车', '理想', '蔚来', '问界', '固态电池'],
            'style_base': ('sleek electric car parked alone in futuristic city at night, '
                          'neon reflections on car body surface, '
                          'EV charging station at sunset, empty street scene, '
                          'car cutaway showing battery pack and motor system, '
                          'automotive photography, dramatic lighting'),
            'subject_base': 'electric vehicle product showcase',
        },
        # 消费电子 / 手机 — 产品静物摄影
        'device': {
            'keywords': ['苹果', 'Apple', 'iPhone', 'iPad', 'Vision Pro', '折叠屏', '华为', '小米',
                        '手机', 'XR', 'VR', 'AR', 'Meta'],
            'style_base': ('smartphone on marble desk surface, screen showing colorful UI, '
                          'foldable phone partially open showing dual displays, '
                          'VR headset resting on clean white table, '
                          'multiple devices arranged artfully on wood surface, '
                          'soft studio lighting, editorial product photography'),
            'subject_base': 'consumer electronics still life',
        },
        # 金融 / 股票 — 数据可视化图表
        'finance': {
            'keywords': ['股票', 'A股', '牛市', '基金', '央行', '利率', '通胀', 'GDP',
                        '金融', '人民币', '比特币', 'BTC', '投资', '港股', '美股', 'ETF'],
            'style_base': ('stock market candlestick chart with red rising pattern, '
                          'gold coins stacking upward with digital trend lines, '
                          'financial data dashboard on monitor screens, '
                          'blockchain network visualization with glowing connected nodes, '
                          'digital yuan and cryptocurrency symbols floating, '
                          'clean data visualization infographic style'),
            'subject_base': 'financial market data visualization',
        },
        # 航天 / 科技前沿 — 只有设备和太空
        'space': {
            'keywords': ['SpaceX', '星舰', '火箭', '卫星', 'NASA', '火星', '航天', '宇航',
                        '脑机接口', 'Neuralink', '6G', '通信'],
            'style_base': ('rocket launching into starry sky with fiery exhaust trail, '
                          'satellite constellation orbiting above Earth city lights, '
                          'space station module with solar panels against nebula, '
                          'Mars rover on red planet surface landscape, '
                          'deep space cosmic background, documentary photography style'),
            'subject_base': 'space exploration technology',
        },
        # 社交 / 平台 — 设备和界面
        'social': {
            'keywords': ['微博', '热搜', '抖音', '微信', '社交', '网红', '直播', '平台',
                        '舆论', '隐私', '算法推荐'],
            'style_base': ('multiple smartphones arranged in a circle showing social apps, '
                          'social network graph visualization with glowing connections, '
                          'notification icons and chat bubbles floating in air, '
                          'digital world map with connection lines spreading, '
                          'colorful app interface mockups on screens, modern flat design'),
            'subject_base': 'digital social network interface',
        },
        # 机器人 — 只有机器本身
        'robot': {
            'keywords': ['机器人', 'robot', '人形机器人', '具身智能', 'automation', 'mechanical arm',
                        'Boston Dynamics', 'Figure', 'Optimus'],
            'style_base': ('humanoid robot standing alone in modern factory, '
                          'robotic arm assembling circuit boards on production line, '
                          'android figure posed elegantly in showroom display, '
                          'fleet of autonomous robots in warehouse coordination, '
                          'precision mechanical joints and metallic skin details, '
                          'industrial design photography, dramatic lighting'),
            'subject_base': 'advanced robotics and automation',
        },
    }

    text_lower = text.lower()
    
    # 匹配主题
    matched_theme = None
    max_matches = 0
    for theme_id, theme_info in theme_styles.items():
        matches = sum(1 for kw in theme_info['keywords'] if kw.lower() in text_lower)
        if matches > max_matches:
            max_matches = matches
            matched_theme = theme_info
    
    if matched_theme:
        style_base = matched_theme['style_base']
        subject_base = matched_theme['subject_base']
    else:
        style_base = ('modern technology scene, futuristic cityscape at dusk, '
                     'data center aesthetics, digital transformation visual, '
                     'clean professional look')
        subject_base = 'technology innovation'
    
    # ── 核心差异注入：从原始文本提取独特场景词 ──
    # 提取中文独特短语作为场景描述（这些是每个段落独有的）
    import re as _re
    cn_phrases = _re.findall(r'[\u4e00-\u9fff]{2,8}', text)
    
    # 提取英文独特词
    en_unique = []
    for word in text.split():
        w = word.strip(' ,.;:!()[]{}\"\'').strip()
        if w and len(w) >= 2 and w.lower() not in ('the', 'and', 'for', 'with', 'that', 'this',
                                                     'are', 'was', 'from', 'have', 'been'):
            if w not in en_unique:
                en_unique.append(w)
    
    # 构建独特的scene描述：用段落独有的短语组合成英文场景提示
    scene_parts = []
    
    # 取前几个中文短语的拼音首字母或直译感来增加变化
    for i, phrase in enumerate(cn_phrases[:4]):
        # 用中文短语本身作为差异化标记（Pollinations支持中文理解）
        scene_parts.append(phrase)
    
    # 加上英文独特词
    scene_parts.extend(en_unique[:5])
    
    # 组合成唯一场景描述
    if scene_parts:
        unique_scene = ', '.join(scene_parts[:8])
    else:
        unique_scene = subject_base
    
    # ── 最终prompt：风格基础 + 独有场景 + 禁人约束 ──
    prompt = (
        f"{subject_base}, {unique_scene}, "
        f"{style_base}, "
        f"{NO_PEOPLE}, "
        f"no text no watermark no logo"
    )
    
    return prompt


# ══════════════════════════════════════
#  图片下载核心
# ══════════════════════════════════════

def _download_image(url: str, output_path: str, timeout: int = DOWNLOAD_TIMEOUT) -> bool:
    """下载图片文件到本地"""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        log.info(f"Downloading image from: {url[:120]}...")
        start = time.time()
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            
            if len(data) < 5000:
                log.warning(f"Downloaded file too small ({len(data)} bytes), may be an error page")
                return False
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(data)
            
            elapsed = time.time() - start
            size_kb = len(data) // 1024
            log.info(f"Image downloaded OK: {size_kb}KB in {elapsed:.1f}s -> {output_path}")
            return True
            
    except Exception as e:
        err_str = str(e).lower()
        if '429' in err_str or 'too many' in err_str:
            raise  # 让调用方处理429限流
        if 'timeout' in err_str or 'timed out' in err_str:
            raise  # 超时也抛出让重试机制处理
        log.error(f"Download failed: {e}")
        return False


def _download_image_post(prompt: str, output_path: str,
                         width: int = DEFAULT_W, height: int = DEFAULT_H,
                         model: str = 'turbo', seed: int = 0,
                         timeout: int = DOWNLOAD_TIMEOUT) -> bool:
    """使用POST方式请求Pollinations AI文生图（避免GET的URL限速问题）"""
    import json, urllib.request
    
    try:
        url = "https://image.pollinations.ai/prompt"
        
        payload = json.dumps({
            "prompt": prompt,
            "width": width,
            "height": height,
            "nologo": True,
            "model": model,
            "seed": seed
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=payload, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        log.info(f"POST generating image: prompt='{prompt[:60]}...' size={width}x{height} model={model}")
        start = time.time()
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            
            if len(data) < 5000:
                log.warning(f"Downloaded file too small ({len(data)} bytes), may be an error page")
                return False
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(data)
            
            # 检测是否为Pollinations限流占位图（关键修复！）
            if _is_placeholder_image(output_path):
                log.warning(f"检测到限流占位图，删除并返回False")
                _clean_placeholder_file(output_path)
                return False
            
            elapsed = time.time() - start
            size_kb = len(data) // 1024
            log.info(f"POST image generated OK: {size_kb}KB in {elapsed:.1f}s -> {output_path}")
            return True
            
    except Exception as e:
        err_str = str(e).lower()
        if '429' in err_str or 'too many' in err_str:
            raise
        if 'timeout' in err_str or 'timed out' in err_str:
            raise
        log.error(f"POST download failed: {e}")
        return False
def _is_placeholder_image(file_path: str) -> bool:
    """检测下载的图片是否为Pollinations限流占位图
    
    检测策略：
    1. 计算文件MD5前6位，匹配已知占位图签名
    2. 文件大小在已知占位图大小的±容差范围内
    """
    try:
        fsize = os.path.getsize(file_path)
        # 快速检查：是否匹配任何已知占位图的大小范围
        for sig_md5, expected_size in _PLACEHOLDER_SIGNATURES.items():
            if abs(fsize - expected_size) <= _PLACEHOLDER_SIZE_TOLERANCE:
                # 大小接近，进一步验证MD5
                import hashlib
                md5_hash = hashlib.md5()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        md5_hash.update(chunk)
                actual_md5 = md5_hash.hexdigest()[:len(sig_md5)]
                if actual_md5 == sig_md5:
                    log.warning(f"检测到Pollinations限流占位图! MD5={actual_md5}... size={fsize} (预期≈{expected_size})")
                    return True
        return False
    except Exception as e:
        log.debug(f"占位图检测异常: {e}")
        return False


def _clean_placeholder_file(file_path: str):
    """删除已确认的占位图文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            log.info(f"已删除占位图文件: {file_path}")
    except Exception as e:
        log.warning(f"无法删除占位图文件 {file_path}: {e}")


#  图片缓存（避免重复下载相同prompt）
# ══════════════════════════════════════

_IMAGE_CACHE_DIR = None

def _get_cache_dir():
    """获取缓存目录路径"""
    global _IMAGE_CACHE_DIR
    if _IMAGE_CACHE_DIR is None:
        # 在项目目录下的 .image_cache 文件夹
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _IMAGE_CACHE_DIR = os.path.join(base_dir, '.image_cache')
        os.makedirs(_IMAGE_CACHE_DIR, exist_ok=True)
    return _IMAGE_CACHE_DIR


def _get_cache_key(prompt: str, size: str) -> str:
    """根据prompt和size生成缓存key（文件名）"""
    raw = f"{prompt}|{size}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()[:16]


def _check_cache(prompt: str, size: str, output_path: str) -> Optional[str]:
    """
    检查是否有缓存的图片。
    如果有，直接复制到目标路径并返回 "OK"。
    如果没有，返回 None。
    """
    cache_dir = _get_cache_dir()
    cache_key = _get_cache_key(prompt, size)
    
    # 查找所有可能的缓存文件格式
    for ext in ['.png', '.jpg', '.jpeg']:
        cache_file = os.path.join(cache_dir, cache_key + ext)
        if os.path.exists(cache_file):
            try:
                import shutil
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copy2(cache_file, output_path)
                size_kb = os.path.getsize(output_path) // 1024
                log.info(f"Cache HIT: {cache_key}{ext} -> {output_path} ({size_kb}KB)")
                return "OK"
            except Exception as e:
                log.warning(f"Cache copy failed: {e}")
    
    return None


def _save_to_cache(prompt: str, size: str, output_path: str):
    """将生成的图片保存到缓存"""
    try:
        cache_dir = _get_cache_dir()
        cache_key = _get_cache_key(prompt, size)
        
        # 根据实际文件格式确定扩展名
        _, ext = os.path.splitext(output_path)
        if not ext or ext.lower() not in ('.png', '.jpg', '.jpeg'):
            ext = '.png'
        
        cache_file = os.path.join(cache_dir, cache_key + ext.lower())
        import shutil
        shutil.copy2(output_path, cache_file)
        log.info(f"Cached: {cache_file}")
    except Exception as e:
        log.warning(f"Cache save failed (non-critical): {e}")


# ══════════════════════════════════════
#  方法1: Pollinations.ai AI文生图（首选）
# ══════════════════════════════════════

def _generate_with_pollinations(prompt_text: str, output_path: str, 
                                 width: int = DEFAULT_W, height: int = DEFAULT_H,
                                 model: str = None, seed: int = 0) -> str:
    """
    使用 Pollinations.ai 免费AI文生图API生成图片（POST方式，带重试和模型轮换）。
    
    特点：
    - 完全免费，无需API Key
    - 支持多模型自动轮换
    - 自动重试（429限流时指数退避）
    - POST方式避免GET请求的URL长度和限速问题
    
    文档：https://pollinations.ai/
    """
    import json
    
    ai_prompt = _build_ai_prompt(prompt_text)
    
    # 确定要尝试的模型列表
    if model:
        models_to_try = [model]
    else:
        models_to_try = POLLINATION_MODELS
    
    last_error = None
    
    for model_idx, try_model in enumerate(models_to_try):
        # 每个模型最多重试 RETRY_MAX 次
        for retry in range(RETRY_MAX):
            attempt_label = f"model={try_model} retry={retry+1}/{RETRY_MAX}" if RETRY_MAX > 1 else f"model={try_model}"
            log.info(f"Pollinations [{attempt_label}]: {ai_prompt[:60]}...")
            
            try:
                result = _download_image_post(
                    prompt=ai_prompt, output_path=output_path,
                    width=width, height=height,
                    model=try_model, seed=seed or (hash(prompt_text) % 10000),
                    timeout=DOWNLOAD_TIMEOUT
                )
                if result:
                    # 验证是否为有效图片
                    try:
                        from PIL import Image
                        img = Image.open(output_path)
                        img.verify()
                        
                        fsize = os.path.getsize(output_path)
                        
                        _save_to_cache(prompt_text, f"{width}x{height}", output_path)
                        log.info(f"Pollinations.ai SUCCESS [{attempt_label}]: {fsize//1024}KB")
                        return "OK"
                    except Exception as verify_err:
                        log.warning(f"Invalid image file: {verify_err}")
                        continue
                        
                last_error = "download returned False"
                
            except Exception as e:
                err_str = str(e).lower()
                last_error = str(e)
                
                is_rate_limit = '429' in err_str or 'too many' in err_str
                is_timeout = 'timeout' in err_str or 'timed out' in err_str
                
                if is_rate_limit or is_timeout:
                    # 计算退避时间：指数退避 + 抖动
                    delay = RETRY_DELAY_BASE * (2 ** retry) + (retry * 0.5)
                    delay = min(delay, 30)  # 最大30秒
                    wait_type = "rate limit" if is_rate_limit else "timeout"
                    
                    log.warning(f"Pollinations [{attempt_label}] {wait_type}: waiting {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    # 其他错误，直接换下一个模型
                    log.warning(f"Pollinations [{attempt_label}] error: {e}, switching model")
                    break
        
        # 当前模型所有重试都失败了，换下一个模型
        log.warning(f"Model {try_model} exhausted, trying next model...")
    
    log.error(f"All Pollinations models failed. Last error: {last_error}")
    return "ERROR:all_models_failed"


# ══════════════════════════════════════
#  方法2: Unsplash Source（备选）
# ══════════════════════════════════════

# 关键词 → Unsplash 搜索词映射
_UNSPLASH_KEYWORD_MAP = {
    'AI': 'artificial intelligence technology',
    'GPT': 'chatbot AI interface',
    'ChatGPT': 'artificial intelligence chatbot',
    'DeepSeek': 'deep learning AI research',
    '芯片': 'microchip processor technology',
    'NVIDIA': 'GPU graphics card technology',
    '英伟达': 'graphics processing unit',
    '特斯拉': 'Tesla electric car',
    '电动车': 'electric vehicle future',
    '新能源': 'green energy technology',
    '苹果': 'Apple iPhone product',
    '华为': 'smartphone technology',
    '手机': 'mobile phone technology',
    '股票': 'stock market financial charts',
    'A股': 'Chinese stock exchange',
    '金融': 'finance business technology',
    '比特币': 'bitcoin cryptocurrency digital',
    '投资': 'investment portfolio analysis',
    'SpaceX': 'SpaceX rocket launch',
    '火箭': 'space rocket technology',
    '航天': 'space exploration astronaut',
    '机器人': 'robotics humanoid robot',
    '自动驾驶': 'autonomous driving car sensor',
    '折叠屏': 'foldable smartphone display',
    'VR': 'virtual reality headset',
    'AR': 'augmented reality glasses',
    '元宇宙': 'metaverse virtual world',
    '量子计算': 'quantum computer technology',
    '脑机接口': 'brain computer interface neural',
    '6G': 'telecommunications 6G network',
    '固态电池': 'solid state battery technology',
    '游戏': 'video game controller gaming',
}


def _get_unsplash_query(text: str) -> str:
    """根据文本内容找到最合适的Unsplash搜索词"""
    for kw, query in _UNSPLASH_KEYWORD_MAP.items():
        if kw.lower() in text.lower():
            return query
    # 默认
    return 'technology digital future abstract'


def _generate_with_unsplash(prompt_text: str, output_path: str,
                             width: int = DEFAULT_W, height: int = DEFAULT_H) -> str:
    """
    使用 Unsplash Source API 获取相关免费高清图片。
    
    注意：Unsplash Source 已被官方弃用，但部分镜像仍可用。
    作为 Pollinations 的降级方案。
    """
    query = _get_unsplash_query(prompt_text)
    encoded_query = quote(query, safe='')
    
    # 尝试多个Unsplash兼容源
    urls = [
        f"https://source.unsplash.com/{width}x{height}?{encoded_query}",
        f"https://images.unsplash.com/photo-{hashlib.md5(query.encode()).hexdigest()}?w={width}&h={height}&fit=crop",
    ]
    
    for i, url in enumerate(urls):
        log.info(f"Unsplash attempt {i+1}: {query}")
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                # Unsplash会返回302重定向，需要跟踪
                final_url = resp.geturl()
                data = resp.read()
                
                if len(data) > 5000:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    log.info(f"Unsplash download OK: {len(data)//1024}KB")
                    return "OK"
                    
        except Exception as e:
            log.warning(f"Unsplash attempt {i+1} failed: {e}")
            continue
    
    return "ERROR:all_unsplash_failed"


# ══════════════════════════════════════
#  方法3: 备用 - 用内置image_gen工具（通过WorkBuddy）
# ══════════════════════════════════════

def _generate_with_fallback_pillow(prompt_text: str, output_path: str,
                                    width: int = DEFAULT_W, height: int = DEFAULT_H) -> str:
    """
    终极备用方案：用Pillow画一个带文字的渐变背景图。
    仅在所有在线方式都失败时使用。
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return "ERROR:Pillow not installed"
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # 渐变背景（深蓝→深紫）
        for y in range(height):
            t = y / height
            r = int(15 + (30 - 15) * t)
            g = int(23 + (20 - 23) * t)
            b = int(42 + (60 - 42) * t)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 加载字体
        font_large = font_medium = font_small = None
        font_candidates = ['msyh.ttc', 'simhei.ttf', 'simsun.ttc', 'arial.ttf']
        for fc in font_candidates:
            try:
                font_large = ImageFont.truetype(fc, 48)
                font_medium = ImageFont.truetype(fc, 28)
                font_small = ImageFont.truetype(fc, 18)
                break
            except OSError:
                continue
        if not font_large:
            font_large = font_medium = font_small = ImageFont.load_default()
        
        # 标题区域
        accent = (99, 102, 241)
        draw.rectangle([0, 0, width, 180], fill=(12, 18, 35))
        draw.line([(50, 168), (width - 50, 168)], fill=accent, width=3)
        
        # 显示截断的文本作为标题
        display_text = prompt_text[:25] + ('...' if len(prompt_text) > 25 else '')
        bbox = draw.textbbox((0, 0), display_text, font=font_large)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) // 2, 70), display_text, fill=(230, 235, 255), font=font_large)
        
        sub = "Tech Article Visual"
        sbbox = draw.textbbox((0, 0), sub, font=font_small)
        sw = sbbox[2] - sbbox[0]
        draw.text(((width - sw) // 2, 130), sub, fill=(140, 155, 180), font=font_small)
        
        # 底部信息栏
        footer_h = 100
        draw.rectangle([0, height - footer_h, width, height], fill=(12, 18, 35))
        draw.line([(50, height - footer_h + 12), (width - 50, height - footer_h + 12)], 
                   fill=accent, width=2)
        
        from datetime import datetime
        date_str = datetime.now().strftime('%Y.%m.%d')
        ft = f"Generated {date_str}"
        fbbox = draw.textbbox((0, 0), ft, font=font_small)
        fw = fbbox[2] - fbbox[0]
        draw.text(((width - fw) // 2, height - footer_h + 38), ft, fill=(140, 155, 180), font=font_small)
        
        # 中间装饰：几个发光圆点
        import random
        random.seed(hash(prompt_text) % (2**32))
        for _ in range(15):
            cx = random.randint(100, width - 100)
            cy = random.randint(250, height - 200)
            cr = random.randint(40, 150)
            for r in range(cr, 0, -4):
                alpha = int(30 * (r / cr))
                color = tuple(min(255, c + alpha) for c in accent)
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color)
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=accent)
        
        img.save(output_path, 'PNG', quality=95)
        log.warning("Used fallback pillow generator (online methods all failed)")
        return "OK"
        
    except Exception as e:
        return f"ERROR:fallback_failed:{str(e)}"


# ══════════════════════════════════════
#  主入口函数（保持原有接口不变）
# ══════════════════════════════════════

def generate_image(prompt: str, output_path: str, size: str = DEFAULT_SIZE, seed: int = 0) -> str:
    """
    根据提示词生成配图。自动选择最佳图片来源策略。
    
    Args:
        prompt: 文本描述
        output_path: 输出路径
        size: 尺寸字符串
        seed: 随机种子（0=自动）
    策略链：
    0. 缓存检查（相同prompt不重复下载）✅
    1. Pollinations.ai (Flux) — 免费 AI 文生图，高质量 ✅ 推荐
       → 自动检测限流占位图（MD5+大小匹配），发现时立即切换策略
    2. Pillow 渐变备用 — 本地兜底（最后手段）
    
    Args:
        prompt: 文本描述（用于生成相关图片）
        output_path: 输出路径（如 static/generated_images/xxx.png）
        size: 尺寸字符串，如 "1080x1920"
    
    Returns:
        'OK' 成功
        'ERROR:...' 失败原因
    """
    # 解析尺寸
    try:
        w_str, h_str = size.split('x')
        img_w, img_h = int(w_str), int(h_str)
    except Exception:
        img_w, img_h = DEFAULT_W, DEFAULT_H
    
    # 清理 prompt
    clean_prompt = prompt.strip()
    if not clean_prompt:
        clean_prompt = "technology innovation"
    
    log.info(f"generate_image: prompt='{clean_prompt[:50]}...' size={img_w}x{img_h} -> {output_path}")
    
    # === 策略0: 检查缓存 ===
    cached = _check_cache(clean_prompt, f"{img_w}x{img_h}", output_path)
    if cached == "OK":
        return "OK"
    
    # === 策略1: Pollinations.ai AI文生图（首选，带重试+模型轮换）===
    result = _generate_with_pollinations(clean_prompt, output_path, width=img_w, height=img_h, seed=seed)
    if result == "OK":
        return "OK"
    else:
        log.warning(f"Pollinations.ai failed: {result}, trying fallback...")
    
    # === 策略2: Pillow 本地兜底（最后手段）===
    result = _generate_with_fallback_pillow(clean_prompt, output_path, width=img_w, height=img_h)
    if result == "OK":
        _save_to_cache(clean_prompt, f"{img_w}x{img_h}", output_path)
    return result


def extract_keywords(text: str) -> List[str]:
    """从文本中提取可能的关键词（保持向后兼容）"""
    known_kw = [
        'AI', 'GPT', 'ChatGPT', 'Sora', 'DeepSeek', 'Kimi',
        '英伟达', '苹果', '华为', '特斯拉', '小米', 'OpenAI',
        '芯片', '自动驾驶', '新能源', '量子', '机器人', '元宇宙',
        '大模型', '算力', '5G', '6G', '脑机接口', '折叠屏',
        '固态电池', 'FSD', '鸿蒙', 'Vision Pro', 'SpaceX',
    ]
    found = []
    text_lower = text.lower()
    for kw in known_kw:
        if kw.lower() in text_lower and kw not in found:
            found.append(kw)
            if len(found) >= 5:
                break
    return found


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python image_helper.py <prompt> <output_path> [size]")
        print("       v3: AI text-to-image via Pollinations.ai + Unsplash fallback")
        sys.exit(1)
    p = sys.argv[1]
    out = sys.argv[2]
    s = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_SIZE
    result = generate_image(p, out, s)
    print(result)
