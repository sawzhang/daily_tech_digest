#!/usr/bin/env python3
"""将 CSS class 转为内联 style，适配微信公众号"""

import re
from pathlib import Path

def inline_css(html: str) -> str:
    """提取 <style> 中的 CSS 规则，内联到对应元素"""

    # 1. 提取 <style> 内容
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    if not style_match:
        return html

    css_text = style_match.group(1)

    # 2. 解析 CSS 规则（简单解析，只处理 class 选择器）
    rules = {}
    for match in re.finditer(r'\.([a-zA-Z0-9_-]+)\s*\{([^}]+)\}', css_text):
        cls_name = match.group(1)
        props = match.group(2).strip().replace('\n', ' ')
        # 压缩多余空格
        props = re.sub(r'\s+', ' ', props).strip()
        rules[cls_name] = props

    # 也处理标签选择器 (p, strong, body, img)
    tag_rules = {}
    for match in re.finditer(r'(?:^|\n)\s*([a-zA-Z]+)\s*\{([^}]+)\}', css_text):
        tag = match.group(1).strip()
        if tag in ('body', 'p', 'strong', 'img', 'code', 'pre'):
            props = match.group(2).strip().replace('\n', ' ')
            props = re.sub(r'\s+', ' ', props).strip()
            tag_rules[tag] = props

    # 3. 移除 <style> 标签
    html = re.sub(r'<style>.*?</style>\s*', '', html, flags=re.DOTALL)

    # 4. 将 class 属性替换为内联 style
    def replace_class(match):
        full_tag = match.group(0)
        tag_name = match.group(1)

        # 提取所有 class 名
        cls_match = re.search(r'class="([^"]+)"', full_tag)
        if not cls_match:
            # 没有 class，但可能需要加标签级样式
            if tag_name in tag_rules:
                existing_style = re.search(r'style="([^"]*)"', full_tag)
                if existing_style:
                    new_style = tag_rules[tag_name] + ' ' + existing_style.group(1)
                    full_tag = full_tag.replace(f'style="{existing_style.group(1)}"', f'style="{new_style}"')
                else:
                    full_tag = full_tag.replace(f'<{tag_name}', f'<{tag_name} style="{tag_rules[tag_name]}"', 1)
            return full_tag

        class_names = cls_match.group(1).split()

        # 收集所有匹配的 CSS 规则
        inline_props = []
        for cn in class_names:
            if cn in rules:
                inline_props.append(rules[cn])

        if not inline_props:
            return full_tag

        combined = ' '.join(inline_props)

        # 合并已有的 style
        existing_style = re.search(r'style="([^"]*)"', full_tag)
        if existing_style:
            combined = combined + ' ' + existing_style.group(1)
            full_tag = re.sub(r'style="[^"]*"', f'style="{combined}"', full_tag)
        else:
            full_tag = re.sub(r'class="[^"]*"', f'style="{combined}"', full_tag)

        # 移除 class 属性（如果 style 已替换）
        if 'class="' in full_tag and 'style="' in full_tag:
            full_tag = re.sub(r'\s*class="[^"]*"', '', full_tag)

        return full_tag

    # 处理所有开标签
    html = re.sub(r'<(\w+)([^>]*)>', replace_class, html)

    return html


def main():
    input_path = Path("/Volumes/ExternalSSD/code/claude-code-book/output/wechat-article-v2.html")
    output_path = Path("/Volumes/ExternalSSD/code/claude-code-book/output/wechat-article-v2-inline.html")

    html = input_path.read_text(encoding="utf-8")

    # 提取 body 内容
    body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)

    if body_match and style_match:
        # 重组为 style + body 内容
        work_html = f"<style>{style_match.group(1)}</style>\n{body_match.group(1)}"
    else:
        work_html = html

    result = inline_css(work_html)

    # 保存
    output_path.write_text(result, encoding="utf-8")

    # 统计
    class_count = len(re.findall(r'class="', result))
    style_count = len(re.findall(r'style="', result))
    style_tag = len(re.findall(r'<style', result))

    print(f"输入: {input_path.name}")
    print(f"输出: {output_path.name}")
    print(f"剩余 class: {class_count}")
    print(f"内联 style: {style_count}")
    print(f"<style> 标签: {style_tag}")
    print(f"大小: {len(result)} bytes")

    if class_count == 0 and style_tag == 0:
        print("✅ 全部内联完成，可安全粘贴到公众号")
    else:
        print(f"⚠️ 仍有 {class_count} 个 class 和 {style_tag} 个 <style> 标签")


if __name__ == "__main__":
    main()
