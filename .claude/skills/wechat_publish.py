#!/usr/bin/env python3
"""
微信公众号图文发布工具
========================
支持正文图片上传和简约排版优化

用法:
    python publish_with_images.py <文章目录路径>
    python publish_with_images.py /path/to/article-folder

文章目录结构:
    article-folder/
    ├── *.html           # 文章内容（必需）
    ├── cover.png/jpg    # 封面图片（必需）
    └── *.png/jpg        # 正文图片（可选，会自动上传并替换路径）
"""

import os
import sys
import re
import json
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeChatPublisher:
    """微信公众号发布器"""

    def __init__(self):
        self.app_id = os.getenv("WECHAT_APP_ID")
        self.app_secret = os.getenv("WECHAT_APP_SECRET")
        self.access_token = None

        if not self.app_id or not self.app_secret:
            raise Exception("请在 .env 中配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")

    def get_access_token(self) -> str:
        """获取 access_token"""
        if self.access_token:
            return self.access_token

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        resp = requests.get(url, timeout=10)
        result = resp.json()

        if "access_token" in result:
            self.access_token = result["access_token"]
            logger.info("access_token 获取成功")
            return self.access_token
        else:
            raise Exception(f"获取 access_token 失败: {result}")

    def upload_content_image(self, image_path: str) -> str:
        """上传正文图片，返回微信 URL"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"

        path = Path(image_path)
        mime_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif"}
        mime_type = mime_types.get(path.suffix.lower(), "image/png")

        with open(image_path, "rb") as f:
            files = {"media": (path.name, f, mime_type)}
            resp = requests.post(url, files=files, timeout=60)
            result = resp.json()

        if "url" in result:
            logger.info(f"正文图片上传成功: {path.name}")
            return result["url"]
        else:
            raise Exception(f"正文图片上传失败 {path.name}: {result}")

    def upload_cover_image(self, image_path: str) -> str:
        """上传封面图片（永久素材），返回 media_id"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"

        path = Path(image_path)
        mime_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
        mime_type = mime_types.get(path.suffix.lower(), "image/png")

        with open(image_path, "rb") as f:
            files = {"media": (path.name, f, mime_type)}
            resp = requests.post(url, files=files, timeout=60)
            result = resp.json()

        if "media_id" in result:
            logger.info(f"封面图片上传成功: {result['media_id']}")
            return result["media_id"]
        else:
            raise Exception(f"封面图片上传失败: {result}")

    def create_draft(self, title: str, content: str, thumb_media_id: str,
                     author: str = "", digest: str = "") -> str:
        """创建草稿"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

        article = {
            "articles": [{
                "title": title,
                "author": author or "Alex",
                "digest": digest or title[:50],
                "content": content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }]
        }

        json_data = json.dumps(article, ensure_ascii=False).encode('utf-8')
        resp = requests.post(url, data=json_data,
                           headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30)
        result = resp.json()

        if "media_id" in result:
            logger.info(f"草稿创建成功: {result['media_id']}")
            return result["media_id"]
        else:
            raise Exception(f"草稿创建失败: {result}")

    def publish(self, draft_media_id: str) -> str:
        """发布文章"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"

        resp = requests.post(url, json={"media_id": draft_media_id}, timeout=30)
        result = resp.json()

        if result.get("errcode") == 0:
            logger.info(f"发布成功: {result.get('publish_id')}")
            return result.get("publish_id")
        elif result.get("errcode") == 48001:
            logger.warning("发布API未授权，请手动到公众号后台发布草稿")
            return None
        else:
            logger.warning(f"发布失败: {result}")
            return None


def extract_title(html: str) -> str:
    """从 HTML 提取标题"""
    # 尝试 <title> 标签
    match = re.search(r'<title>(.+?)</title>', html, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 尝试 <h1> 标签
    match = re.search(r'<h1[^>]*>(.+?)</h1>', html, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r'<[^>]+>', '', match.group(1)).strip()

    return "微信公众号文章"


def extract_body(html: str) -> str:
    """提取 body 内容"""
    match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return html


def optimize_html_for_wechat(html: str) -> str:
    """优化 HTML 适配微信公众号"""

    # 1. 替换颜色名称为十六进制
    color_map = {
        r'\bwhite\b': '#ffffff',
        r'\bblack\b': '#000000',
        r'\bred\b': '#ff0000',
        r'\bblue\b': '#0000ff',
        r'\bgreen\b': '#008000',
        r'\bgray\b': '#808080',
        r'\bgrey\b': '#808080',
    }
    for pattern, replacement in color_map.items():
        html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)

    # 2. 清理列表标签之间的空白
    html = re.sub(r'<ul([^>]*)>\s+<li', r'<ul\1><li', html)
    html = re.sub(r'</li>\s+<li', r'</li><li', html)
    html = re.sub(r'</li>\s+</ul>', r'</li></ul>', html)
    html = re.sub(r'<ol([^>]*)>\s+<li', r'<ol\1><li', html)
    html = re.sub(r'</li>\s+</ol>', r'</li></ol>', html)

    # 3. 清理表格标签之间的空白
    html = re.sub(r'<table([^>]*)>\s+', r'<table\1>', html)
    html = re.sub(r'<thead>\s+', r'<thead>', html)
    html = re.sub(r'<tbody>\s+', r'<tbody>', html)
    html = re.sub(r'<tr([^>]*)>\s+', r'<tr\1>', html)
    html = re.sub(r'</tr>\s+', r'</tr>', html)
    html = re.sub(r'</th>\s+<th', r'</th><th', html)
    html = re.sub(r'</td>\s+<td', r'</td><td', html)

    # 4. 确保图片样式
    def fix_img_style(match):
        img_tag = match.group(0)
        if 'style=' not in img_tag:
            return img_tag.replace('<img', '<img style="width: 100%; height: auto; border-radius: 8px; display: block; margin: 20px auto;"')
        return img_tag

    html = re.sub(r'<img[^>]+>', fix_img_style, html)

    return html


