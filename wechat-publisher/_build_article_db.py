# -*- coding: utf-8 -*-
"""
文章数据库构建器
将爆款分析系统的全部样本文章导出为结构化数据库，
按分类存储，方便git版本管理和后续参考使用。

目录结构：
  article_db/
    manifest.json          # 全局索引(统计/分类/更新时间)
    categories.json        # 分类定义和说明
    tech_viral/            # 科技爆款类 (28篇)
      001_英伟达市值突破4万亿.json
      ...
    life_share/            # 生活分享/自述类 (20篇)
    digital_review/        # 数码测评类 (10篇)
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# 确保可以导入项目模块
sys.path.insert(0, str(Path(__file__).parent))

DB_DIR = Path(__file__).parent / "article_db"


def get_all_articles():
    """从 ViralArticleAnalyzer 获取全部58篇文章"""
    from _analyze_viral_articles import ViralArticleAnalyzer

    analyzer = ViralArticleAnalyzer()
    print("[Step 1] 初始化分析器...")

    # 获取热点种子（不实际搜索，只用于初始化）
    hot_seeds = analyzer._fetch_hot_seeds()
    print(f"  热点种子: {len(hot_seeds)} 个")

    # 获取科技爆款+生活分享+数码测评的完整样本
    articles = analyzer._search_viral_articles(hot_seeds)
    print(f"  总文章数: {len(articles)}")

    return articles


def categorize_articles(articles):
    """
    对文章进行分类，返回 {category: [articles]} 的字典。
    
    分类规则：
    - tech_viral: 科技爆款/行业观察（含tech_viral_sample, auto_tech, ai_llm等）
    - life_share: 生活分享/自述（含life_share, tech_life_share, career_tech）
    - digital_review: 数码测评/开箱体验（digital_review）
    - consumer_electronics: 消费电子观点类（consumer_electronics, chip_semiconductor等）
    - internet_platform: 互联网平台观察（internet_platform, cloud_computing等）
    """
    categories = {
        "tech_viral": [],       # 科技爆款（AI/芯片/新能源车/大模型等核心话题）
        "life_share": [],       # 生活分享/自述
        "digital_review": [],   # 数码测评/开箱
        "consumer_electronics": [],  # 消费电子/硬件观点
        "internet_platform": [],     # 互联网平台/云计算观察
    }

    # 分类关键词映射
    CATEGORY_RULES = {
        "tech_viral": [
            "tech_viral", "auto_tech", "ai_llm", "ai_productivity",
            "ai_video", "chip_semiconductor"
        ],
        "life_share": [
            "life_share", "tech_life_share", "career_tech"
        ],
        "digital_review": [
            "digital_review"
        ],
        "consumer_electronics": [
            "consumer_electronics"
        ],
        "internet_platform": [
            "internet_platform", "cloud_computing"
        ],
    }

    for art in articles:
        source_tag = art.get("source", "")
        matched = False
        for cat, tags in CATEGORY_RULES.items():
            if any(tag in source_tag for tag in tags):
                categories[cat].append(art)
                matched = True
                break
        if not matched:
            # 默认归类到科技爆款
            categories["tech_viral"].append(art)

    return categories


def build_article_record(article, index: int, category: str) -> dict:
    """将原始文章数据转换为标准化的数据库记录格式"""
    content = article.get("simulated_content", "") or article.get("content", "")
    
    return {
        "db_id": f"{category}_{index:03d}",
        "category": category,
        "source_tag": article.get("source", ""),
        "title": article.get("title", ""),
        "author_style": article.get("author_style", article.get("real_observed_features", [])),
        "word_count": len(content),
        
        # 完整内容
        "opening": content[:300] if content else "",
        "body_paragraphs": _split_into_paragraphs(content),
        "closing": content[-200:] if content and len(content) > 200 else (content or ""),
        "full_content": content,
        
        # 分析元数据
        "writing_features": article.get("real_observed_features", []),
        "is_tech": article.get("is_tech", False),
        
        # 数据库元数据
        "created_at": datetime.now().isoformat(),
        "version": "1.0",
        "tags": _extract_tags(article),
    }


def _split_into_paragraphs(content: str) -> list[str]:
    """按段落拆分正文"""
    if not content:
        return []
    paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
    return paragraphs


def _extract_tags(article) -> list[str]:
    """从文章中提取标签"""
    tags = []
    title = article.get("title", "")
    content = article.get("simulated_content", "") or article.get("content", "")

    # 标签提取规则
    tag_patterns = [
        (r"英伟达|NVIDIA|黄仁勋", "英伟达"),
        (r"华为|Huawei|Pura|Mate|昇腾", "华为"),
        (r"苹果|Apple|iPhone|iPad|Mac", "苹果"),
        (r"小米|Xiaomi|SU7|雷军", "小米"),
        (r"特斯拉|Tesla|马斯克|FSD", "特斯拉"),
        (r"比亚迪|BYD|王传福", "比亚迪"),
        (r"蔚来|NIO|李斌|换电", "蔚来"),
        (r"理想|Li Auto|MEGA|李想", "理想汽车"),
        (r"DeepSeek|Kimi|月之暗面|GPT|ChatGPT|OpenAI", "AI大模型"),
        (r"台积电|TSMC|2nm|芯片|半导体", "芯片半导体"),
        (r"折叠屏|新能源|智驾|自动驾驶", "智能硬件"),
        (r"裁员|裸辞|转行|35岁|失业|大厂", "职场人生"),
        (r"独居|租房|断舍离|极简|戒.*短视频", "生活方式"),
        (r"评测|开箱|用了.*个月|真实体验", "数码测评"),
        (r"字节|拼多多|小红书|阿里云|微信|腾讯", "互联网平台"),
    ]

    text = f"{title} {content}"
    for pattern, tag in tag_patterns:
        if re.search(pattern, text, re.IGNORECASE) and tag not in tags:
            tags.append(tag)

    return tags


def save_article(record: dict, output_dir: Path):
    """保存单篇文章到JSON文件"""
    filename = f"{record['db_id']}_{_sanitize_filename(record['title'][:30])}.json"
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return filepath


def _sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    name = name.replace(' ', '_')
    return name[:50]  # 截断过长文件名


def build_manifest(categories: dict, db_dir: Path) -> dict:
    """构建全局索引manifest"""
    total = sum(len(arts) for arts in categories.values())
    manifest = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "total_articles": total,
        "categories": {},
        "tag_index": {},  # 标签倒排索引
        "statistics": {},
    }

    all_tags = {}
    for cat_name, articles in categories.items():
        cat_manifest = {
            "name_zh": CATEGORY_NAMES_ZH[cat_name],
            "description": CATEGORY_DESC[cat_name],
            "count": len(articles),
            "articles": [],
        }

        for i, art in enumerate(articles):
            record = build_article_record(art, i + 1, cat_name)
            save_article(record, db_dir / cat_name)

            entry = {
                "db_id": record["db_id"],
                "title": record["title"],
                "source_tag": record["source_tag"],
                "word_count": record["word_count"],
                "tags": record["tags"],
                "is_tech": record.get("is_tech", False),
            }
            cat_manifest["articles"].append(entry)

            # 构建标签索引
            for tag in record["tags"]:
                if tag not in all_tags:
                    all_tags[tag] = []
                all_tags[tag].append(record["db_id"])

        manifest["categories"][cat_name] = {
            "name_zh": cat_manifest["name_zh"],
            "description": cat_manifest["description"],
            "count": cat_manifest["count"],
            "article_ids": [a["db_id"] for a in cat_manifest["articles"]],
        }
        print(f"  [{cat_name}] {cat_manifest['name_zh']}: {len(articles)} 篇")

    manifest["tag_index"] = {k: sorted(set(v)) for k, v in sorted(all_tags.items())}
    
    # 统计信息
    manifest["statistics"] = {
        "total_words": sum(
            len(a.get("simulated_content", "") or a.get("content", ""))
            for arts in categories.values()
            for a in arts
        ),
        "avg_word_per_article": int(
            sum(len(a.get("simulated_content", "") or a.get("content", ""))
                for arts in categories.values() for a in arts)
            / max(total, 1)
        ),
        "unique_tags": len(all_tags),
    }

    return manifest


# 分类名称中文映射
CATEGORY_NAMES_ZH = {
    "tech_viral": "科技爆款",
    "life_share": "生活分享",
    "digital_review": "数码测评",
    "consumer_electronics": "消费电子观点",
    "internet_platform": "互联网平台观察",
}

CATEGORY_DESC = {
    "tech_viral": "AI、芯片、新能源车、消费电子、互联网平台等领域的高热度爆款文章，侧重行业观察和观点输出",
    "life_share": "博主个人生活分享、自述式文章，第一人称自然语言，包含职业变动、独居生活、财务状况等真实经历",
    "digital_review": "数码产品深度测评和使用体验，包含开箱感受、长期使用反馈、购买建议等",
    "consumer_electronics": "消费电子产品相关的行业分析和观点文章",
    "internet_platform": "互联网平台企业动态、战略方向、行业竞争格局观察",
}


def main():
    print("=" * 60)
    print("  文章数据库构建器")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: 获取所有文章
    print("\n[Step 1] 收集全部文章...")
    articles = get_all_articles()
    print(f"  共收集 {len(articles)} 篇")

    # Step 2: 创建目录结构（先清理旧数据）
    print("\n[Step 2] 创建目录结构...")
    import shutil
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)
        print("  已清理旧数据库")
    DB_DIR.mkdir(parents=True, exist_ok=True)
    for cat_dir in ["tech_viral", "life_share", "digital_review", 
                     "consumer_electronics", "internet_platform"]:
        (DB_DIR / cat_dir).mkdir(exist_ok=True)
    print(f"  数据库根目录: {DB_DIR}")

    # Step 3: 分类并导出
    print("\n[Step 3] 分类导出文章...")
    categories = categorize_articles(articles)

    # Step 4: 构建manifest
    print("\n[Step 4] 构建全局索引...")
    manifest = build_manifest(categories, DB_DIR)

    # 保存 manifest
    manifest_path = DB_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 保存分类定义
    categories_def = {
        cat: {"name_zh": CATEGORY_NAMES_ZH[cat], "description": CATEGORY_DESC[cat]}
        for cat in categories.keys()
    }
    with open(DB_DIR / "categories.json", "w", encoding="utf-8") as f:
        json.dump(categories_def, f, ensure_ascii=False, indent=2)

    # 输出结果
    print("\n" + "=" * 60)
    print(f"  [DONE] 数据库构建完成!")
    print(f"  总文章: {manifest['total_articles']} 篇")
    print(f"  总字数: {manifest['statistics']['total_words']:,} 字")
    print(f"  平均每篇: {manifest['statistics']['avg_word_per_article']} 字")
    print(f"  标签数: {manifest['statistics']['unique_tags']} 个")
    print(f"  分类:")
    for cat_id, cat_info in manifest["categories"].items():
        print(f"    - {cat_info['name_zh']}: {cat_info['count']} 篇")
    print(f"\n  数据库路径: {DB_DIR}")
    print(f"  索引文件: {manifest_path.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
