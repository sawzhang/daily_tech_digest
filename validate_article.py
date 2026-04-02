#!/usr/bin/env python3
"""
微信公众号 HTML 格式校验器
基于 daily_tech_digest 的 _clean_html_for_wechat 规则 + 额外微信兼容性检查
"""

import re
import sys
from pathlib import Path
from collections import Counter

def validate_wechat_html(html: str) -> list:
    """返回所有检测到的问题列表"""
    issues = []

    # ==================== 1. 微信禁止/不支持的特性 ====================

    # 1.1 颜色名称（微信要求十六进制）
    color_names = re.findall(r'(?:color|background|border)[^;]*:\s*(white|black|red|blue|green|gray|grey|orange|purple|yellow|pink)\b', html, re.IGNORECASE)
    if color_names:
        issues.append(f"P1-颜色名称: 发现 {len(color_names)} 处使用颜色名称而非十六进制: {Counter(color_names).most_common(5)}")

    # 1.2 position: absolute/fixed（微信支持不稳定）
    abs_pos = re.findall(r'position\s*:\s*(absolute|fixed)', html, re.IGNORECASE)
    if abs_pos:
        issues.append(f"P1-定位: 发现 {len(abs_pos)} 处 position:{abs_pos[0]}，微信渲染不稳定")

    # 1.3 display: flex（微信部分支持，旧版不行）
    flex_count = len(re.findall(r'display\s*:\s*flex', html, re.IGNORECASE))
    if flex_count > 0:
        issues.append(f"P2-Flex: 发现 {flex_count} 处 display:flex，微信旧版客户端可能不支持（建议保留但需测试）")

    # 1.4 CSS 变量（微信不支持）
    css_vars = re.findall(r'var\(--', html)
    if css_vars:
        issues.append(f"P1-CSS变量: 发现 {len(css_vars)} 处 CSS 变量，微信不支持")

    # 1.5 @media 查询（微信不支持）
    media_queries = re.findall(r'@media', html)
    if media_queries:
        issues.append(f"P2-MediaQuery: 发现 {len(media_queries)} 处 @media 查询，微信会忽略")

    # 1.6 外部资源引用
    ext_resources = re.findall(r'(?:src|href)\s*=\s*["\']https?://', html, re.IGNORECASE)
    if ext_resources:
        issues.append(f"P2-外部资源: 发现 {len(ext_resources)} 处外部 URL 引用，微信可能屏蔽非白名单域名")

    # 1.7 JavaScript
    js_tags = re.findall(r'<script', html, re.IGNORECASE)
    if js_tags:
        issues.append(f"P0-JavaScript: 发现 <script> 标签，微信会完全过滤！")

    # 1.8 iframe
    iframes = re.findall(r'<iframe', html, re.IGNORECASE)
    if iframes:
        issues.append(f"P0-iframe: 发现 <iframe> 标签，微信不支持！")

    # ==================== 2. 列表标签间距（微信空列表项问题） ====================

    list_gaps = re.findall(r'</li>\s+<li', html)
    if list_gaps:
        issues.append(f"P2-列表间距: 发现 {len(list_gaps)} 处 </li> 和 <li> 之间有空白，可能导致微信显示空列表项")

    ul_gaps = re.findall(r'<ul[^>]*>\s+<li', html)
    if ul_gaps:
        issues.append(f"P2-UL间距: 发现 {len(ul_gaps)} 处 <ul> 和 <li> 之间有空白")

    # ==================== 3. 表格检查 ====================

    # 3.1 表格是否过宽
    tables = re.findall(r'<table[^>]*>', html)
    for t in tables:
        if 'width' not in t and 'width:' not in t:
            issues.append(f"P2-表格宽度: 表格缺少 width 设置，可能在手机上溢出")
            break

    # 3.2 表头 th 是否有单独的背景色（微信不支持 tr 级背景）
    ths_without_bg = re.findall(r'<th(?!ead)(?![^>]*background)[^>]*>', html)
    if ths_without_bg:
        issues.append(f"P2-表头背景: 发现 {len(ths_without_bg)} 个 <th> 缺少 background 样式（微信不支持 tr 级背景）")

    # ==================== 4. 内联样式 vs <style> 标签 ====================

    has_style_tag = bool(re.search(r'<style', html))
    inline_styles = len(re.findall(r'style="', html))

    if has_style_tag:
        # 微信公众号支持 <style> 标签，但部分第三方编辑器会剥离
        issues.append(f"INFO-Style标签: 使用了 <style> 标签（{inline_styles} 处内联样式），微信原生编辑器支持，第三方工具可能不支持")

    # ==================== 5. 图片检查 ====================

    imgs = re.findall(r'<img[^>]*>', html)
    for img in imgs:
        if 'width' not in img and 'max-width' not in img:
            issues.append(f"P2-图片宽度: 图片缺少 width/max-width，可能超出屏幕")
            break

    # ==================== 6. 字体检查 ====================

    fonts = re.findall(r'font-family\s*:\s*([^;}"]+)', html)
    for font in fonts:
        if 'PingFang' not in font and 'apple-system' not in font and 'Helvetica' not in font:
            if 'SF Mono' in font or 'Fira Code' in font or 'Menlo' in font:
                continue  # 代码字体 OK
            issues.append(f"P3-字体: 字体 '{font.strip()[:30]}' 可能在部分安卓设备不可用")
            break

    # ==================== 7. 内容长度检查 ====================

    # 去除标签后的纯文本长度
    text_only = re.sub(r'<[^>]+>', '', html)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    char_count = len(text_only)

    if char_count < 500:
        issues.append(f"P1-内容过短: 纯文本仅 {char_count} 字，公众号推荐 1500-2500 字")
    elif char_count > 5000:
        issues.append(f"P3-内容偏长: 纯文本 {char_count} 字，阅读时间较长，考虑精简")
    else:
        issues.append(f"INFO-字数: 纯文本约 {char_count} 字，阅读时间约 {char_count // 300} 分钟 ✓")

    # ==================== 8. 代码块检查 ====================

    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', html, re.DOTALL)
    for i, block in enumerate(code_blocks):
        if 'word-wrap' not in block and 'word-break' not in block and 'white-space: pre-wrap' not in block:
            issues.append(f"P2-代码溢出: 第 {i+1} 个代码块缺少 word-wrap/white-space:pre-wrap，长行会水平溢出")
            break

    # ==================== 9. 微信特殊限制 ====================

    # 9.1 checked html 总大小
    html_size = len(html.encode('utf-8'))
    if html_size > 100000:
        issues.append(f"P1-体积: HTML 大小 {html_size // 1024}KB，超过微信 100KB 草稿限制")
    elif html_size > 50000:
        issues.append(f"P3-体积: HTML 大小 {html_size // 1024}KB，接近限制但可用")
    else:
        issues.append(f"INFO-体积: HTML 大小 {html_size // 1024}KB ✓")

    # 9.2 嵌套深度
    max_depth = 0
    depth = 0
    for char in html:
        if char == '<':
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == '>':
            depth = max(0, depth - 1)
    if max_depth > 30:
        issues.append(f"P3-嵌套: HTML 嵌套深度 {max_depth}，微信可能截断深层嵌套")

    return issues