def find_images(directory: Path) -> dict:
    """查找目录中的所有图片"""
    images = {"cover": None, "content": []}

    for ext in ['png', 'jpg', 'jpeg', 'gif']:
        # 查找封面
        for cover_name in ['cover', 'Cover', 'COVER']:
            cover_path = directory / f"{cover_name}.{ext}"
            if cover_path.exists():
                images["cover"] = cover_path
                break

        # 查找其他图片（正文图片）
        for img_path in directory.glob(f"*.{ext}"):
            if img_path.name.lower().startswith('cover'):
                continue
            if img_path not in images["content"]:
                images["content"].append(img_path)

    return images


def publish_article(article_dir: str) -> dict:
    """发布文章到微信公众号"""

    article_path = Path(article_dir)
    if not article_path.is_dir():
        raise Exception(f"目录不存在: {article_dir}")

    # 1. 查找 HTML 文件
    html_files = list(article_path.glob("*.html"))
    if not html_files:
        raise Exception(f"未找到 HTML 文件: {article_dir}")

    html_file = html_files[0]
    html_content = html_file.read_text(encoding='utf-8')
    logger.info(f"读取文章: {html_file.name}")

    # 2. 提取标题
    title = extract_title(html_content)
    logger.info(f"文章标题: {title}")

    # 3. 查找图片
    images = find_images(article_path)
    if not images["cover"]:
        raise Exception("未找到封面图片 (cover.png/jpg)")

    logger.info(f"封面图片: {images['cover'].name}")
    logger.info(f"正文图片: {[img.name for img in images['content']]}")

    # 4. 初始化发布器
    publisher = WeChatPublisher()

    # 5. 上传正文图片并替换路径
    body_content = extract_body(html_content)
    image_url_map = {}

    for img_path in images["content"]:
        try:
            url = publisher.upload_content_image(str(img_path))
            image_url_map[img_path.name] = url
            # 替换 HTML 中的本地路径
            body_content = body_content.replace(f'src="{img_path.name}"', f'src="{url}"')
            body_content = body_content.replace(f"src='{img_path.name}'", f'src="{url}"')
        except Exception as e:
            logger.warning(f"上传图片失败 {img_path.name}: {e}")

    # 6. 上传封面图片
    thumb_media_id = publisher.upload_cover_image(str(images["cover"]))

    # 7. 优化 HTML
    body_content = optimize_html_for_wechat(body_content)
    logger.info(f"HTML 内容长度: {len(body_content)} 字符")

    # 8. 创建草稿
    draft_media_id = publisher.create_draft(
        title=title,
        content=body_content,
        thumb_media_id=thumb_media_id,
        digest=title[:100]
    )

    # 9. 尝试发布
    publish_id = publisher.publish(draft_media_id)

    return {
        "title": title,
        "html_file": html_file.name,
        "cover_image": images["cover"].name,
        "content_images": list(image_url_map.keys()),
        "thumb_media_id": thumb_media_id,
        "draft_media_id": draft_media_id,
        "publish_id": publish_id,
        "status": "published" if publish_id else "draft_created"
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n错误: 请提供文章目录路径")
        print("示例: python publish_with_images.py /path/to/article-folder")
        sys.exit(1)

    article_dir = sys.argv[1]

    try:
        result = publish_article(article_dir)

        print("\n" + "=" * 50)
        print("发布结果")
        print("=" * 50)
        print(f"标题: {result['title']}")
        print(f"HTML 文件: {result['html_file']}")
        print(f"封面图片: {result['cover_image']}")
        print(f"正文图片: {', '.join(result['content_images']) or '无'}")
        print(f"草稿 ID: {result['draft_media_id']}")
        print(f"状态: {result['status']}")

        if result['status'] == 'draft_created':
            print("\n提示: 请登录微信公众平台手动发布草稿")
            print("地址: https://mp.weixin.qq.com/")

    except Exception as e:
        logger.error(f"发布失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
