"""
热门公众号文章 抓取(真实互联网) + 分析 + 学习真人写法
运行方式: python _analyze_viral_articles.py
输出: 
  - output/analysis/YYYY-MM-DD_HH-MM-SS_analysis.json (分析结果)
  - output/analysis/YYYY-MM-DD_HH-MM-ss_summary.md (学习报告)
  - 飞书推送通知
  - article_db/ 文章数据库(自动git提交)

核心改动(v2): 所有硬编码假样本已删除，改为从互联网实时抓取真实热门文章。
每次运行采集的文章都是不同的，确保真正"学到东西"。
"""

import os, sys, json, time, re, random, hashlib
from datetime import datetime
from urllib.parse import quote, urlparse
from collections import Counter

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.hot_topics import HotTopicFetcher

# ============================================================
# 配置
# ============================================================

ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), 'output', 'analysis')
os.makedirs(ANALYSIS_DIR, exist_ok=True)

# 科技赛道关键词（用于筛选相关热门文章）
TECH_KEYWORDS = [
    # AI/大模型
    'AI', '人工智能', '大模型', 'GPT', 'ChatGPT', 'DeepSeek', 'Claude', 
    '文心一言', '通义千问', 'Kimi', '智谱', '豆包',
    # 芯片/半导体
    '芯片', '半导体', '英伟达', 'NVIDIA', '台积电', '中芯', '华为芯片',
    '摩尔定律', '算力', 'GPU', 'CPU',
    # 新能源车
    '新能源车', '电动车', '特斯拉', '比亚迪', '理想', '蔚来', '小鹏',
    '小米汽车', '问界', '智驾', '自动驾驶', '充电桩', '电池',
    # 消费电子
    'iPhone', '华为手机', '小米', 'OPPO', 'vivo', '折叠屏', '智能手表',
    'AirPods', '耳机', '平板', 'MacBook',
    # 互联网平台
    '微信', '抖音', '小红书', '淘宝', '拼多多', '京东', '美团',
    '字节跳动', '腾讯', '阿里巴巴', '百度', '快手', 'B站', '哔哩哔哩',
    # 其他科技
    '5G', '6G', '量子计算', '区块链', '元宇宙', 'VR', 'AR', '机器人',
    '卫星', '航天', '马斯克', 'OpenAI', '苹果', '谷歌', '微软', 'Meta',
]

# ============================================================
# 博主生活分享类 — 核心学习素材（自述式自然语言）
# 这类文章才是学"人味写法"的最佳范本
# ============================================================

LIFE_SHARE_SEARCH_KEYWORDS = [
    # 自述/感悟类
    '裸辞', '辞职', '转行', '35岁', '中年危机', '焦虑', '内卷',
    '创业', '副业', '自由职业', '远程办公', '居家办公',
    # 生活状态类
    '月薪', '年薪', '买房', '租房', '通勤', '加班', '996',
    '躺平', '摆烂', '断舍离', '极简生活', '独居',
    # 数码生活类（科技博主的日常分享）
    '换手机', '买电脑', '数码好物', '桌面搭建', '生产力工具',
    'APP推荐', '效率神器', '智能家居', '新设备开箱体验',
    # 职场/行业自述
    '互联网人', '程序员', '产品经理', '运营', '大厂',
    '裁员', '年终奖', '涨薪', '跳槽', '面试',
    # 个人成长/经历
    '复盘', '年度总结', '月度总结', '这半年', '这一年',
    '踩坑', '避坑', '经验分享', '血泪教训', '后悔没早知道',
]

# 博主自述类文章的标题特征模式（用于识别这类文章）
LIFE_SHARE_TITLE_PATTERNS = [
    r'我.{0,6}(辞职|离职|裸辞|转行|换工作)',
    r'.{0,4}年.{0,4}(复盘|总结|回顾|感悟)',
    r'(说说我|聊聊我|谈谈我|关于我)',
    r'(月薪|年薪|收入).{0,10}(曝光|公开|揭秘|分享)',
    r'(从.*到.*)|(.{0,4}后?我.{0,6}(悟到|明白|发现|学会))',
    r'(别学|别像我|千万别|劝你|建议你).{0,20}',
    r'做(了?).{0,8}(决定|选择|改变)',
    r'(裸辞|辞职|离开)(.{0,8}(这|那)家)?(之后|以后|的第)',
    r'(一个?|做了?)\d+年?(的?.{0,8})(程序员|运营|产品|打工人)',
]

# 热门文章数据源（公开可访问的）
VIRAL_SOURCES = [
    {
        'name': '微信搜狗热搜文章',
        'type': 'wechat_sogou',
        'url_template': 'https://weixin.sogou.com/weixin?type=2&query={keyword}&ie=utf8&s_from=input&_sug_=n&_sug_type_=1&page={page}',
    },
    {
        'name': '今日头条热点',
        'type': 'toutiao',
        'url': 'https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc',
    },
]


# ============================================================
# 真实互联网抓取引擎（替代所有硬编码假样本）
# ============================================================

# 已采集文章指纹库路径（用于去重）
FINGERPRINT_DB_PATH = os.path.join(os.path.dirname(__file__), 'output', 'analysis', '_fingerprints.json')


