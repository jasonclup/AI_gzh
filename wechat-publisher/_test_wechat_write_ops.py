# -*- coding: utf-8 -*-
import json
from pathlib import Path

import yaml

from modules.wechat_api import WeChatPublisher


def main():
    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8")) or {}
    pub = WeChatPublisher(cfg)

    img = "output/images/A_high_quality_magazine_cover__2026-04-14T11-40-36.png"
    token = pub._get_access_token()
    temp_url = pub.upload_temp_image(img)
    media_id = pub.upload_image(img)
    draft = pub._save_draft(
        token,
        {
            "articles": [
                {
                    "title": "【接口测试】请忽略",
                    "author": "WorkBuddy AI",
                    "digest": "公众号接口联通性测试草稿，可忽略。",
                    "content": f'<p>这是接口联通性测试草稿，可忽略。</p><p><img src="{temp_url}" /></p>',
                    "thumb_media_id": media_id,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0,
                }
            ]
        },
    )

    out = {
        "token_ok": bool(token),
        "temp_image_ok": bool(temp_url),
        "temp_image_url_prefix": temp_url[:60] + "..." if temp_url else "",
        "permanent_image_ok": bool(media_id),
        "media_id_prefix": media_id[:12] + "..." if media_id else "",
        "draft_add_ok": isinstance(draft, dict) and "media_id" in draft,
        "draft_response": {
            "media_id": (draft.get("media_id", "")[:12] + "...") if isinstance(draft, dict) and draft.get("media_id") else draft
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
