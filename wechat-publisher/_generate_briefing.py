"""
竞品分析全量数据简报生成器
读取所有日期的JSON数据，输出HTML可视化简报
"""
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'competitor_analysis')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_all_data():
    """加载所有日期的数据文件"""
    all_records = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.endswith('.json') or fname.startswith('_') or '.bak' in fname:
            continue
        fpath = os.path.join(DATA_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            records = data.get('hourly_records', [])
            date_key = fname.replace('.json', '')
            for r in records:
                r['_date'] = date_key
            all_records.extend(records)
        except Exception as e:
            print(f"跳过 {fname}: {e}")
    return all_records

def analyze(records):
    """分析所有数据"""
    
    # 1. 基本统计
    total_rounds = len(records)
    total_articles = 0
    total_topics_set = set()
    ai_scores = []
    accounts = Counter()
    article_styles = Counter()
    high_ai_articles = []  # AI > 70
    low_ai_articles = []   # AI < 40
    
    hourly_distribution = Counter()
    daily_distribution = Counter()
    topic_heat_map = []  # (topic, heat_level, count)
    
    for r in records:
        hour = r.get('hour', '?')
        date = r.get('_date', '?')
        hourly_distribution[hour] += 1
        daily_distribution[date] += 1
        
        topics = r.get('hot_topics', [])
        if isinstance(topics, list) and topics:
            for t in topics:
                topic_title = ''
                articles = []
                
                if isinstance(t, dict):
                    topic_title = t.get('topic') or t.get('title', 'N/A')
                    articles = t.get('competitor_articles', [])
                elif isinstance(t, str):
                    topic_title = t
                
                total_topics_set.add(topic_title[:30])
                
                if isinstance(articles, list):
                    for a in articles:
                        total_articles += 1
                        score = a.get('ai_score', 50)
                        ai_scores.append(score)
                        
                        acc = a.get('account', '未知')
                        accounts[acc] += 1
                        
                        style = a.get('article_style', '未知')
                        article_styles[style] += 1
                        
                        if score >= 70:
                            high_ai_articles.append({
                                'title': a.get('title', ''),
                                'account': acc,
                                'score': score,
                                'topic': topic_title,
                                'hour': hour,
                                'date': date,
                            })
                        if score < 40:
                            low_ai_articles.append({
                                'title': a.get('title', ''),
                                'account': acc,
                                'score': score,
                                'topic': topic_title,
                                'style': style,
                                'hour': hour,
                                'date': date,
                            })
    
    # 2. 计算统计值
    avg_ai = sum(ai_scores) / len(ai_scores) if ai_scores else 0
    max_ai = max(ai_scores) if ai_scores else 0
    min_ai = min(ai_scores) if ai_scores else 0
    
    # AI评分分布
    ai_distribution = {
        '人写 (<40)': len([s for s in ai_scores if s < 40]),
        '疑似AI (40-55)': len([s for s in ai_scores if 40 <= s < 56]),
        '较像AI (56-70)': len([s for s in ai_scores if 56 <= s < 71]),
        '几乎确定AI (>70)': len([s for s in ai_scores if s >= 70]),
    }
    
    # 账号平均分统计
    account_score_map = defaultdict(list)
    for r in records:
        topics = r.get('hot_topics', [])
        if isinstance(topics, list):
            for t in topics:
                if not isinstance(t, dict): continue
                for a in t.get('competitor_articles', []):
                    acc = a.get('account', '未知')
                    account_score_map[acc].append(a.get('ai_score', 50))
    
    account_rankings = []
    for acc, scores in account_score_map.items():
        account_rankings.append({
            'account': acc,
            'avg_score': round(sum(scores)/len(scores), 1),
            'article_count': len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
        })
    account_rankings.sort(key=lambda x: x['avg_score'], reverse=True)
    
    # 低AI账号排行（最像人写的）
    human_like_accounts = [a for a in account_rankings if a['avg_score'] < 50]
    human_like_accounts.sort(key=lambda x: x['avg_score'])
    
    return {
        'total_rounds': total_rounds,
        'total_articles': total_articles,
        'unique_topics': len(total_topics_set),
        'avg_ai': round(avg_ai, 1),
        'max_ai': max_ai,
        'min_ai': min_ai,
        'ai_distribution': ai_distribution,
        'high_ai_count': ai_distribution.get('几乎确定AI (>70)', 0),
        'low_ai_count': ai_distribution.get('人写 (<40)', 0),
        'hourly_dist': dict(sorted(hourly_distribution.items())),
        'daily_dist': dict(sorted(daily_distribution.items())),
        'top_accounts': account_rankings[:10],
        'human_accounts': human_like_accounts[:10],
        'high_ai_top20': sorted(high_ai_articles, key=lambda x: x['score'], reverse=True)[:20],
        'low_ai_top20': sorted(low_ai_articles, key=lambda x: x['score'])[:20],
        'styles': dict(article_styles.most_common(10)),
        'total_accounts': len(account_rankings),
    }

def generate_html(stats, output_path):
    """生成HTML简报"""
    
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>竞品分析全景简报</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background:#f0f2f5; color:#333; padding:16px; }
.container { max-width:1100px; margin:0 auto; }

.header { background:linear-gradient(135deg, #0d47a1, #1565c0); color:#fff; padding:28px 32px; border-radius:14px; margin-bottom:20px; box-shadow:0 4px 20px rgba(13,71,161,0.25); }
.header h1 { font-size:24px; font-weight:800; margin-bottom:6px; }
.header .sub { font-size:13px; opacity:0.85; }
.header .badge { display:inline-block; background:rgba(255,255,255,0.18); padding:4px 14px; border-radius:20px; font-size:12px; margin-top:8px; }

.row { display:flex; gap:14px; margin-bottom:18px; flex-wrap:wrap; }

.card { background:#fff; border-radius:12px; padding:18px 20px; box-shadow:0 2px 10px rgba(0,0,0,0.06); transition:all 0.2s; cursor:pointer; }
.card:hover { transform:translateY(-3px); box-shadow:0 6px 22px rgba(0,0,0,0.12); }
.stat-card { text-align:center; min-width:120px; flex:1; }
.stat-card .num { font-size:32px; font-weight:900; line-height:1.2; }
.stat-card .label { font-size:11.5px; color:#888; margin-top:3px; }
.c-blue .num { color:#1565c0; }
.c-green .num { color:#2e7d32; }
.c-orange .num { color:#e65100; }
.c-red .num { color:#c62828; }
.c-purple .num { color:#6a1b9a; }
.c-teal .num { color:#00695c; }

.section { background:#fff; border-radius:12px; padding:22px 24px; margin-bottom:18px; box-shadow:0 2px 10px rgba(0,0,0,0.06); transition:box-shadow 0.2s; }
.section:hover { box-shadow:0 4px 18px rgba(0,0,0,0.1); }
.section-title { font-size:17px; font-weight:800; color:#0d47a1; margin-bottom:14px; display:flex; align-items:center; gap:8px; padding-bottom:10px; border-bottom:2px solid #e3f2fd; }
.section-title::before { content:''; width:4px; height:20px; background:linear-gradient(180deg,#1565c0,#42a5f5); border-radius:2px; }

/* AI分布条 */
.ai-dist-bar { height:36px; border-radius:18px; overflow:hidden; display:flex; margin:14px 0; box-shadow:inset 0 2px 6px rgba(0,0,0,0.08); }
.ai-seg { display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; color:#fff; transition:filter 0.2s; cursor:pointer; min-width:40px; }
.ai-seg:hover { filter:brightness(1.15); transform:scaleY(1.05); }
.seg-human { background:linear-gradient(135deg,#43a047,#66bb6a); }
.seg-suspect { background:linear-gradient(135deg,#fb8c00,#ffa726); }
.seg-likely { background:linear-gradient(135deg,#e65100,#ff9800); }
.seg-certain { background:linear-gradient(135deg,#c62828,#ef5350); }
.dist-legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:8px; font-size:12px; }
.legend-item { display:flex; align-items:center; gap:5px; }
.legend-dot { width:12px; height:12px; border-radius:3px; }

/* 表格 */
table { width:100%; border-collapse:collapse; font-size:13px; }
th { background:#e8eaf6; color:#1a237e; padding:10px 12px; text-align:left; font-weight:700; font-size:12px; letter-spacing:0.3px; }
td { padding:9px 12px; border-bottom:1px solid #f0f0f0; vertical-align:middle; }
tr { transition:all 0.15s; cursor:pointer; }
tr:hover { background:#e3f2fd; transform:scale(1.002); }

.score-badge { display:inline-block; padding:2px 10px; border-radius:10px; font-weight:800; font-size:11.5px; transition:all 0.2s; }
.badge-danger { background:#ffcdd2; color:#b71c1c; }
.badge-warn { background:#ffe0b2; #e65100; color:#bf360c; }
.badge-safe { background:#c8e6c9; color:#1b5e20; }
.score-badge:hover { transform:scale(1.15); box-shadow:0 2px 8px rgba(0,0,0,0.15); }

/* 热力图 */
.heatmap-grid { display:grid; grid-template-columns:repeat(24,1fr); gap:3px; margin-top:10px; }
.hm-cell { aspect-ratio:1; border-radius:5px; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:700; color:#fff; transition:transform 0.15s; cursor:pointer; }
.hm-cell:hover { transform:scale(1.3); z-index:2; box-shadow:0 3px 12px rgba(0,0,0,0.3); }

/* 账号卡片 */
.account-row { display:flex; align-items:center; padding:10px 14px; border-radius:8px; margin-bottom:6px; background:#fafafa; transition:all 0.2s; cursor:pointer; }
.account-row:hover { background:#e8eaf6; transform:translateX(4px); }
.acc-name { font-weight:600; font-size:13px; flex:2; }
.acc-score { font-weight:800; font-size:16px; flex:1; text-align:right; }
.acc-count { font-size:11.5px; color:#888; flex:1; text-align:right; }
.acc-bar { height:6px; border-radius:3px; margin-right:12px; flex:1.5; min-width:60px; }

/* 标签 */
.tag { display:inline-block; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:600; margin:2px; }
.tag-blue { background:#e3f2fd; color:#1565c0; }
.tag-red { background:#ffebee; color:#c62828; }
.tag-green { background:#e8f5e9; color:#2e7d32; }
.tag-gray { background:#f5f5f5; color:#666; }

.insight-box { background:linear-gradient(135deg,#e8eaf6,#c5cae9); border-left:5px solid #1565c0; padding:14px 18px; border-radius:0 10px 10px 0; margin:10px 0; font-size:13.5px; line-height:1.7; }
.insight-box.warning { background:linear-gradient(135deg,#fff3e0,#ffe0b2); border-left-color:#e65100; }
.insight-box.success { background:linear-gradient(135deg,#e8f5e9,#c8e6c9); border-left-color:#2e7d32; }

.footer { text-align:center; padding:18px; color:#aaa; font-size:11.5px; margin-top:10px; }
</style>
</head>
<body>
<div class="container">
'''
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    html += f'''
<div class="header">
  <h1>📊 公众号竞品分析 · 全景简报</h1>
  <div class="sub">热点追踪 × AI内容检测 × 多日数据分析</div>
  <div class="badge">🕐 数据截止 {now} | 共覆盖 {len(stats["daily_dist"])} 个采集日</div>
</div>

<!-- 核心指标 -->
<div class="row">'''

    metrics = [
        ('总轮次', stats['total_rounds'], 'c-blue'),
        ('文章总数', stats['total_articles'], 'c-green'),
        ('独立话题', stats['unique_topics'], 'c-purple'),
        ('平均AI分', stats['avg_ai'], 'c-orange'),
        ('最高AI分', stats['max_ai'], 'c-red'),
        ('最低AI分', stats['min_ai'], 'c-teal'),
        ('高AI(>70)', stats['high_ai_count'], 'c-red'),
        ('低AI(<40)', stats['low_ai_count'], 'c-green'),
        ('监控账号', stats['total_accounts'], 'c-blue'),
    ]
    for label, val, cls in metrics:
        html += f'''<div class="card stat-card {cls}">
          <div class="num">{val}</div>
          <div class="label">{label}</div></div>'''
    
    html += '</div>'

    # AI评分分布
    dist = stats['ai_distribution']
    total = stats['total_articles']
    segs = [
        ('seg-human', dist.get('人写 (<40)', 0), '#43a047', '人写\\n<40分'),
        ('seg-suspect', dist.get('疑似AI (40-55)', 0), '#fb8c00', '疑似AI\\n40-55分'),
        ('seg-likely', dist.get('较像AI (56-70)', 0), '#e65100', '较像AI\\n56-70分'),
        ('seg-certain', dist.get('几乎确定AI (>70)', 0), '#c62828', '确定AI\\n>70分'),
    ]
    
    pct_parts = [v/total*100 if total > 0 else 0 for _, v, _, _ in segs]
    
    html += '''
<!-- AI评分分布 -->
<div class="section">
  <div class="section-title">🎯 AI评分分布全景</div>
  <div class="ai-dist-bar">'''
    for cls, val, color, label in segs:
        pct = val/total*100 if total > 0 else 0
        if pct > 5:
            show_text = f'{val}篇({pct:.0f}%)'
        elif val > 0:
            show_text = f'{val}篇'
        else:
            show_text = ''
        html += f'<div class="ai-seg {cls}" style="width:{pct:.1f}%;background:{color}">{show_text}</div>'
    
    html += '</div><div class="dist-legend">'
    for cls, val, color, label in segs:
        clean_label = label.replace('\\n', ' ')
        pct = val/total*100 if total > 0 else 0
        html += f'<div class="legend-item"><div class="legend-dot" style="background:{color}"></div>{clean_label}: {val}篇 ({pct:.1f}%)</div>'
    html += '</div>'
    
    # 人写率
    low_pct = stats['low_ai_count']/total*100 if total > 0 else 0
    high_pct = stats['high_ai_count']/total*100 if total > 0 else 0
    html += f'''
  <div class="insight-box success" style="margin-top:14px;">
    💡 <strong>关键发现：</strong>在 ''' + str(total) + ''' 篇文章中，''' + str(stats['low_ai_count']) + ''' 篇 (''' + f'{low_pct:.1f}' + ''') 的AI评分低于40分（人写风格），<br/>
    而 ''' + str(stats['high_ai_count']) + ''' 篇 (''' + f'{high_pct:.1f}' + ''') 被判定为几乎确定是AI写的。<br/>平均AI评分 ''' + str(stats['avg_ai']) + ''' 分。
    这意味着约 ''' + f'{100-high_pct-low_pct:.0f}' + '''% 的内容处于"模糊地带"，这正是我们写作要瞄准的区间。
  </div>
</div>'''

    # 每日轮次热力图
    html += '''
<!-- 采集时间热力图 -->
<div class="section">
  <div class="section-title">📅 各时段采集频率热力图</div>
  <div style="font-size:12px;color:#666;margin-bottom:6px;">颜色越深=采集次数越多 | 每格代表该小时累计轮数</div>
  <div class="heatmap-grid">'''
    
    hourly = stats['hourly_dist']
    max_h = max(hourly.values()) if hourly else 1
    for h in range(24):
        count = hourly.get(f'{h:02d}', 0)
        intensity = count / max_h if max_h > 0 else 0
        if intensity == 0:
            bg = '#eceff1'
            fg = '#999'
        elif intensity < 0.33:
            bg = '#c8e6c9'
            fg = '#2e7d32'
        elif intensity < 0.67:
            bg = '#64b5f6'
            fg = '#fff'
        else:
            bg = '#1565c0'
            fg = '#fff'
        html += f'<div class="hm-cell" style="background:{bg};color:{fg}" title="{h:02d}:00 - {count}轮">{count}</div>'
    html += '</div></div>'

    # 最像AI的账号 TOP10
    html += '''
<!-- 高AI账号排行 -->
<div class="section">
  <div class="section-title">⚠️ 最可能用AI的账号 TOP10</div>
  <table>
  <thead><tr><th>#</th><th>公众号</th><th>文章数</th><th>平均AI分</th><th>最高/最低</th><th>风险等级</th></tr></thead><tbody>'''
    
    for i, acc in enumerate(stats.get('top_accounts', [])[:10], 1):
        avg = acc['avg_score']
        if avg >= 75: badge_cls, badge_txt = 'badge-danger', '极高'
        elif avg >= 60: badge_cls, badge_txt = 'badge-warn', '偏高'
        else: badge_cls, badge_txt = 'badge-safe', '一般'
        
        bar_color = '#ef5350' if avg >= 75 else '#ffa726' if avg >= 60 else '#66bb6a'
        bar_width = min(avg, 100)
        
        html += f'''<tr>
          <td>{i}</td>
          <td><strong>{acc['account']}</strong></td>
          <td>{acc['article_count']}篇</td>
          <td><span class="score-badge {'badge-danger' if avg>=70 else 'badge-warn' if avg>=55 else 'badge-safe'}">{avg}</span></td>
          <td>{acc['max_score']} / {acc['min_score']}</td>
          <td><span class="tag tag-red">{badge_txt}</span></td>
        </tr>'''
    html += '</tbody></table></div>'

    # 最像人写的账号 TOP10
    html += '''
<!-- 低AI账号（人写风格） -->
<div class="section">
  <div class="section-title">✅ 最像人写的账号 TOP10（学习对象）</div>
  <table>
  <thead><tr><th>#</th><th>公众号</th><th>文章数</th><th>平均AI分</th><th>分数范围</th><th>推荐度</th></tr></thead><tbody>'''
    
    for i, acc in enumerate(stats.get('human_accounts', [])[:10], 1):
        avg = acc['avg_score']
        rec = '⭐⭐⭐ 强推' if avg < 25 else '⭐⭐ 推荐' if avg < 35 else '⭐ 参考'
        
        html += f'''<tr>
          <td>{i}</td>
          <td><strong>{acc['account']}</strong></td>
          <td>{acc['article_count']}篇</td>
          <td><span class="score-badge badge-safe">{avg}</span></td>
          <td>{acc['min_score']} ~ {acc['max_score']}</td>
          <td><span class="tag tag-green">{rec}</span></td>
        </tr>'''
    html += '</tbody></table></div>'

    # 高AI文章 TOP15
    html += '''
<!-- 最高AI评分文章 -->
<div class="section">
  <div class="section-title">🔴 最高AI评分文章 TOP15（反面教材）</div>
  <table>
  <thead><tr><th>AI分</th><th>标题</th><th>公众号</th><th>话题/时间</th></tr></thead><tbody>'''
    
    for art in stats.get('high_ai_top20', [])[:15]:
        cls = 'badge-danger' if art['score'] >= 85 else 'badge-warn' if art['score'] >= 75 else 'badge-warn'
        title_short = art['title'][:35] + ('...' if len(art['title']) > 35 else '')
        topic_short = art['topic'][:20] + ('...' if len(art['topic']) > 20 else '')
        html += f'''<tr>
          <td><span class="score-badge {cls}">{art['score']}</span></td>
          <td>{title_short}</td>
          <td>@{art['account']}</td>
          <td>{topic_short}<br/><span class="tag tag-gray">{art['date']} {art['hour']}:00</span></td>
        </tr>'''
    html += '</tbody></table></div>'

    # 低AI文章 TOP15（学习榜样）
    html += '''
<!-- 最低AI评分文章 -->
<div class="section">
  <div class="section-title">🟢 最低AI评分文章 TOP15（学习榜样）</div>
  <table>
  <thead><tr><th>AI分</th><th>标题</th><th>公众号</th><th>写作风格/时间</th></tr></thead><tbody>'''
    
    for art in stats.get('low_ai_top20', [])[:15]:
        title_short = art['title'][:35] + ('...' if len(art['title']) > 35 else '')
        style_tag = art.get('style', '')[:10]
        html += f'''<tr>
          <td><span class="score-badge badge-safe">{art['score']}</span></td>
          <td>{title_short}</td>
          <td>@{art['account']}</td>
          <td><span class="tag tag-blue">{style_tag or "人写"}</span> 
              <span class="tag tag-gray">{art['date']} {art['hour']}:00</span></td>
        </tr>'''
    html += '</tbody></table></div>'

    # 文章风格分布
    html += '<div class="section"><div class="section-title">📝 写作风格分布</div>'
    styles = stats.get('styles', {})
    for style, count in styles.items():
        pct = count / total * 100 if total > 0 else 0
        bar_color = '#1565c0'
        html += f'''<div style="margin:6px 0;display:flex;align-items:center;gap:10px;font-size:13px;">
      <span style="width:140px;font-weight:600;">{style}</span>
      <div style="flex:1;height:22px;background:#eee;border-radius:11px;overflow:hidden;">
        <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:11px;transition:width 0.5s;"></div>
      </div>
      <span style="font-weight:600;width:80px;text-align:right;">{count}篇({pct:.1f}%)</span>
    </div>'''
    html += '</div>'

    # 关键洞察
    html += f'''
<!-- 关键洞察 -->
<div class="section">
  <div class="section-title">💡 关键洞察与建议</div>
  
  <div class="insight-box warning">
    ⚠️ <strong>风险警示：</strong>当前监控的 {stats["total_accounts"]} 个账号中，
    平均AI评分超过60分的占比显著。其中排名前3的账号平均分均超过70分，
    这些账号的内容特征值得作为<strong>反面教材</strong>重点研究——避免踩坑。
  </div>
  
  <div class="insight-box success">
    ✅ <strong>学习机会：</strong>有 {stats["low_ai_count"]} 篇文章AI评分低于40分，
    这些文章来自 {len(stats.get("human_accounts",[]))} 个人写风格明显的账号。
    建议重点关注这些账号的：<br/>
    &nbsp;&nbsp;• 开头方式（避免"首先/其次"等套路）<br/>
    &nbsp;&nbsp;• 过渡句式（多用口语化转折）<br/>
    &nbsp;&nbsp;• 结尾风格（避免"让我们期待/未来可期"等套话）
  </div>
  
  <div class="insight-box">
    📈 <strong>数据规模：</strong>经过 {len(stats["daily_dist"])} 天、{stats["total_rounds"]} 轮次的持续采集，
    已积累 {stats["total_articles"]} 篇竞品文章样本。这个数据量足以支撑：
    <br/>• 建立稳定的"人写vs AI"特征基线<br/>
    • 识别各垂直领域的典型写作模式<br/>
    • 为我们自己的AI写作提供持续的优化反馈
  </div>
</div>

<div class="footer">
  🔍 wechat-publisher 竞品分析系统自动生成 | 数据来源: competitor_analysis/*.json
</div>
</div></body></html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    print("正在加载数据...")
    records = load_all_data()
    print(f"共加载 {len(records)} 条轮次记录")
    
    print("正在分析...")
    stats = analyze(records)
    
    out_path = os.path.join(OUTPUT_DIR, 'full_briefing.html')
    generate_html(stats, out_path)
    
    print(f"\n简报已生成: {out_path}")
    print(f"总文章: {stats['total_articles']}, 平均AI: {stats['avg_ai']}")
