# -*- coding: utf-8 -*-
import json
from pathlib import Path

import requests
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
TIMEOUT = 15


def mask(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - keep * 2) + value[-keep:]


def main():
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    appid = (cfg.get("WECHAT_APPID") or "").strip()
    secret = (cfg.get("WECHAT_SECRET") or "").strip()

    result = {
        "configured": bool(appid and secret),
        "appid_masked": mask(appid),
        "secret_masked": mask(secret),
        "token_test": None,
        "draft_api_test": None,
        "material_api_test": None,
    }

    if not result["configured"]:
        result["error"] = "WECHAT_APPID / WECHAT_SECRET 未配置完整"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    token_resp = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": appid,
            "secret": secret,
        },
        timeout=TIMEOUT,
    )
    token_data = token_resp.json()

    if "access_token" not in token_data:
        result["token_test"] = {
            "ok": False,
            "response": token_data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    access_token = token_data["access_token"]
    result["token_test"] = {
        "ok": True,
        "expires_in": token_data.get("expires_in"),
        "token_prefix": access_token[:10] + "...",
    }

    draft_resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}",
        json={"offset": 0, "count": 1, "no_content": 1},
        timeout=TIMEOUT,
    )
    draft_data = draft_resp.json()
    result["draft_api_test"] = {
        "ok": "errcode" not in draft_data or draft_data.get("errcode") == 0,
        "item_count": len(draft_data.get("item", [])) if isinstance(draft_data.get("item"), list) else 0,
        "total_count": draft_data.get("total_count"),
        "response": draft_data if draft_data.get("errcode") else {k: v for k, v in draft_data.items() if k != "item"},
    }

    material_resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={access_token}",
        json={"type": "image", "offset": 0, "count": 1},
        timeout=TIMEOUT,
    )
    material_data = material_resp.json()
    result["material_api_test"] = {
        "ok": "errcode" not in material_data or material_data.get("errcode") == 0,
        "item_count": len(material_data.get("item", [])) if isinstance(material_data.get("item"), list) else 0,
        "total_count": material_data.get("total_count"),
        "response": material_data if material_data.get("errcode") else {k: v for k, v in material_data.items() if k != "item"},
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