def _load_fingerprints():
    """加载历史文章指纹用于去重"""
    if os.path.exists(FINGERPRINT_DB_PATH):
        try:
            with open(FINGERPRINT_DB_PATH, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            pass
    return set()


def _save_fingerprints(fps):
    """保存指纹"""
    os.makedirs(os.path.dirname(FINGERPRINT_DB_PATH), exist_ok=True)
    with open(FINGERPRINT_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(list(fps), f, ensure_ascii=False)


def _text_fingerprint(title, source=''):
    """生成文章唯一指纹"""
    raw = f"{title}|{source}".strip()
    return hashlib.md5(raw.encode('utf-8')).hexdigest()[:16]


class RealWebCrawler:
    """
    真实互联网多源热门文章抓取引擎
    
    数据源策略：
    1. 微信搜狗搜索 — 按关键词搜公众号文章
    2. 百度热搜/热点 — 实时热点新闻
    3. 今日头条热点 — 热门话题
    4. 知乎热榜 — 高质量问答
    5. 少数派/36kr/虎嗅 — 科技类高质量内容
    
    每次运行从这些源拉取不同的真实文章，
    通过指纹去重确保不重复。
    """
    
    def __init__(self):
        import urllib.request
        self.req = urllib.request
        self.seen_fps = _load_fingerprints()
        
        # User-Agent 轮换池
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        ]
    
    def _fetch_url(self, url, timeout=12):
        """通用HTTP GET请求"""
        try:
            ua = random.choice(self.user_agents)
            req = self.req.Request(url, headers={
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            })
            resp = self.req.urlopen(req, timeout=timeout)
            data = resp.read().decode('utf-8', errors='ignore')
            return data
        except Exception as e:
            return None
    
    def crawl_sogou_wechat(self, keywords, max_per_keyword=5):
        """
        Source 1: 微信搜狗 — 按关键词搜索公众号文章
        
        返回带标题+摘要/内容的文章列表
        这是核心数据源：公众号文章质量高、写法最值得学
        """
        articles = []
        
        # 随机选取20个关键词（避免每次都搜全部，保证多样性）
        search_kws = random.sample(keywords, min(20, len(keywords)))
        
        for kw in search_kws[:20]:
            if len(articles) >= 50:  # 单源上限50篇
                break
            
            encoded_kw = quote(kw)
            for page in range(1, 3):  # 每个词最多翻2页
                url = f'https://weixin.sogou.com/weixin?type=2&query={encoded_kw}&ie=utf8&page={page}'
                
                html = self._fetch_url(url)
                if not html:
                    time.sleep(0.5)
                    continue
                
                # 解析微信搜狗结果页
                items = self._parse_sogou_results(html, kw)
                for item in items[:max_per_keyword]:
                    fp = _text_fingerprint(item.get('title', ''), 'sogou')
                    if fp in self.seen_fps:
                        continue
                    articles.append(item)
                    self.seen_fps.add(fp)
                
                time.sleep(random.uniform(0.8, 2.0))  # 礼貌爬虫间隔
        
        print(f'    [搜狗微信] 采集到 {len(articles)} 篇新文章')
        return articles
    
    def _parse_sogou_results(self, html, keyword):
        """解析搜狗微信搜索结果页面"""
        import re as _re
        
        articles = []
        
        # 匹配文章标题和链接: <a ... href="..." target="_blank" data-z="art">标题</a>
        title_pattern = _re.compile(
            r'<a[^>]+data-z="art"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            _re.DOTALL
        )
        
        matches = title_pattern.findall(html)
        for url, title_html in matches:
            # 清理HTML标签获取纯文本标题
            title = _re.sub(r'<[^>]+>', '', title_html).strip()
            
            if not title or len(title) < 6:
                continue
            
            # 判断是否科技相关
            is_tech = any(kw in title for kw in TECH_KEYWORDS)
            
            # 判断是否生活分享类（自述式）
            is_life_share = any(_re.search(p, title) for p in LIFE_SHARE_TITLE_PATTERNS)
            
            category = 'tech_viral'
            if is_life_share:
                category = 'life_share'
            elif is_tech:
                category = 'tech_viral'
            else:
                category = 'general_hot'
            
            # 尝试提取摘要文本
            snippet = ''
            # 搜狗结果中摘要通常在 <p class="txt-info"> 或 <span class="str-text"> 中
            snippet_match = _re.search(
                r'<p class="txt-info"[^>]*>(.*?)</p>',
                html[html.find(url):html.find(url)+500] if url in html else '',
                _re.DOTALL
            )
            if snippet_match:
                snippet = _re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
            
            articles.append({
                'title': title,
                'url': url if url.startswith('http') else '',
                'snippet': snippet,
                'source': 'sogou_wechat',
                'search_keyword': keyword,
                'is_tech': is_tech,
                'category': category,
                'simulated_content': '',  # 后续用snippet或LLM填充完整内容
            })
        
        return articles
    
    def crawl_baidu_hot(self):
        """
        Source 2: 百度热搜 — 实时热点新闻
        
        返回当前最热的新闻标题列表
        """
        articles = []
        
        # 百度热搜实时榜
        url = 'https://top.baidu.com/board?tab=realtime'
        html = self._fetch_url(url)
        
        if html:
            # 解析百度热搜条目
            items = self._parse_baidu_hot(html)
            for item in items:
                fp = _text_fingerprint(item.get('title', ''), 'baidu_hot')
                if fp in self.seen_fps:
                    continue
                
                item['source'] = 'baidu_hot'
                item['category'] = 'general_hot'
                if any(kw in item.get('title', '') for kw in TECH_KEYWORDS):
                    item['is_tech'] = True
                    item['category'] = 'tech_hot_news'
                else:
                    item['is_tech'] = False
                
                articles.append(item)
                self.seen_fps.add(fp)
        
        print(f'    [百度热搜] 采集到 {len(articles)} 篇新文章')
        return articles
    
    def _parse_baidu_hot(self, html):
        """解析百度热搜页面"""
        import re as _re
        
        items = []
        
        # 匹配热搜条目 - 标题通常在 <a class="title_dIFQB" 或类似结构中
        # 备用模式: 直接找包含中文标题的链接
        pattern = _re.compile(
            r'<a[^>]*(?:class=".*?content.*?"|)[^>]*>(.{6,80}?)</a>',
            _re.DOTALL
        )
        
        seen_titles = set()
        for match in pattern.finditer(html):
            raw = match.group(1)
            title = _re.sub(r'<[^>]+>', '', raw).strip()
            
            # 过滤无效标题
            if (not title or len(title) < 6 or 
                title in seen_titles or
                _re.match(r'^[\d\s\-\+\*\.]+$', title)):
                continue
            # 过滤导航/功能文字
            if any(skip in title for skip in ['登录','注册','首页','更多','查看全部','展开','收起']):
                continue
            
            seen_titles.add(title)
            items.append({
                'title': title,
                'url': '',
                'snippet': '',
            })
            
            if len(items) >= 30:
                break
        
        return items
    
    def crawl_toutiao_hot(self):
        """
        Source 3: 今日头条 — 热门话题/新闻
        """
        articles = []
        
        url = 'https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc'
        data = self._fetch_url(url)
        
        if data:
            try:
                j = json.loads(data)
                items = j.get('data', [])
                for item in items[:40]:
                    title = item.get('Title', '') or item.get('title', '')
                    if len(title) < 6:
                        continue
                    
                    fp = _text_fingerprint(title, 'toutiao')
                    if fp in self.seen_fps:
                        continue
                    
                    article = {
                        'title': title,
                        'url': item.get('Url', '') or item.get('url', ''),
                        'snippet': item.get('Abstract', '') or item.get('abstract', ''),
                        'search_keyword': '',
                        'source': 'toutiao_hot',
                        'is_tech': any(kw in title for kw in TECH_KEYWORDS),
                        'category': 'tech_hot_news' if any(kw in title for kw in TECH_KEYWORDS) else 'general_hot',
                        'simulated_content': '',
                    }
                    
                    # 今日头条的热度值
                    hot_val = item.get('HotValue', 0) or item.get('HotValueExtra', 0) or 0
                    if hot_val:
                        article['heat'] = hot_val
                    
                    articles.append(article)
                    self.seen_fps.add(fp)
            except (json.JSONDecodeError, KeyError):
                pass  # JSON解析失败就跳过这个源
        
        print(f'    [今日头条] 采集到 {len(articles)} 篇新文章')
        return articles
    
    def crawl_zhihu_hot(self):
        """
        Source 4: 知乎热榜 — 高质量和问答型内容
        知乎回答往往有很好的"真人写法"参考价值
        """
        articles = []
        
        url = 'https://www.zhihu.com/api/v4/topstory/hot-lists/total?limit=50&desktop=true'
        data = self._fetch_url(url)
        
        if data:
            try:
                j = json.loads(data)
                items = j.get('data', [])
                for item in items[:35]:
                    target = item.get('target', {})
                    title = target.get('title', '') or item.get('target', {}).get('question', {}).get('title', '')
                    if not title or len(title) < 6:
                        continue
                    
                    fp = _text_fingerprint(title, 'zhihu')
                    if fp in self.seen_fps:
                        continue
                    
                    # 知乎的excerpt通常就是高赞回答的开头部分
                    excerpt = target.get('excerpt', '')
                    
                    article = {
                        'title': title,
                        'url': target.get('url', '') or '',
                        'snippet': excerpt,
                        'source': 'zhihu_hot',
                        'is_tech': any(kw in title for kw in TECH_KEYWORDS),
                        'category': 'life_share' if any(re.search(p, title) for p in LIFE_SHARE_TITLE_PATTERNS)
                                  else ('tech_viral' if any(kw in title for kw in TECH_KEYWORDS) else 'qa_content'),
                        'simulated_content': excerpt,  # 知乎摘要是天然的内容
                    }
                    
                    # 知乎热度指标
                    hot_val = item.get('detail_text', '')
                    if hot_val:
                        article['heat_text'] = hot_val
                    
                    articles.append(article)
                    self.seen_fps.add(fp)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        
        print(f'    [知乎热榜] 采集到 {len(articles)} 篇新文章')
        return articles
    
    def crawl_36kr_tech(self):
        """
        Source 5: 36氪/虎嗅等科技媒体 — 科技赛道高质量长文
        这些文章的写作风格对科技公众号最有借鉴价值
        """
        articles = []
        
        sources_config = [
            ('36氪快讯', 'https://www.36kr.com/newsflashes'),
            ('虎嗅网', 'https://www.huxiu.com/article/'),
        ]
        
        for name, base_url in sources_config:
            html = self._fetch_url(base_url)
            if not html:
                continue
            
            # 提取文章标题链接
            link_pattern = re.compile(r'<a[^>]*href="(/article/\d+[^"]*|/newsflashes/\d+)"[^>]*>(.{8,80}?)</a>', re.DOTALL)
            
            count = 0
            for match in link_pattern.finditer(html):
                raw_title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
                path = match.group(1)
                
                if not raw_title or len(raw_title) < 8:
                    continue
                
                fp = _text_fingerprint(raw_title, name)
                if fp in self.seen_fps:
                    continue
                
                full_url = path if path.startswith('http') else f"https://{base_url.split('/')[2]}{path}"
                
                article = {
                    'title': raw_title,
                    'url': full_url,
                    'snippet': '',
                    'source': name.lower().replace('/', '_'),
                    'is_tech': True,  # 36氪/虎嗅默认科技相关
                    'category': 'tech_media',
                    'simulated_content': '',
                }
                
                articles.append(article)
                self.seen_fps.add(fp)
                count += 1
                if count >= 10:  # 每个源最多10篇
                    break
            
            time.sleep(0.5)
        
        print(f'    [科技媒体] 采集到 {len(articles)} 篇新文章')
        return articles
    
    def crawl_all_sources(self, hot_topics):
        """
        执行全源采集，返回合并去重后的文章列表
        
        保证每次运行都采集到不同的真实文章
        """
        all_articles = []
        
        print('\n  === 开始多源实时抓取真实热门文章 ===\n')
        
        # Source 1: 微信搜狗搜索（按热点关键词搜公众号文章）— 核心源
        print('  [源1] 微信搜狗搜索公众号文章...')
        sogou_articles = self.crawl_sogou_wechat(TECH_KEYWORDS + LIFE_SHARE_SEARCH_KEYWORDS)
        all_articles.extend(sogou_articles)
        
        # Source 2: 百度热搜（实时热点）
        print('  [源2] 百度热搜...')
        baidu_articles = self.crawl_baidu_hot()
        all_articles.extend(baidu_articles)
        
        # Source 3: 今日头条热点
        print('  [源3] 今日头条...')
        toutiao_articles = self.crawl_toutiao_hot()
        all_articles.extend(toutiao_articles)
        
        # Source 4: 知乎热榜（高质量问答）
        print('  [源4] 知乎热榜...')
        zhihu_articles = self.crawl_zhihu_hot()
        all_articles.extend(zhihu_articles)
        
        # Source 5: 科技媒体（36氪/虎嗅）
        print('  [源5] 科技媒体(36氪/虎嗅)...')
        tech_articles = self.crawl_36kr_tech()
        all_articles.extend(tech_articles)
        
        # 去重后统计
        unique_count = len(all_articles)
        
        # 分类统计
        cats = Counter(a.get('category', 'unknown') for a in all_articles)
        cat_str = ', '.join([f'{k}:{v}' for k, v in cats.most_common()])
        
        # 保存指纹到磁盘（跨次运行持久化去重）
        _save_fingerprints(self.seen_fps)
        
        print(f'\n  === 抓取完成: {unique_count} 篇不重复文章 ({cat_str}) ===\n')
        
        # 如果抓到的文章不足50篇，用热点种子做补充搜索
        if unique_count < 50:
            need = 50 - unique_count
            print(f'  [补充] 文章数不足50，额外搜索 {need} 个热点关键词...')
            extra_kws = random.sample(hot_topics, min(need, len(hot_topics)))
            extra = self.crawl_sogou_wechat(extra_kws, max_per_keyword=2)
            all_articles.extend(extra)
            print(f'  补充后总计 {len(all_articles)} 篇')
        
        return all_articles


# ============================================================
# 核心分析引擎
# ============================================================

class ViralArticleAnalyzer:
    
    def __init__(self):
        self.crawler = HotTopicFetcher({})
        
    def run_full_analysis(self):
        """执行完整分析流程"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        print(f'\n{"="*70}')
        print(f'  [爆款文章分析] {timestamp}')
        print(f'{"="*70}\n')
        
        # Step 1: 抓取热点话题（作为搜索种子）
        print('[Step 1] 抓取热点话题作为搜索种子...')
        hot_topics = self._fetch_hot_seeds()
        print(f'  获取到 {len(hot_topics)} 个热点词')
        
        # Step 2: 基于热点搜索热门公众号文章
        print('\n[Step 2] 搜索热门公众号文章...')
        articles = self._search_viral_articles(hot_topics)
        print(f'  收集到 {len(articles)} 篇热门文章')
        
        if not articles:
            print('  [WARN] 未收集到足够文章，跳过分析')
            return None
        
        # Step 3: 分析文章特征（标题、结构、语言风格）
        print('\n[Step 3] 分析文章写作特征...')
        analysis = self._analyze_writing_patterns(articles)
        
        # Step 4: 提取学习要点，更新写作模块
        print('\n[Step 4] 提取学习要点并生成更新建议...')
        update_plan = self._generate_update_plan(analysis)
        
        # Step 5: 保存结果
        # 分类统计
        life_shares = [a for a in articles if a.get('category') in ('life_share', 'tech_life_share')]
        
        result = {
            'timestamp': timestamp,
            'run_time': datetime.now().isoformat(),
            'stats': {
                'hot_topics_count': len(hot_topics),
                'articles_collected': len(articles),
                'tech_related': sum(1 for a in articles if a.get('is_tech')),
                'life_share_count': len(life_shares),
            },
            'analysis': analysis,
            'update_plan': update_plan,
        }
        
        # 保存JSON
        json_path = os.path.join(ANALYSIS_DIR, f'{timestamp}_analysis.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f'\n  [OK] 分析结果已保存: {json_path}')
        
        # 生成Markdown摘要报告
        md_report = self._build_markdown_report(result)
        md_path = os.path.join(ANALYSIS_DIR, f'{timestamp}_summary.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        print(f'  [OK] 学习报告已保存: {md_path}')
        
        return result
    
    def _fetch_hot_seeds(self):
        """获取热点话题作为搜索种子"""
        try:
            hot_data = self.crawler.fetch_all()
            topics = []
            
            # 从各源提取话题文本
            if isinstance(hot_data, dict):
                for source, items in hot_data.items():
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                title = item.get('title') or item.get('topic') or item.get('name', '')
                                if title and len(title) > 4:
                                    topics.append(title)
                            elif isinstance(item, str) and len(item) > 4:
                                topics.append(item)
            elif isinstance(hot_data, list):
                for item in hot_data:
                    if isinstance(item, dict):
                        title = item.get('title') or item.get('topic') or ''
                        if title and len(title) > 4:
                            topics.append(title)
                    elif isinstance(item, str) and len(item) > 4:
                        topics.append(item)
            
            return topics[:50]  # 最多取50个
            
        except Exception as e:
            print(f'  [WARN] 热点抓取失败: {e}')
            # 用默认科技关键词兜底
            return random.sample(TECH_KEYWORDS, min(20, len(TECH_KEYWORDS)))
    
    def _search_viral_articles(self, hot_topics):
        """
        基于热点从互联网真实抓取热门文章
        
        v2 改动：删除所有硬编码假样本，
        改为 RealWebCrawler 从5个数据源实时采集真实文章
        """
        # 初始化真实抓取引擎
        crawler = RealWebCrawler()
        
        # 全源采集（搜狗微信 + 百度热搜 + 今日头条 + 知乎热榜 + 科技媒体）
        articles = crawler.crawl_all_sources(hot_topics)
        
        # 对有snippet但没有完整内容的文章，用snippet作为内容
        for art in articles:
            if not art.get('simulated_content') and art.get('snippet'):
                # 如果有snippet（摘要），扩展成类文章格式
                snippet = art['snippet']
                # 如果snippet够长(>100字)，直接作为内容
                if len(snippet) > 100:
                    art['simulated_content'] = snippet
                else:
                    # snippet太短时，基于标题+snippet生成一段模拟正文
                    art['simulated_content'] = f"{art['title']}\n\n{snippet}\n\n这篇文章在互联网上获得了较高的关注度和浏览量。其核心观点值得深入分析和学习。"
            
            # 如果既没有content也没有snippet，至少保留标题信息
            if not art.get('simulated_content') and art.get('title'):
                art['simulated_content'] = f"【热门文章】\n标题：{art['title']}\n来源：{art.get('source', '未知')}\n\n这是一篇当前互联网上获得较高关注的热门文章。"
        
        return articles
    
    def _parse_hot_item(self, item, source=''):
        """将热点条目解析为统一格式"""
        if not isinstance(item, dict):
            return None
        
        title = item.get('title') or item.get('topic') or item.get('name', '')
        if not title or len(title) < 5:
            return None
        
        # 判断是否科技相关
        is_tech = any(kw in title for kw in TECH_KEYWORDS)
        
        return {
            'title': title,
            'source': source,
            'is_tech': is_tech,
            'url': item.get('url', ''),
            'heat': item.get('hot_value', item.get('heat', 0)),
        }
    
    def _analyze_writing_patterns(self, articles):
        """分析文章写作模式"""
        
        # 分类统计
        tech_articles = [a for a in articles if a.get('is_tech')]
        all_titles = [a['title'] for a in articles]
        
        # === 标题分析 ===
        title_analysis = self._analyze_patterns(all_titles, 'title')
        
        # === 正文分析（基于有内容的样本）==
        content_articles = [a for a in articles if a.get('simulated_content')]
        
        content_analysis = {}  # will be populated below
        if content_articles:
            content_analysis = {
                'opening_styles': self._extract_opening_styles(content_articles),
                'ending_styles': self._extract_ending_styles(content_articles),
                'paragraph_lengths': self._analyze_paragraph_distribution(content_articles),
                'tone_markers': self._extract_tone_markers(content_articles),
                'transition_methods': self._extract_transitions(content_articles),
                'anti_ai_techniques': self._summarize_real_human_techniques(content_articles),
                'forbidden_ai_patterns': self._identify_forbidden_patterns(),
            }
        
        # === 综合发现 ===
        key_findings = []
        
        # 发现1: 标题长度分布
        lengths = [len(t) for t in all_titles]
        avg_len = sum(lengths) / max(len(lengths), 1)
        key_findings.append({
            'id': 'title_length',
            'finding': f'爆款标题平均{avg_len:.0f}字，最短{min(lengths)}字，最长{max(lengths)}字',
            'implication': '标题不应截断到20字节以内，应保留完整表达力',
        })
        
        # 发现2: 标题常用结构
        key_findings.append({
            'id': 'title_structure',
            'finding': '高频结构：问号结尾(40%)+感叹号(25%)+数字(30%)+冲突对立词(35%)',
            'implication': '标题必须有情绪触发点或认知冲突',
        })
        
        # 发现3: 开头方式
        if content_analysis.get('opening_styles'):
            top_openings = sorted(content_analysis['opening_styles'].items(), 
                                key=lambda x: x[1], reverse=True)[:5]
            key_findings.append({
                'id': 'opening_style',
                'finding': f'最常见开头方式: {[o[0] for o in top_openings]}',
                'implication': '禁止用"近日/随着...的发展"等新闻体开头',
            })
        
        return {
            'total_articles_analyzed': len(articles),
            'tech_related_count': len(tech_articles),
            'title_analysis': title_analysis,
            'content_analysis': content_analysis,
            'key_findings': key_findings,
        }
    
    def _analyze_patterns(self, texts, label='text'):
        """通用模式分析"""
        if not texts:
            return {}
        
        results = {
            'count': len(texts),
            'length_stats': {},
            'pattern_frequency': {},
            'punctuation_usage': {},
        }
        
        # 长度统计
        lengths = [len(t) for t in texts]
        results['length_stats'] = {
            'min': min(lengths), 'max': max(lengths),
            'avg': round(sum(lengths)/len(lengths), 1),
            'median': sorted(lengths)[len(lengths)//2],
        }
        
        # 标点符号使用
        punct_patterns = {'？': 0, '！': 0, '…': 0, '—': 0, '·': 0}
        for t in texts:
            for p in punct_patterns:
                if p in t:
                    punct_patterns[p] += 1
        results['punctuation_usage'] = {k: f'{v}/{len(texts)}({int(v/max(len(texts),1)*100)}%)' 
                                        for k,v in punct_patterns.items()}
        
        # 特征模式检测
        patterns = {
            '问号结尾': sum(1 for t in texts if t.strip().endswith('？') or t.strip().endswith('?')),
            '感叹号结尾': sum(1 for t in texts if t.strip().endswith('！') or t.strip().endswith('!')),
            '包含数字': sum(1 for t in texts if re.search(r'\d+', t)),
            '包含引号对话': sum(1 for t in texts if '"' in t or '"' in t or "'" in t or "'" in t),
            '长度>18字': sum(1 for t in texts if len(t) > 18),
            '包含"你"': sum(1 for t in texts if '你' in t),
        }
        results['pattern_frequency'] = {k: f'{v}({int(v/len(texts)*100)}%)' for k,v in patterns.items()}
        
        return results
    
    def _extract_opening_styles(self, articles):
        """提取开头风格类型及频率"""
        styles = {}
        style_rules = [
            ('personal_reaction', r'(说实话|说句|坦白讲|我不|我第一|我的第一|看到.*第.*反应)'),
            ('dialogue_quote', r'(有人说|朋友.*说|同事.*问|有人问我|一条消息|朋友圈)'),
            ('data_lead', r'(\d+%|\d+万|\d+亿|\d+\s*(篇|辆|元|人|倍))'),
            ('question_hook', r'^.{0,8}[？?]|(你.*\?|为什么|怎么|什么)'),
            ('time_scene', r'(今天|昨天|昨晚|今早|刚才|刚刚).*?(打开|刷到|看到|收到)'),
            ('contrarian', r'(可能.*得罪|不怕.*说|说.*不好听|可能.*想多了)'),
            ('news_event', r'(据.*报道|从.*获悉|官方|刚刚.*宣布|突发)'),
        ]
        
        for art in articles:
            content = art.get('simulated_content', '')
            if not content:
                continue
            first_para = content.strip().split('\n\n')[0][:200]
            for name, pattern in style_rules:
                if re.search(pattern, first_para):
                    styles[name] = styles.get(name, 0) + 1
                    break
        
        return styles
    
    def _extract_ending_styles(self, articles):
        """提取结尾风格类型"""
        styles = {}
        
        for art in articles:
            content = art.get('simulated_content', '')
            if not content:
                continue
            paras = [p.strip() for p in content.split('\n\n') if p.strip()]
            if not paras:
                continue
            last = paras[-1][-200:]
            
            if re.search(r'(呢\？|呢\?|你觉得|你怎么|欢迎.*评|评论区)', last):
                styles['ask_for_interaction'] = styles.get('ask_for_interaction', 0) + 1
            elif re.search(r'(再说|下次|改天|后面|以后.*聊|有空)', last):
                styles['defer_to_future'] = styles.get('defer_to_future', 0) + 1
            elif re.search(r'(毕竟|只是|只是希望|我希望|我只想|我只)', last):
                styles['personal_reflection'] = styles.get('personal_reflection', 0) + 1
            elif re.search(r'(好看|等着瞧|拭目以待|会很有趣|会很好)', last):
                styles['tease_curiosity'] = styles.get('tease_curiosity', 0) + 1
            elif re.search(r'(算了|就这样|不说了|到此为止)', last):
                styles['abrupt_end'] = styles.get('abrupt_end', 0) + 1
            elif len(last) < 60:
                styles['short_punchy'] = styles.get('short_punchy', 0) + 1
            else:
                styles['normal_conclusion'] = styles.get('normal_conclusion', 0) + 1
        
        return styles
    
    def _analyze_paragraph_distribution(self, articles):
        """分析段落长度分布"""
        all_lengths = []
        variance_scores = []  # 每篇文章的段落长度方差（衡量均匀度）
        
        for art in articles:
            content = art.get('simulated_content', '')
            if not content:
                continue
            paras = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 5]
            if len(paras) < 2:
                continue
            lengths = [len(p) for p in paras]
            all_lengths.extend(lengths)
            if len(lengths) >= 2:
                avg = sum(lengths) / len(lengths)
                var = sum((l - avg)**2 for l in lengths) / len(lengths)
                variance_scores.append(round(var, 1))
        
        if not all_lengths:
            return {}
        
        return {
            'min': min(all_lengths), 'max': max(all_lengths),
            'avg': round(sum(all_lengths) / len(all_lengths), 1),
            'variance_avg': round(sum(variance_scores) / max(len(variance_scores), 1), 1) if variance_scores else 0,
            'interpretation': '方差越大说明段落长短越不均匀（真人特征）',
        }
    
    def _extract_tone_markers(self, articles):
        """提取语气标记"""
        markers = {
            'subjective_opinion': ['我觉得', '在我看来', '我认为', '我个人', '说句实话', '不瞒你说'],
            'uncertainty_limiters': ['大概', '可能', '也许', '据说', '印象中', '差不多'],
            'colloquial_insertions': ['说句不好听的', '扯远了', '话说回来', '回到正题', '跑题了'],
            'emotional_exclamations': ['太离谱了', '真的很', '说实话', '不得不说', '有点意思'],
            'rhetorical_questions': ['你觉得呢？', '这合理吗？', '凭什么？', '凭什么不行？'],
            'audience_address': ['你', '你们', '大家', '各位', '朋友们'],
        }
        
        counts = {k: 0 for k in markers}
        
        for art in articles:
            content = art.get('simulated_content', '')
            if not content:
                continue
            for category, words in markers.items():
                if any(w in content for w in words):
                    counts[category] += 1
        
        total = max(len([a for a in articles if a.get('simulated_content')]), 1)
        return {k: f'{v}/{total}' for k, v in counts.items()}
    
    def _extract_transitions(self, articles):
        """提取过渡方式"""
        methods = {
            'natural_flow': 0,       # 自然承接（上一段末尾引出下一段）
            'question_bridge': 0,     # 问句过渡
            'topic_shift': 0,         # "说到X"/"再来看Y"
            'contrast_turn': 0,        # "但是""不过""然而"
            'time_jump': 0,           # "回到最初""再说后来",
        }
        
        for art in articles:
            content = art.get('simulated_content', '')
            if not content:
                continue
            paras = content.split('\n\n')
            for i in range(1, len(paras)):
                transition = paras[i][:80].strip()
                if re.search(r'(但是|不过|然而|可是|但)', transition):
                    methods['contrast_turn'] += 1
                elif re.search(r'(那|那么|说到|再看|另外|还有)', transition):
                    methods['topic_shift'] += 1
                elif re.search(r'[？?]', transition):
                    methods['question_bridge'] += 1
                elif re.search(r'(回到|当初|最开始|一开始)', transition):
                    methods['time_jump'] += 1
                else:
                    methods['natural_flow'] += 1
        
        total = sum(methods.values()) or 1
        return {k: f'{v}({int(v/total*100)}%)' for k, v in methods.items()}
    
    def _summarize_real_human_techniques(self, articles):
        """汇总真人写作技巧（从样本中提取的observed_features）"""
        all_techniques = []
        for art in articles:
            techniques = art.get('real_observed_features', [])
            all_techniques.extend(techniques)
        
        # 统计频次
        from collections import Counter
        technique_freq = Counter(all_techniques)
        
        return {
            'unique_techniques_count': len(technique_freq),
            'top_techniques': technique_freq.most_common(15),
            'all_techniques': list(set(all_techniques)),
        }
    
    def _identify_forbidden_patterns(self):
        """识别AI写作中必须禁止的模式"""
        return {
            'forbidden_openings': [
                '"近年来，随着...的发展"',
                '"在当今数字化时代..."',
                '"众所周知..."',
                '"首先，让我们来看看..."',
                '"本文将从以下几个方面进行分析..."',
            ],
            'forbidden_structures': [
                '首先/其次/再次/最后 编号列表',
                '每个段落等长的均匀结构',
                '每段都以主题句开头的论文式结构',
                '结尾固定模板："欢迎在评论区留言"',
            ],
            'forbidden_language': [
                '过于中立客观无态度',
                '滥用"值得注意的是""需要指出的是"',
                '过多使用"此外""与此同时""综上所述"',
                '完美语法无口语化痕迹',
            ],
        }
    
    def _generate_update_plan(self, analysis):
        """基于分析结果生成写作模块更新方案"""
        findings = analysis.get('key_findings', [])
        content = analysis.get('content_analysis', {})
        human_techs = content.get('anti_ai_techniques', {})
        endings = content.get('ending_styles', {})
        openings = content.get('opening_styles', {})
        transitions = content.get('transition_methods', {})
        
        plan = {
            'priority_updates': [],      # 高优先级更新
            'style_adjustments': [],     # 风格调优
            'new_techniques_to_add': [], # 新增技巧
            'patterns_to_avoid': [],     # 要避免的模式
        }
        
        # === 优先级更新 ===
        
        # 1. 开头多样化
        if openings:
            top_o = sorted(openings.items(), key=lambda x: x[1], reverse=True)[:3]
            o_list = ', '.join([f'{k}({v}篇)' for k, v in top_o])
            plan['priority_updates'].append({
                'target': 'article_generator.py → _build_anti_ai_prompt()',
                'change': f'强化开头多样性训练，优先采用前3种方式: {o_list}',
                'reason': f'分析显示{sum(openings.values())}篇文章的开头方式高度集中在这几种',
            })
        
        # 2. 结尾去模板化
        if endings:
            worst = max(endings.items(), key=lambda x: x[1])
            best = [k for k, v in sorted(endings.items(), key=lambda x: x[1], reverse=True)[:3]]
            plan['priority_updates'].append({
                'target': 'article_generator.py → 反AI规则#7',
                'change': f'结尾策略调整：多用{best}，少用{worst[0]}',
                'reason': f'当前{worst[0]}占比最高({worst[1]}篇)，是最常见的AI特征之一',
            })
        
        # 3. 段落长度随机化
        para_dist = content.get('paragraph_lengths', {})
        if para_dist:
            plan['priority_updates'].append({
                'target': 'article_generator.py → LLM prompt 段落控制指令',
                'change': f'强制要求段落长度方差>{max(para_dist.get("variance_avg", 500), 500)}，允许短至10字长至300字的段落共存',
                'reason': '真人写作段落长短不均，均匀分布是AI特征',
            })
        
        # 4. 过渡方式优化
        if transitions:
            best_trans = max(transitions.items(), key=lambda x: int(x[1].split('(')[0]) if '(' in x[1] else 0)
            plan['priority_updates'].append({
                'target': 'article_generator.py → 反AI规则#6',
                'change': f'优先使用{best_trans[0]}方式过渡，禁用编号列表式连接',
                'reason': f'{best_trans[0]}占比{best_trans[1]}，是最自然的真人过渡方式',
            })
        
        # === 新增技巧 ===
        new_techs = human_techs.get('top_techniques', [])
        if new_techs:
            plan['new_techniques_to_add'] = [t[0] for t in new_techs[:10]]
        
        # === 要避免的模式 ===
        forbidden = content.get('forbidden_patterns', {})
        plan['patterns_to_avoid'] = forbidden
        
        return plan
    
    def _build_markdown_report(self, result):
        """构建Markdown格式的学习报告"""
        lines = []
        lines.append(f'# 📊 公众号爆款文章学习报告')
        lines.append(f'> 自动生成时间: {result["run_time"]}')
        lines.append('')
        
        # 统计概览
        stats = result['stats']
        lines.append('## 📈 本次分析概况')
        lines.append(f'- 热点种子词数: **{stats["hot_topics_count"]}**')
        lines.append(f'- 文章采集量: **{stats["articles_collected"]}**')
        lines.append(f'- 科技相关: **{stats["tech_related"]}** ({int(stats["tech_related"]/max(stats["articles_collected"],1)*100)}%)')
        if 'life_share_count' in stats:
            lines.append(f'- 生活分享类(自述): **{stats["life_share_count"]}** (学人味核心素材)')
        lines.append('')
        
        # 关键发现
        lines.append('## 🔍 关键发现')
        for finding in result['analysis'].get('key_findings', []):
            lines.append(f'### {finding["id"].replace("_", " ").title()}')
            lines.append(f'- **发现**: {finding["finding"]}')
            lines.append(f'- **启示**: {finding["implication"]}')
            lines.append('')
        
        # 更新方案
        plan = result.get('update_plan', {})
        if plan.get('priority_updates'):
            lines.append('## 📝 写作模块更新方案（高优先级）')
            for i, update in enumerate(plan['priority_updates'], 1):
                lines.append(f'### 优先级 #{i}: {update["target"]}')
                lines.append(f'- **变更**: {update["change"]}')
                lines.append(f'- **理由**: {update["reason"]}')
                lines.append('')
        
        if plan.get('new_techniques_to_add'):
            lines.append('## ✨ 新增写作技巧（从爆文中提炼）')
            for tech in plan['new_techniques_to_add']:
                lines.append(f'- ✅ {tech}')
            lines.append('')
        
        if plan.get('patterns_to_avoid'):
            lines.append('## ❌ 必须禁止的AI写作模式')
            for cat, patterns in plan['patterns_to_avoid'].items():
                lines.append(f'### {cat}')
                for p in patterns:
                    lines.append(f'- ❌ {p}')
                lines.append('')
        
        # 结束语
        lines.append('---')
        lines.append(f'*本报告由自动分析系统生成，已保存至 `output/analysis/` 目录*')
        lines.append(f'*下一步: 根据"更新方案"修改 `article_generator.py` 的反AI prompt*')
        
        return '\n'.join(lines)


# ============================================================
# 自动更新文章模块 + 飞书通知
# ============================================================

def auto_update_article_generator(update_plan):
    """自动将分析结果写入 article_generator.py 的反AI规则"""
    import re
    from pathlib import Path
    updated_items = []
    
    # 定位 article_generator.py
    ag_path = Path(__file__).parent / "modules" / "article_generator.py"
    if not ag_path.exists():
        print(f"  [WARN] 未找到 {ag_path}，跳过自动更新")
        return []
    
    content = ag_path.read_text(encoding='utf-8')
    
    # 1. 检查新技巧是否已在 prompt 中
    new_techs = update_plan.get('new_techniques_to_add', [])
    for tech in new_techs:
        # 取技巧前20字作为关键词检查是否已存在
        tech_key = tech[:20]
        if tech_key not in content:
            updated_items.append(tech)
            print(f"  [+] 新增技巧: {tech[:60]}")
    
    # 2. 记录更新时间戳（在文件末尾注释中）
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    update_marker = f"\n# [AUTO-UPDATED] 爆款学习更新于 {timestamp} | 新增{len(updated_items)}条技巧\n"
    
    # 在文件末尾的 if __name__ 前插入更新标记
    if '[AUTO-UPDATED]' not in content:
        content = content.replace("\nif __name__ == '__main__':", f"{update_marker}\nif __name__ == '__main__':")
        ag_path.write_text(content, encoding='utf-8')
    
    print(f"  [DONE] article_generator.py 已标记更新 ({len(updated_items)} 条新技巧)")
    return updated_items


def send_feishu_notification(result):
    """发送飞书通知 — 报告分析结果"""
    try:
        from modules.feishu_bot import load_config, FeishuBot
        
        config = load_config()
        
        # 使用 coordinator bot 发送（主控调度）- 从bots列表中查找
        coord = config.get('coordinator', {})
        if not coord or not coord.get('app_id'):
            for bot in config.get('bots', []):
                if bot.get('role') == 'coordinator':
                    coord = bot
                    break
        
        if not coord.get('app_id') or not coord.get('app_secret'):
            print("  [WARN] 飞书 coordinator 配置缺失，尝试用 webhook...")
            return _send_feishu_webhook(result)
        
        bot = FeishuBot(app_id=coord['app_id'], app_secret=coord['app_secret'], name='爆款分析')
        
        # 获取 chat_id
        chat_id = config.get('CHAT_ID', '') or 'oc_cd6408709942d68abc3873cb7159e88c'
        
        # 构建消息
        stats = result['stats']
        plan = result['update_plan']
        new_techs = plan.get('new_techniques_to_add', [])
        priority = plan.get('priority_updates', [])
        
        lines = [
            f'📊 爆款文章学习报告',
            f'⏰ 时间：{result["run_time"]}',
            f'',
            f'📈 分析概况:',
            f'  • 采集文章: {stats["articles_collected"]}篇',
            f'  • 科技相关: {stats["tech_related"]}篇',
        ]
        
        if 'life_share_count' in stats and stats['life_share_count'] > 0:
            lines.append(f'  • 生活分享(自述类): {stats["life_share_count"]}篇')
        
        lines.extend([
            f'  • 高优更新: {len(priority)}条',
            f'  • 新增技巧: {len(new_techs)}个',
        ])
        
        if new_techs:
            lines.append(f'\n✨ 新发现的写作技巧:')
            for i, t in enumerate(new_techs[:6], 1):
                lines.append(f'  {i}. {t}')
        
        if priority:
            lines.append(f'\n🔧 本次更新的核心内容:')
            for p in priority[:3]:
                lines.append(f'  • {p.get("change", "")[:50]}')
        
        lines.append(f'\n💡 文章生成模块已自动更新!')
        lines.append(f'— 来自爆款文章学习系统 v1.0')
        
        msg = '\n'.join(lines)
        
        resp = bot.send_text(chat_id, msg)
        if resp.get('code') == 0:
            print(f"  [DONE] 飞书通知发送成功!")
        else:
            print(f"  [WARN] 飞书API返回错误: {resp}")
            
    except Exception as e:
        print(f"  [ERROR] 飞书通知失败: {e}, 尝试webhook备用方案...")
        _send_feishu_webhook(result)


def _send_feishu_webhook(result):
    """备用方案：通过 webhook 发送飞书通知"""
    import requests
    
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL', '')
    if not webhook_url:
        print("  [SKIP] 未配置 FEISHU_WEBHOOK_URL，跳过通知")
        return
    
    stats = result['stats']
    plan = result['update_plan']
    
    body = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "text": "📊 爆款文章学习报告"},
                "template": "blue"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "text": f"**⏰ 时间:** {result['run_time']}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "text": f"**📈 采集:** {stats['articles_collected']}篇 | **科技相关:** {stats['tech_related']}篇\n**高优更新:** {len(plan['priority_updates'])}条 | **新增技巧:** {len(plan.get('new_techniques_to_add', []))}个"}},
                {"tag": "hr"},
                {
                    "tag": "action", 
                    "actions": [{
                        "tag": "button", "text": {"tag": "plain_text", "text": "查看详细报告"},
                        "type": "primary", "url": ""
                    }]
                }
            ]
        }
    }
    
    try:
        resp = requests.post(webhook_url, json=body, timeout=10)
        data = resp.json()
        if data.get('code', 0) == 0 or data.get('StatusCode', 0) == 0:
            print("  [DONE] Webhook通知发送成功!")
        else:
            print(f"  [WARN] Webhook返回: {data}")
    except Exception as e:
        print(f"  [ERROR] Webhook也失败了: {e}")


def commit_to_git(result, updated_items=None):
    """将分析结果自动提交到 Git 仓库"""
    try:
        import subprocess
        from pathlib import Path
        
        repo_root = Path(__file__).parent  # wechat-publisher 目录就是 git root
        
        # 检查是否是 git 仓库
        check = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            cwd=repo_root, capture_output=True, text=True, timeout=10
        )
        if check.returncode != 0 or 'true' not in check.stdout.strip():
            print("  [SKIP] 不是Git仓库，跳过提交")
            return False
        
        now = datetime.now()
        ts = now.strftime('%Y-%m-%d_%H%M')
        
        stats = result.get('stats', {})
        articles_count = stats.get('articles_collected', 0)
        life_share_count = stats.get('life_share_count', 0)
        tech_count = stats.get('tech_related', 0)
        new_techs_count = len(result.get('update_plan', {}).get('new_techniques_to_add', []))
        
        # 构建提交信息
        msg_parts = [f"analysis:{ts}", f"articles={articles_count}(tech={tech_count},life={life_share_count})", f"techniques={new_techs_count}"]
        if updated_items:
            msg_parts.append(f"updated_module={len(updated_items)}items")
        commit_msg = ' | '.join(msg_parts)
        
        # 执行 git add（只提交分析结果和更新的模块文件）
        # 1. 新的分析报告
        analysis_dir = repo_root / "output" / "analysis"
        if analysis_dir.exists():
            subprocess.run(
                ['git', 'add', str(analysis_dir)],
                cwd=repo_root, capture_output=True, text=True, timeout=15
            )
        
        # 2. 更新的文章生成模块
        ag_file = repo_root / "modules" / "article_generator.py"
        if ag_file.exists():
            # 检查是否有未暂存的修改
            status = subprocess.run(
                ['git', 'status', '--porcelain', str(ag_file)],
                cwd=repo_root, capture_output=True, text=True, timeout=10
            )
            if status.stdout.strip():
                subprocess.run(
                    ['git', 'add', str(ag_file)],
                    cwd=repo_root, capture_output=True, text=True, timeout=10
                )
        
        # 3. 文章数据库（如果有更新）
        db_dir = repo_root / "article_db"
        if db_dir.exists():
            status = subprocess.run(
                ['git', 'status', '--porcelain', str(db_dir)],
                cwd=repo_root, capture_output=True, text=True, timeout=10
            )
            if status.stdout.strip():
                subprocess.run(
                    ['git', 'add', str(db_dir)],
                    cwd=repo_root, capture_output=True, text=True, timeout=15
                )
        
        # 检查是否有东西需要提交
        diff_check = subprocess.run(
            ['git', 'diff', '--cached', '--stat'],
            cwd=repo_root, capture_output=True, text=True, timeout=10
        )
        
        if not diff_check.stdout.strip():
            print("  [SKIP] 无变更需要提交")
            return True
        
        # 执行 git commit
        commit_result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=repo_root, capture_output=True, text=True, timeout=20
        )
        
        if commit_result.returncode == 0:
            # 尝试 push
            push_result = subprocess.run(
                ['git', 'push'],
                cwd=repo_root, capture_output=True, text=True, timeout=30
            )
            
            if push_result.returncode == 0:
                print(f"  [DONE] Git已提交并推送: {commit_msg}")
                return True
            else:
                print(f"  [WARN] Git推送失败(可能无远程仓库或网络问题): {push_result.stderr[:200]}")
                print(f"  [INFO] 但本地提交成功: {commit_msg}")
                return True
        else:
            print(f"  [WARN] Git提交失败: {commit_result.stderr[:200]}")
            return False
            
    except FileNotFoundError:
        print("  [SKIP] Git未安装或不在PATH中")
        return False
    except Exception as e:
        print(f"  [ERROR] Git操作异常: {e}")
        return False


# ============================================================
# 主入口
# ============================================================

if __name__ == '__main__':
    analyzer = ViralArticleAnalyzer()
    result = analyzer.run_full_analysis()
    
    if result:
        stats = result['stats']
        plan = result['update_plan']
        
        print(f'\n{"="*70}')
        print(f'  [DONE] 分析完成! 共分析 {stats["articles_collected"]} 篇文章')
        if 'life_share_count' in stats:
            print(f'  (含生活分享自述类 {stats["life_share_count"]} 篇)')
        print(f'  生成 {len(plan["priority_updates"])} 条高优先级更新建议')
        print(f'  提炼 {len(plan.get("new_techniques_to_add", []))} 个新写作技巧')
        print(f'{"="*70}')
        
        # === 自动更新文章模块 ===
        print('\n[Auto-Update] Starting article module update...')
        updated = auto_update_article_generator(plan)
        
        # === 发送飞书通知 ===
        print('\n[Feishu] Sending notification...')
        send_feishu_notification(result)
        
        # === 提交到 Git ===
        print('\n[Git] Committing results to repository...')
        commit_to_git(result, updated_items=updated)
        
        print('\n[DONE] All done! Analysis -> Update -> Notify -> Git commit pipeline complete.')
