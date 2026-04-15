# -*- coding: utf-8 -*-
"""
飞书机器人API客户端
支持：获取Token、发送文本/富文本/卡片消息、上传图片
"""

import json
import time
import hashlib
import base64
import requests
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "feishu_bots_config.json"


def load_config():
    """加载飞书机器人配置"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class FeishuBot:
    """单个飞书机器人的API客户端"""

    def __init__(self, app_id: str, app_secret: str, name: str = ""):
        self.app_id = app_id
        self.app_secret = app_secret
        self.name = name
        self._token = None
        self._token_expire = 0
        # 飞书API基础地址
        self.base_url = "https://open.feishu.cn/open-apis"

    def get_token(self) -> str:
        """获取或复用 tenant_access_token（自动缓存，过期前1分钟刷新）"""
        if self._token and time.time() < self._token_expire:
            return self._token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }, timeout=10)
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"获取Token失败: {data}")
        self._token = data["tenant_access_token"]
        # token有效期2小时，提前60秒刷新
        self._token_expire = time.time() + data["expire"] - 60
        return self._token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json"
        }

    def send_text(self, chat_id: str, content: str) -> dict:
        """
        发送纯文本消息到指定群聊
        chat_id: 群聊ID（open_chat_id）
        content: 消息内容（支持部分Markdown）
        """
        url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
        body = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }
        resp = requests.post(url, headers=self._headers(), json=body, timeout=10)
        result = resp.json()
        if result.get("code") != 0:
            print(f"[{self.name}] 发送消息失败: {result}")
        return result

    def send_post(self, chat_id: str, title: str,
                  content_lines: list[str]) -> dict:
        """
        发送富文本消息（带标题的多段落）
        content_lines: 每行一个段落字符串
        """
        # 构建post格式的内容结构
        post_content = {
            "zh_cn": {
                "title": title,
                "content": [
                    [{"tag": "text", "text": line}]
                    for line in content_lines
                ]
            }
        }

        url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
        body = {
            "receive_id": chat_id,
            "msg_type": "post",
            "content": json.dumps(post_content)
        }
        resp = requests.post(url, headers=self._headers(), json=body, timeout=10)
        result = resp.json()
        if result.get("code") != 0:
            print(f"[{self.name}] 发送富文本失败: {result}")
        return result

    def send_interactive(self, chat_id: str, card_content: dict) -> dict:
        """
        发送交互卡片消息（最灵活，支持按钮、进度条等）
        card_content: 卡片JSON（参考飞书卡片文档）
        """
        url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
        body = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content)
        }
        resp = requests.post(url, headers=self._headers(), json=body, timeout=10)
        result = resp.json()
        if result.get("code") != 0:
            print(f"[{self.name}] 发送卡片失败: {result}")
        return result

    def upload_image(self, image_path: str) -> str | None:
        """
        上传图片到飞书，返回 image_key
        image_path: 本地图片文件路径
        返回: image_key 或 None(失败时)
        """
        try:
            with open(image_path, "rb") as f:
                img_data = f.read()

            url = f"{self.base_url}/image/v4/upload"
            headers = {"Authorization": f"Bearer {self.get_token()}"}

            files = {
                "image": (
                    Path(image_path).name,
                    img_data,
                    "image/png"
                )
            }
            form_data = {
                "image_type": "message"
            }
            resp = requests.post(
                url, headers=headers,
                files=form_data, data=form_data, timeout=30
            )
            result = resp.json()
            if result.get("code") == 0:
                return result["data"]["image_key"]
            else:
                print(f"[{self.name}] 上传图片失败: {result}")
                return None
        except Exception as e:
            print(f"[{self.name}] 上传图片异常: {e}")
            return None

    def send_image_msg(self, chat_id: str, image_key: str) -> dict:
        """发送图片消息到群聊"""
        url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
        body = {
            "receive_id": chat_id,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }
        resp = requests.post(url, headers=self._headers(), json=body, timeout=10)
        return resp.json()

    # ---- 便捷方法 -----

    def status_start(self, chat_id: str, task_name: str):
        """发送「开始工作」状态消息"""
        self.send_text(chat_id, f"▸ 开始执行：{task_name}...")

    def status_progress(
        self, chat_id: str, current: int, total: int,
        detail: str = ""
    ):
        """发送进度更新"""
        pct = int(current / max(total, 1) * 100)
        bar_len = 12
        filled = int(pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)

        msg = (
            f"▸ 进度: [{bar}] {pct}% "
            f"({current}/{total})"
        )
        if detail:
            msg += f"\n  {detail}"
        self.send_text(chat_id, msg)

    def status_ok(self, chat_id: str, summary: str, detail: str = ""):
        """发送成功完成状态"""
        msg = f"✅ {summary}"
        if detail:
            msg += f"\n   {detail}"
        self.send_text(chat_id, msg)

    def status_error(self, chat_id: str, error: str):
        """发送错误信息"""
        self.send_text(chat_id, f"❌ 错误: {error}")

    def send_separator(self, chat_id: str, title: str = ""):
        """发送分隔线"""
        line = "═" * 28
        msg = line if not title else f"{line}\n  {title}"
        self.send_text(chat_id, msg)


class FeishuTeam:
    """
    AI团队管理器 — 管理所有飞书机器人，
    提供统一的群发、任务报告等功能
    """

    def __init__(self):
        config = load_config()
        self.config = config
        self.bots: dict[str, FeishuBot] = {}
        bots_data = config.get("bots", [])
        # 支持列表或字典格式
        if isinstance(bots_data, list):
            for info in bots_data:
                self.bots[info.get("role", info["name"])] = FeishuBot(
                    app_id=info["app_id"],
                    app_secret=info["app_secret"],
                    name=info["name"]
                )
        else:
            for key, info in bots_data.items():
                self.bots[key] = FeishuBot(
                    app_id=info["app_id"],
                    app_secret=info["app_secret"],
                    name=info["name"]
                )
        self.chat_id: str | None = None

    @classmethod
    def from_config(cls) -> "FeishuTeam":
        """从配置文件创建团队实例"""
        return cls()

    def set_chat_id(self, chat_id: str):
        """设置目标群聊ID（所有机器人往这个群里发）"""
        self.chat_id = chat_id
        return self

    def get_bot(self, role: str) -> FeishuBot:
        """按角色名获取机器人实例"""
        if role not in self.bots:
            raise KeyError(f"未知的AI角色: {role}, 可用: {list(self.bots.keys())}")
        return self.bots[role]

    # ---- 团队级操作 ----

    def broadcast(self, message: str, exclude_roles: list[str] | None = None):
        """所有机器人广播同一条消息（通常用主控即可）"""
        self.coordinator.send_text(self.chat_id, message)

    def announce_task_start(self, topic: str):
        """主控宣布新任务开始"""
        if not self.chat_id:
            return
        now = time.strftime("%H:%M")
        sep = "═" * 28
        self.coordinator.send_text(
            self.chat_id,
            f"{sep}\n🚀 新任务启动 [{now}]\n"
            f"📌 话题: {topic}"
        )

    def announce_task_done(
        self, title: str, word_count: int,
        images: int, ai_score: int
    ):
        """主控宣布任务完成"""
        if not self.chat_id:
            return
        sep = "═" * 28
        status = "✅通过" if ai_score < 40 else ("⚠️模糊" if ai_score <= 70 else "❌风险")
        self.coordinator.send_text(
            self.chat_id,
            f"{sep}\n📦 任务完成！\n\n"
            f"标题: {title}\n"
            f"字数: {word_count}字 | 配图: {images}张\n"
            f"AI评分: {ai_score}分 ({status})"
        )

    def announce_summary(self, today_count: int, success_count: int):
        """宣布每日汇总"""
        if not self.chat_id:
            return
        sep = "═" * 28
        now = time.strftime("%H:%M")
        self.coordinator.send_text(
            self.chat_id,
            f"{sep}\n📊 今日汇总 [{now}]\n\n"
            f"计划产出: {today_count}篇\n"
            f"实际完成: {success_count}篇\n"
            f"成功率: {int(success_count/max(today_count,1)*100)}%"
        )

    # ---- 属性快捷访问 ----

    @property
    def hot_fetcher(self) -> FeishuBot:
        return self.bots["hot_fetcher"]

    @property
    def writer(self) -> FeishuBot:
        return self.bots["writer"]

    @property
    def artist(self) -> FeishuBot:
        return self.bots["artist"]

    @property
    def reviewer(self) -> FeishuBot:
        return self.bots["reviewer"]

    @property
    def coordinator(self) -> FeishuBot:
        return self.bots["coordinator"]

    def list_bots_info(self) -> list[dict]:
        """返回所有机器人的基本信息列表"""
        return [
            {"key": k, "name": b.name, "app_id": b.app_id}
            for k, b in self.bots.items()
        ]


# ---- 测试入口 ----
if __name__ == "__main__":
    team = TeamManager.from_config()
    print("=== 飞书AI团队 ===")
    for info in team.list_bots_info():
        print(f"  {info['name']}: {info['app_id'][:16]}...")
    print(f"\n共 {len(team.bots)} 个机器人就绪")

    # 测试获取token
    print("\n测试Token获取...")
    token = team.hot_fetcher.get_token()
    print(f"热点猎手 Token: {token[:20]}...✅")
