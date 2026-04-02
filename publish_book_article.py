#!/usr/bin/env python3
"""
发布《深入理解 Claude Code 源码》公众号文章
使用 daily_tech_digest 的 WeChatPublisher 能力
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from tech_digest_agent import WeChatPublisher
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 读取 v2 文章 HTML
    article_path = Path("/Volumes/ExternalSSD/code/claude-code-book/output/wechat-article-v2.html")

    if not article_path.exists():
        logger.error(f"文章文件不存在: {article_path}")
        return

    html_full = article_path.read_text(encoding="utf-8")

    # 提取 <body> 内的内容（公众号只需要 body 内容）
    import re
    body_match = re.search(r'<body>(.*?)</body>', html_full, re.DOTALL)
    if body_match:
        html_content = body_match.group(1).strip()
    else:
        html_content = html_full

    # 提取 <style> 并内联（公众号需要内联样式，但也支持 <style> 标签）
    style_match = re.search(r'<style>(.*?)</style>', html_full, re.DOTALL)
    if style_match:
        # 微信公众号支持 style 标签，直接拼接
        html_content = f"<style>{style_match.group(1)}</style>\n{html_content}"

    logger.info(f"文章 HTML 长度: {len(html_content)} 字符")

    # 发布
    title = "用 6 个 AI Agent，一晚上写了本 12 万字的开源技术书"
    keywords = ["Claude Code", "AI Agent", "源码分析", "开源"]

    publisher = WeChatPublisher()

    try:
        result = publisher.run(
            html_content=html_content,
            title=title,
            keywords=keywords
        )

        logger.info(f"发布结果: {result}")

        if result["status"] == "published":
            logger.info("文章已成功发布!")
        elif result["status"] == "draft_created":
            logger.info("草稿已创建，请到公众号后台手动发布")
            logger.info(f"草稿 media_id: {result['draft_media_id']}")

    except Exception as e:
        logger.error(f"发布失败: {e}")
        logger.info("请检查:")
        logger.info("  1. WECHAT_APP_ID 和 WECHAT_APP_SECRET 是否正确")
        logger.info("  2. 服务器 IP 是否在公众号白名单中")
        logger.info("  3. access_token 是否过期")
        raise

if __name__ == "__main__":
    main()
