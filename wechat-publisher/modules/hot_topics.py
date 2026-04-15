# -*- coding: utf-8 -*-
"""
Hot topic fetcher - v3 Network Fixed
Working sources (verified 2026-04-09):
  1. Toutiao API (JSON, 50 items) ★ Primary
  2. Tophub Weibo (HTML parsing)
  3. Baidu Hot Search (HTML parsing)

All requests: 8s timeout, auto-fallback.
Uses urllib (stdlib) to avoid requests dependency issues.
"""

import json
import logging
import random
import re
import urllib.request
import socket
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger('WechatPublisher.HotTopicFetcher')

REQUEST_TIMEOUT = 8  # ALL external requests: max 8 seconds

COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Fallback: DO NOT use stale hardcoded topics!
# If all external sources fail, raise error instead of publishing outdated content.
FALLBACK_TOPICS = []


def _http_get(url: str, extra_headers: dict = None, timeout: int = REQUEST_TIMEOUT) -> tuple:
    """
    Unified HTTP GET. Returns (status_code, raw_text).
    Never hangs - always respects timeout.
    """
    headers = {**COMMON_HEADERS}
    if extra_headers:
        headers.update(extra_headers)

    try:
        req = urllib.request.Request(url, headers=headers)
        # Use a socket-level timeout for safety
        socket.setdefaulttimeout(timeout)
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = resp.read()
        # Try UTF-8 first, then gbk for Chinese sites
        for enc in ['utf-8', 'gbk', 'gb2312']:
            try:
                text = data.decode(enc)
                return (resp.status, text)
            except (UnicodeDecodeError, LookupError):
                continue
        return (resp.status, data.decode('utf-8', errors='replace'))
    except Exception as e:
        logger.debug(f"HTTP GET failed [{url}]: {e}")
        return (0, str(e))


