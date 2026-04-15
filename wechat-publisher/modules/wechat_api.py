# -*- coding: utf-8 -*-
"""
微信公众号 API 对接模块
- 账号绑定
- 草稿创建
- 图文发布
- 素材管理（图片上传）
"""

import os
import json
import time
import base64
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger('WechatPublisher.WeChatPublisher')


class WeChatPublisher:
    """微信公众号发布器"""
    
    # API 基础地址
    BASE_URL = "https://api.weixin.qq.com"
    
    def __init__(self, config: dict):
        self.config = config
        self.appid = config.get('WECHAT_APPID', '')
        self.secret = config.get('WECHAT_SECRET', '')
        self.token = config.get('WECHAT_TOKEN', '')
        
        self.access_token = None
        self.token_expires_at = 0
        
        # 已上传的素材缓存 {md5: media_id}
        self._material_cache = {}
        
        logger.info(f"微信公众号发布器初始化 | AppID: {'***' + self.appid[-4:] if self.appid else '未设置'}")
    
    def is_configured(self) -> bool:
        """检查是否已完成配置"""
        return bool(self.appid and self.secret)
    
    # ==================== Access Token ====================
    
    def _get_access_token(self) -> str:
        """获取/刷新 access_token"""
        now = time.time()
        
        if self.access_token and now < self.token_expires_at - 300:  # 提前5分钟刷新
            return self.access_token
        
        if not self.appid or not self.secret:
            raise ValueError("微信 AppID 或 Secret 未配置，请在 config.yaml 中填写")
        
        url = f"{self.BASE_URL}/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.appid,
            'secret': self.secret
        }
        
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        
        if 'access_token' in data:
            self.access_token = data['access_token']
            self.token_expires_at = now + data.get('expires_in', 7200)
            logger.info(f"access_token 刷新成功")
            return self.access_token
        else:
            raise Exception(f"获取 access_token 失败: {data}")
    
    # ==================== 素材上传 ====================
    
    def upload_image(self, image_path: str) -> str:
        """
        上传永久图片素材
        返回: media_id (用于在文章中引用)
        """
        if image_path in self._material_cache:
            logger.debug(f"图片命中缓存: {image_path}")
            return self._material_cache[image_path]
        
        token = self._get_access_token()
        url = f"{self.BASE_URL}/cgi-bin/material/add_material?access_token={token}&type=image"
        
        with open(image_path, 'rb') as f:
            files = {
                'media': (
                    os.path.basename(image_path),
                    f,
                    'image/png' if image_path.endswith('.png') else 'image/jpeg'
                )
            }
            resp = requests.post(url, files=files, timeout=60)
        
        data = resp.json()
        
        if 'media_id' in data:
            self._material_cache[image_path] = data['media_id']
            url = data.get('url', '')
            logger.info(f"图片上传成功: {os.path.basename(image_path)} -> {data['media_id']}")
            return data['media_id']
        else:
            raise Exception(f"图片上传失败: {data}")
    
    def upload_temp_image(self, image_path: str) -> str:
        """
        上传正文配图并返回可嵌入图文消息 HTML 的 URL。

        注意：
        - 公众号图文正文里的 <img src="..."> 不能使用 media/upload 返回的 media_id
        - 必须使用 uploadimg 接口，接口成功时返回 url
        - 该方法名为兼容旧代码暂时保留，实际用途是“上传图文正文图片”
        """
        token = self._get_access_token()
        url = f"{self.BASE_URL}/cgi-bin/media/uploadimg?access_token={token}"

        with open(image_path, 'rb') as f:
            files = {
                'media': (
                    os.path.basename(image_path),
                    f,
                    'image/png' if image_path.endswith('.png') else 'image/jpeg'
                )
            }
            resp = requests.post(url, files=files, timeout=60)

        data = resp.json()

        if data.get('url'):
            logger.info(f"正文图片上传成功: {data['url']}")
            return data['url']
        else:
            raise Exception(f"正文图片上传失败: {data}")
    
    # ==================== 文章发布 ====================
    
    def publish_article(self, article: Dict, publish_now: bool = False) -> Dict:
        """
        发布文章到公众号
        
        Args:
            article: 文章数据字典
            publish_now: True=立即发布, False=保存为草稿
            
        Returns:
            发布结果
        """
        token = self._get_access_token()
        
        # 构建文章 HTML
        html_content = self._build_article_html(article)
        
        # 上传封面图
        cover_media_id = ''
        cover_path = article.get('cover_image')
        if cover_path and os.path.exists(cover_path):
            try:
                cover_media_id = self.upload_image(cover_path)
            except Exception as e:
                logger.warning(f"封面上传失败: {e}")
        
        # 上传正文中的图片并替换 URL
        for para in article.get('paragraphs', []) or article.get('sections', []):
            img_path = para.get('image_path')
            if img_path and os.path.exists(img_path):
                try:
                    img_url = self.upload_temp_image(img_path)
                    # 在 HTML 中替换占位符
                    html_content = html_content.replace(
                        f'__IMAGE_PLACEHOLDER_{para["index"]}__',
                        img_url
                    )
                except Exception as e:
                    logger.warning(f"段落图片{para['index']}上传失败: {e}")
        
        # 构建请求体
        article_data = {
            "articles": [{
                "title": article['title'],
                # 作者名：必须非空才能让原创声明(copyright_stat=1)自动生效
                # 空字符串会导致"未声明"，需要手动点
                "author": "往前看的月半子",
                "digest": article.get('summary', ''),
                "content": html_content,
                "thumb_media_id": cover_media_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 0,
                "content_source_url": "",
                "copyright_stat": 1,  # 1=原创声明
            }]
        }
        
        if publish_now:
            # 免费订阅号不支持直接发布，只能通过草稿+群发接口
            result = self._publish_free(account_data)
        else:
            result = self._save_draft(token, article_data)
        
        logger.info(f"文章{'发布' if publish_now else '保存草稿'}完成: {article['title']}")
        return result
    
    def _build_article_html(self, article: Dict) -> str:
        """构建公众号兼容的富文本 HTML"""
        paragraphs = article.get('paragraphs', []) or article.get('sections', [])
        
        html_parts = ['<section style="max-width:100%;padding:0 15px;">']
        
        for para in paragraphs:
            text = para['text'].replace('\n', '<br/>')
            
            # 将 **粗体** 文本转为带高亮样式的 <strong> 标签
            import re
            def _highlight_bold(m):
                return f'<strong style="color:#c0392b;font-weight:bold;background:linear-gradient(transparent 60%,#ffeaa7 0);">{m.group(1)}</strong>'
            text = re.sub(r'\*\*(.+?)\*\*', _highlight_bold, text)
            
            # 段落样式
            style = """font-size:16px;
line-height:1.8;
color:#333333;
margin-bottom:20px;
letter-spacing:0.5px;
text-align:justify;"""
            
            html_parts.append(f'<p style="{style}">{text}</p>')
            
            # 插入配图
            if para.get('needs_image') and para.get('image_path'):
                img_style = "width:100%;border-radius:8px;margin-bottom:20px;display:block;"
                
                # 先用占位符，后续替换为实际URL
                img_html = f'''<p>
  <img src="__IMAGE_PLACEHOLDER_{para['index']}__" 
       style="{img_style}" 
       mode="widthFix"/>
</p>'''
                html_parts.append(img_html)
        
        # 结尾关注引导
        cta_style = """background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
color:white;padding:25px 20px;border-radius:12px;text-align:center;margin-top:30px;"""
        html_parts.append(f'''
<section style="{cta_style}">
  <p style="color:white;font-size:18px;font-weight:bold;margin-bottom:10px;">👇 觉得有用就关注一下吧 👇</p>
  <p style="color:rgba(255,255,255,0.9);font-size:14px;">每天分享最新科技资讯和深度解读</p>
</section>''')
        
        html_parts.append('</section>')
        
        return '\n'.join(html_parts)
    
    def _save_draft(self, token: str, articles_data: dict) -> Dict:
        """保存为草稿"""
        url = f"{self.BASE_URL}/cgi-bin/draft/add?access_token={token}"
        # 使用 ensure_ascii=False 防止中文字段（标题/摘要/文件名）被转义为 \uXXXX
        resp = requests.post(
            url,
            data=json.dumps(articles_data, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8'},
            timeout=30
        )
        return resp.json()
    
    def _publish_free(self, token: str, media_id: str) -> Dict:
        """
        通过草稿群发接口发布
        注意：免费订阅号每天只能群发1次
        """
        # 先获取所有用户群组（all）
        group_url = f"{self.BASE_URL}/cgi-bin/groups/get?access_token={token}"
        groups_resp = requests.get(group_url, timeout=15)
        groups = groups_resp.json().get('groups', [])
        
        # 找到全部用户组
        to_all_group = None
        for g in groups:
            if g.get('name') == '全部用户':
                to_all_group = g
                break
        
        if not to_all_group:
            raise Exception("未找到用户群组信息")
        
        # 发送群发消息
        send_url = f"{self.BASE_URL}/cgi-bin/freepublish/submit?access_token={token}"
        send_data = {
            "media_id": media_id,
        }
        resp = requests.post(send_url, json=send_data, timeout=30)
        
        return resp.json()
    
    def get_publish_status(self, publish_id: str) -> Dict:
        """查询发布状态"""
        token = self._get_access_token()
        url = f"{self.BASE_URL}/cgi-bin/freepublish/get?access_token={token}"
        resp = requests.post(url, json={"publish_id": publish_id}, timeout=15)
        return resp.json()


if __name__ == '__main__':
    import yaml
    
    with open('../config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    publisher = WeChatPublisher(config)
    
    print(f"\n配置状态: {'✅ 已配置' if publisher.is_configured() else '❌ 未配置'}")
    print(f"AppID: {'已设置' if config.get('WECHAT_APPID') else '未设置'}")
    print(f"Secret: {'已设置' if config.get('WECHAT_SECRET') else '未设置'}")
