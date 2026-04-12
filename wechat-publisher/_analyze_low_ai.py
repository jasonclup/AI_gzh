"""修复损坏的JSON文件并提取低AI文章"""
import json
import re

DATA_FILE = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-11.json'
OUTPUT_FILE = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\low_ai_analysis.json'

# 读取原始内容
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()

# 尝试修复常见JSON问题：找到每个hourly_records中的独立record
# 策略：提取所有独立的record对象

print(f"原始文件大小: {len(raw)} 字符")

# 方法1: 尝试逐步解析，找到坏的位置
try:
    data = json.loads(raw)
    print("JSON正常！")
except json.JSONDecodeError as e:
    print(f"JSON错误位置: 行{e.lineno}, 列{e.colno}: {e.msg}")
    
    # 方法2: 找到错误位置附近的文本分析
    pos = e.pos
    context_start = max(0, pos - 200)
    context_end = min(len(raw), pos + 200)
    print(f"\n错误附近内容:")
    print(repr(raw[context_start:context_end]))

# 方法3: 用正则提取每个完整的record块
print("\n\n--- 正则提取模式 ---")

# 提取所有 {"hour": "XX", ...} 记录
pattern = r'\{\s*"hour"\s*:\s*"[0-9]+"' 
matches = list(re.finditer(pattern, raw))
print(f"找到 {len(matches)} 个hourly record起始位置")

# 尝试逐个提取并解析record
low_ai_articles = []
total_articles = 0
valid_records = 0
failed_records = 0

for i, m in enumerate(matches):
    start = m.start()
    # 找到这个record的结束位置（下一个record开始或文件结束）
    if i + 1 < len(matches):
        end = matches[i + 1].start()
    else:
        end = len(raw)
    
    chunk = raw[start:end].rstrip().rstrip(',')
    
    # 尝试补全为完整对象
    if not chunk.endswith('}'):
        # 往后找最近的 }
        last_brace = chunk.rfind('}')
        if last_brace > 0:
            chunk = chunk[:last_brace + 1]
    
    try:
        record = json.loads(chunk)
        valid_records += 1
        hour = record.get('hour', '?')
        
        # 从record中提取文章
        for key in ['hot_topics', 'all_results']:
            topics = record.get(key, [])
            if isinstance(topics, list) and topics:
                first_t = topics[0]
                if isinstance(first_t, dict) and 'competitor_articles' in first_t:
                    for t in topics:
                        topic_title = t.get('topic', t.get('title', 'N/A'))
                        for a in t.get('competitor_articles', []):
                            total_articles += 1
                            score = a.get('ai_score', 100)
                            if score < 40:
                                low_ai_articles.append({
                                    'hour': hour,
                                    'topic': topic_title,
                                    'title': a.get('title', ''),
                                    'account': a.get('account', ''),
                                    'ai_score': score,
                                    'ai_category': a.get('ai_category', ''),
                                    'ai_evidence': a.get('ai_evidence', []),
                                    'summary': a.get('summary', ''),
                                    'article_style': a.get('article_style', ''),
                                    'word_count': a.get('word_count', 0),
                                    'has_real_data': a.get('has_real_data', False),
                                })
                break  # 只取一个key
    
    except json.JSONDecodeError as e2:
        failed_records += 1
        # 打印前几个失败的信息
        if failed_records <= 3:
            print(f"  Record #{i+1} 解析失败: {e2.msg}")

print(f"\n有效记录: {valid_records}, 失败记录: {failed_records}")
print(f"总文章数: {total_articles}, 低AI(<40): {len(low_ai_articles)}篇")

# 按分数排序
low_ai_articles.sort(key=lambda x: x['ai_score'])

print("\n" + "=" * 80)

for i, art in enumerate(low_ai_articles, 1):
    score = art['ai_score']
    h = art['hour']
    title = art['title']
    acc = art['account']
    style = art['article_style']
    wc = art['word_count']
    has_data = art['has_real_data']
    summary = art['summary']
    evidence = art.get('ai_evidence', [])
    
    print(f"\n{'─'*60}")
    print(f"[{i}] ★★★ AI={score}分 | {h}:00 | @{acc}")
    print(f"标题: {title}")
    print(f"风格:{style} | 字数:{wc} | 有真实数据:{has_data}")
    print(f"摘要: {summary}")
    if evidence:
        print(f"人写特征(反向证据):")
        for ev in evidence:
            print(f"  [OK] {ev}")

# 保存结果
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(low_ai_articles, f, ensure_ascii=False, indent=2)

print(f"\n\n✅ 已保存到 {OUTPUT_FILE}")

# 输出汇总统计
if low_ai_articles:
    scores = [a['ai_score'] for a in low_ai_articles]
    accounts = {}
    styles = {}
    for a in low_ai_articles:
        acc = a['account']
        accounts[acc] = accounts.get(acc, 0) + 1
        s = a['article_style']
        styles[s] = styles.get(s, 0) + 1
    
    print(f"\n{'='*60}")
    print(f"统计汇总:")
    print(f"  平均AI评分: {sum(scores)/len(scores):.1f}分")
    print(f"  最低分: {min(scores)}分 | 最高分: {max(scores)}分")
    print(f"\n  账号分布:")
    for acc, cnt in sorted(accounts.items(), key=lambda x:-x[1]):
        print(f"    @{acc}: {cnt}篇")
    print(f"\n  风格分布:")
    for s, cnt in sorted(styles.items(), key=lambda x:-x[1]):
        print(f"    {s}: {cnt}篇")