def main():
    article_path = Path("/Volumes/ExternalSSD/code/claude-code-book/output/wechat-article-v2.html")

    if not article_path.exists():
        print(f"ERROR: 文件不存在: {article_path}")
        sys.exit(1)

    html = article_path.read_text(encoding="utf-8")

    print("=" * 60)
    print("微信公众号 HTML 格式校验报告")
    print(f"文件: {article_path.name}")
    print(f"大小: {len(html)} bytes")
    print("=" * 60)
    print()

    issues = validate_wechat_html(html)

    # 分类输出
    p0 = [i for i in issues if i.startswith("P0")]
    p1 = [i for i in issues if i.startswith("P1")]
    p2 = [i for i in issues if i.startswith("P2")]
    p3 = [i for i in issues if i.startswith("P3")]
    info = [i for i in issues if i.startswith("INFO")]

    if p0:
        print("🔴 P0 — 致命（微信会过滤/报错）:")
        for i in p0: print(f"  {i}")
        print()

    if p1:
        print("🟠 P1 — 严重（显示异常）:")
        for i in p1: print(f"  {i}")
        print()

    if p2:
        print("🟡 P2 — 警告（可能有问题）:")
        for i in p2: print(f"  {i}")
        print()

    if p3:
        print("🔵 P3 — 建议（优化项）:")
        for i in p3: print(f"  {i}")
        print()

    if info:
        print("✅ INFO — 通过:")
        for i in info: print(f"  {i}")
        print()

    # 总结
    total_issues = len(p0) + len(p1) + len(p2) + len(p3)
    print("=" * 60)
    if p0:
        print(f"❌ 校验失败: {len(p0)} 个致命问题必须修复")
    elif p1:
        print(f"⚠️  校验通过（有风险）: {len(p1)} 个严重问题建议修复")
    elif p2:
        print(f"✅ 校验通过: {len(p2)} 个警告，{len(p3)} 个建议")
    else:
        print(f"✅ 校验完美通过!")
    print(f"   总计: P0={len(p0)} P1={len(p1)} P2={len(p2)} P3={len(p3)} INFO={len(info)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