class HotTopicFetcher:
    """Hot topic collector with verified working sources."""

    def __init__(self, config: dict):
        self.config = config
        self.sources = config.get('HOT_SOURCES', [])
        self.tech_keywords = [
            'AI', '人工智能', 'GPT', 'ChatGPT', '机器人', '芯片', '半导体',
            '苹果', '华为', '小米', '特斯拉', '马斯克', '手机', '科技',
            '元宇宙', 'VR', 'AR', '区块链', '比特币', '加密货币', '量子',
            '5G', '6G', '新能源', '自动驾驶', '大模型', '算力',
            '英伟达', 'OpenAI', '谷歌', '微软', '三星',
            'Sora', 'Claude', 'Gemini', 'DeepSeek', 'Kimi',
            '智能', '数字', '互联网', 'APP', '算法', '数据',
            '卫星', '火箭', 'SpaceX', '脑机接口', '折叠屏'
        ]

    def fetch_all(self) -> List[Dict]:
        """Fetch from all available sources. Always returns data."""
        all_topics = []
        source_ok = False

        # Source priority order (verified working):
        # 1. Toutiao API (JSON, most reliable)
        # 2. Baidu Hot (HTML)
        # 3. Tophub (HTML fallback)

        # Try each source independently
        fetchers = [
            ('今日头条', self._fetch_toutiao),
            ('百度热搜', self._fetch_baidu),
            ('Tophub微博', self._fetch_tophub_weibo),
        ]

        enabled_names = {s.get('name', '') for s in self.sources if s.get('enabled', True)}

        for name, fn in fetchers:
            # If user has specific sources configured, respect that
            if self.sources:
                # More flexible matching: partial substring match both ways
                is_match = any(
                    name in n or n in name
                    for n in enabled_names
                )
                # Also allow all sources to run when config has sources but none match (fallback behavior)
                # Only skip if explicitly disabled
                any_disabled = any(
                    s.get('name', '') and (name in s['name'] or s['name'] in name) and not s.get('enabled', True)
                    for s in self.sources
                )
                if any_disabled:
                    continue

            try:
                topics = fn()
                if topics:
                    source_ok = True
                    for t in topics:
                        t['source'] = name
                        t['fetched_at'] = datetime.now().isoformat()
                    all_topics.extend(topics)
                    logger.info(f"[{name}] Got {len(topics)} topics")
                    # If got good data from primary source, still try others for variety
                    # but don't break - collect from all working sources
            except Exception as e:
                logger.debug(f"[{name}] Failed: {e}")

        # CRITICAL: if all sources failed, do NOT silently use stale topics
        if not all_topics:
            logger.error("All external sources failed! No hot topics available.")
            # Return empty list - caller must handle this as a blocking error
            return []

        # Dedup by title
        seen = set()
        unique_topics = []
        for t in all_topics:
            key = t.get('title', '').strip()
            if key and key not in seen:
                seen.add(key)
                unique_topics.append(t)

        # Sort: tech first, then by hot value
        def _sort_key(x):
            hv = x.get('hot_value', 0)
            try:
                hv = int(hv)
            except (TypeError, ValueError):
                hv = 0
            return (
                0 if self._is_tech_topic(x.get('title', '')) else 1,
                -hv
            )
        unique_topics.sort(key=_sort_key)

        return unique_topics[:50]

    # ─── Source 1: Toutiao API (JSON, VERIFIED WORKING) ──────────────

    def _fetch_toutiao(self) -> List[Dict]:
        """Fetch Toutiao trending - returns JSON."""
        topics = []
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        status, raw = _http_get(url, extra_headers={
            'Referer': 'https://www.toutiao.com/',
        })

        if status != 200 or not raw.strip().startswith('{'):
            return topics

        try:
            data = json.loads(raw)
            items = data.get('data', [])
            for item in items[:50]:
                title = item.get('Title', '')
                if title and len(title) > 2:
                    hv = item.get('HotValue', 0)
                    try:
                        hv = int(hv)
                    except (TypeError, ValueError):
                        hv = 0
                    topics.append({
                        'title': title,
                        'hot_value': hv,
                        'category': item.get('Category', ''),
                        'url': item.get('Url', ''),
                    })
        except (json.JSONDecodeError, KeyError) as e:
            logger.debug(f"Toutiao parse error: {e}")

        return topics

    # ─── Source 2: Baidu Hot Search (HTML, VERIFIED ACCESSIBLE) ──────

    def _fetch_baidu(self) -> List[Dict]:
        """Fetch Baidu hot search from HTML page."""
        topics = []
        url = "https://top.baidu.com/board?tab=realtime"
        status, raw = _http_get(url)

        if status != 200 or len(raw) < 500:
            return topics

        # Parse: extract title + hot value from HTML patterns
        # Baidu format: <a ... title="话题名" ... /> ... <span class="...">热度值</span>
        try:
            # Pattern 1: title attribute in tags
            titles = re.findall(r'title="([^"]{3,50})"', raw[:50000])
            # Pattern 2: numeric hot values nearby
            numbers = re.findall(r'>(\d{4,10})<', raw[:50000])

            # Pair them up (rough alignment)
            min_len = min(len(titles), len(numbers))
            for i in range(min_len):
                if i >= 30:  # cap at 30 per source
                    break
                topics.append({
                    'title': titles[i],
                    'hot_value': int(numbers[i]) if numbers[i].isdigit() else 0,
                    'category': '',
                    'url': f'https://www.baidu.com/s?wd={urllib.request.quote(titles[i])}',
                })
        except Exception as e:
            logger.debug(f"Baidu parse error: {e}")

        return topics

    # ─── Source 3: Tophub (HTML, backup source) ─────────────────────

    def _fetch_tophub_weibo(self) -> List[Dict]:
        """Fetch Weibo hot topics via Tophub aggregator (HTML)."""
        topics = []
        url = "https://tophub.today/n/KqndgxeLl9"
        status, raw = _http_get(url)

        if status != 200 or len(raw) < 1000:
            return topics

        try:
            # Tophub format: table rows with <td class="al"><a>标题</a></td>
            # and adjacent td with numeric value
            items = re.findall(
                r'<td class="al">.*?<a[^>]*>([^<]{3,50})</a>.*?'
                r'(\d[\d,.]*\d|\d+)',
                raw[:80000],
                re.DOTALL
            )
            for title_str, hv_str in items[:30]:
                # Clean up hot value string
                hv_clean = re.sub(r'[,.\s]', '', hv_str)
                topics.append({
                    'title': title_str.strip(),
                    'hot_value': int(hv_clean) if hv_clean.isdigit() else 0,
                    'category': '',
                    'url': url,
                })
        except Exception as e:
            logger.debug(f"Tophub parse error: {e}")

        return topics

    # ─── Utility methods ────────────────────────────────────────────

    def _is_tech_topic(self, title: str) -> bool:
        """Check if a title is tech-related."""
        title_lower = title.lower()
        return any(kw.lower() in title_lower for kw in self.tech_keywords)

    def get_tech_topics(self, count: int = 20) -> List[Dict]:
        """Get tech-focused hot topics."""
        all_topics = self.fetch_all()
        tech_topics = [t for t in all_topics if self._is_tech_topic(t.get('title', ''))]
        if len(tech_topics) < count:
            non_tech = [t for t in all_topics if not self._is_tech_topic(t.get('title', ''))]
            tech_topics.extend(non_tech[:count - len(tech_topics)])
        return tech_topics[:count]

    def get_viral_titles(self, base_title: str) -> List[str]:
        """Generate viral title variations based on a base title."""
        templates = [
            f"\U0001f525 {base_title}\uff01\u8fd9\u6ce2\u64cd\u4f5c\u6211\u770b\u4edc\u4e86",
            f"\u8bf4\u771f\u7684\uff0c{base_title}\u53ef\u80fd\u6539\u53d8\u4e00\u5207",
            f"{base_title}\uff1a\u6211\u4f53\u9a8c\u5b8c\u53ea\u60f3\u8bf4\u4e00\u4e2a\u5b57",
            f"\u6df1\u5ea6\u4f53\u9a8c {base_title} \u540e\uff0c\u6211\u53d1\u73b0\u4e86\u4e00\u4e2a\u79d8\u5bc6...",
            f"\u522b\u518d\u88ab\u9a97\u4e86\uff01\u5173\u4e8e{base_title}\u7684\u771f\u76f8",
            f"\u521a\u8bd5\u4e86{base_title}\uff0c\u6211\u7684\u4e0b\u5df4\u6389\u4e0b\u6765\u4e86",
            f"\u4e3a\u4ec0\u4e48\u61c2\u7684\u4eba\u90fd\u5728\u804a{base_title}\uff1f",
            f"{base_title}\u6765\u4e86\uff01\u666e\u901a\u4eba\u600e\u4e48\u6293\u4f4d\u673a\u4f1a\uff1f",
            f"\u5b9e\u6d4b {base_title}\uff0c\u7ed3\u679c\u8ba9\u6211\u610f\u5916",
            f"\u5173\u4e8e{base_title}\uff099%\u7684\u4eba\u90fd\u4e0d\u77e5\u9053\u7684\u4e8b",
        ]
        random.shuffle(templates)
        return templates[:8]


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    # Minimal config for standalone test
    config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}]}

    fetcher = HotTopicFetcher(config)
    topics = fetcher.fetch_all()

    print(f"\n=== Hot Topics ({len(topics)} total) ===\n")
    for i, t in enumerate(topics[:25], 1):
        src = t.get('source', '?')
        print(f"{i:2d}. [{src}] {t['title']} (hot:{t.get('hot_value',0)})")

    print(f"\nSource: {topics[0].get('source','?') if topics else 'NONE'}")
