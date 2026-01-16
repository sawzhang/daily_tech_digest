#!/usr/bin/env python3
"""
Daily Tech Digest Agent
========================
使用 Claude Agent SDK 每天定时生成技术日报并发布到微信公众号

功能：
1. 聚合 HN/ProductHunt/Twitter 数据
2. AI 分析趋势并生成日报
3. 自动发布到微信公众号

使用方法：
    python tech_digest_agent.py              # 立即执行一次
    python tech_digest_agent.py --schedule   # 启动定时任务（每天8:00）
    python tech_digest_agent.py --test       # 测试模式（不发布）

环境变量（或 .env 文件）：
    ANTHROPIC_API_KEY=sk-ant-xxx
    WECHAT_APP_ID=wxxxxxxxxxxx
    WECHAT_APP_SECRET=xxxxxxxxxx
"""

import os
import json
import re
import logging
import argparse
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

import anthropic
import requests
import schedule
import time
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tech_digest.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# AI Twitter 搜索关键词配置
AI_TWITTER_KEYWORDS = {
    # AI 公司/实验室
    "companies": [
        "OpenAI", "Anthropic", "Claude", "DeepMind", "Google AI",
        "Meta AI", "Mistral", "Cohere", "Perplexity", "xAI"
    ],
    # AI 模型/产品
    "models": [
        "GPT-4o", "GPT-5", "Claude 4", "Gemini", "Llama 3",
        "Mistral Large", "DALL-E", "Sora", "Midjourney", "Stable Diffusion"
    ],
    # AI 开发工具
    "dev_tools": [
        "Claude Code", "Claude Cowork", "Cursor", "GitHub Copilot", "Windsurf",
        "v0", "Replit Agent", "Devin", "LangChain", "LlamaIndex"
    ],
    # AI 技术/概念
    "technologies": [
        "AI agent", "LLM", "RAG", "fine-tuning", "multimodal",
        "AGI", "AI safety", "RLHF", "MoE", "context window"
    ],
    # AI 领域KOL (用于提升搜索质量)
    "influencers": [
        "@sama", "@ylecun", "@kaborevsky", "@emaborevsky",
        "@AnthropicAI", "@OpenAI", "@GoogleDeepMind"
    ],
    # 突发新闻/产品发布 (捕捉最新动态)
    "breaking_news": [
        "Anthropic launches", "OpenAI announces", "Google AI releases",
        "new AI tool", "AI product launch", "just released", "now available"
    ]
}


class TechDigestAgent:
    """技术日报 Agent - 使用 Claude API 生成技术日报"""

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-5-20250929"  # 使用 Sonnet 4.5 平衡成本和质量
        self.today = datetime.now().strftime("%Y年%m月%d日")
        self.today_short = datetime.now().strftime("%Y-%m-%d")
        self.output_dir = Path("output")

    def load_recent_topics(self, days: int = 7) -> str:
        """加载最近几天报道过的话题，用于内容去重"""
        recent_topics = []

        for i in range(1, days + 1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            md_path = self.output_dir / f"tech_digest_{date}.md"

            if md_path.exists():
                try:
                    content = md_path.read_text(encoding="utf-8")
                    # 提取标题
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else ""
                    # 提取今日头条
                    headline_match = re.search(r'今日头条[：:]\s*(.+)', content)
                    headline = headline_match.group(1) if headline_match else ""
                    # 提取硅谷雷达部分的小标题
                    radar_titles = re.findall(r'###\s*[🔥⚠️💀]\s*(.+)', content)

                    if title or headline or radar_titles:
                        topics = [f"- 日期: {date}"]
                        if title:
                            topics.append(f"  标题: {title}")
                        if headline:
                            topics.append(f"  头条: {headline}")
                        if radar_titles:
                            topics.append(f"  雷达: {', '.join(radar_titles[:3])}")
                        recent_topics.append("\n".join(topics))
                except Exception as e:
                    logger.warning(f"读取历史文件 {md_path} 失败: {e}")

        return "\n\n".join(recent_topics) if recent_topics else ""
        
    def search_web(self, query: str) -> str:
        """使用 Claude 的 web_search 工具搜索网页"""
        logger.info(f"搜索: {query}")
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search"
            }],
            messages=[{
                "role": "user",
                "content": f"搜索以下内容并返回结果摘要：{query}"
            }]
        )
        
        # 提取文本响应
        result = ""
        for block in response.content:
            if hasattr(block, 'text'):
                result += block.text
        return result
    
    def fetch_hn_data(self) -> str:
        """获取 Hacker News 热门文章"""
        logger.info("获取 Hacker News 数据...")
        return self.search_web(f"Hacker News top stories today {self.today_short} site:news.ycombinator.com OR site:hntoplinks.com")
    
    def fetch_producthunt_data(self) -> str:
        """获取 Product Hunt 热门产品"""
        logger.info("获取 Product Hunt 数据...")
        return self.search_web(f"Product Hunt top products {self.today_short} site:producthunt.com")
    
    def fetch_ai_twitter_data(self) -> str:
        """获取 AI Twitter 动态 - 多维度搜索策略，只获取最近7天的内容"""
        logger.info("获取 AI Twitter 数据...")

        # 时间限制：只获取最近7天的内容
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        time_filter = f"after:{week_ago}"
        site_filter = "site:x.com OR site:twitter.com"

        # 多维度搜索查询
        search_dimensions = [
            # 维度1: 突发新闻/产品发布 (优先级最高，捕捉最新动态)
            {
                "name": "AI突发新闻",
                "keywords": AI_TWITTER_KEYWORDS["breaking_news"],
            },
            # 维度2: AI公司动态
            {
                "name": "AI公司动态",
                "keywords": AI_TWITTER_KEYWORDS["companies"][:5],
            },
            # 维度3: AI模型/产品发布
            {
                "name": "AI模型产品",
                "keywords": AI_TWITTER_KEYWORDS["models"][:5],
            },
            # 维度4: AI开发工具
            {
                "name": "AI开发工具",
                "keywords": AI_TWITTER_KEYWORDS["dev_tools"][:6],  # 包含 Claude Code 和 Cowork
            },
            # 维度5: AI技术趋势
            {
                "name": "AI技术趋势",
                "keywords": AI_TWITTER_KEYWORDS["technologies"][:5],
            },
        ]

        all_results = []
        for dimension in search_dimensions:
            keywords_str = " OR ".join(dimension["keywords"])
            query = f"({keywords_str}) latest news {time_filter} {site_filter}"
            logger.info(f"搜索 {dimension['name']}: {query[:80]}...")

            result = self.search_web(query)
            if result:
                all_results.append(f"### {dimension['name']}\n{result}")

        return "\n\n".join(all_results) if all_results else "未获取到AI Twitter数据"

    def fetch_reddit_ml_data(self) -> str:
        """获取 Reddit r/MachineLearning 热门帖子"""
        logger.info("获取 Reddit ML 数据...")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        return self.search_web(f"site:reddit.com/r/MachineLearning top posts after:{week_ago}")

    def fetch_github_trending(self) -> str:
        """获取 GitHub Trending 项目"""
        logger.info("获取 GitHub Trending 数据...")
        return self.search_web(f"GitHub trending repositories {self.today_short} AI machine learning site:github.com/trending OR site:github.blog")

    def generate_digest(self, hn_data: str, ph_data: str, twitter_data: str,
                        reddit_data: str = "", github_data: str = "") -> Dict[str, str]:
        """使用 Claude 生成技术日报"""
        logger.info("生成技术日报...")

        # 加载历史话题用于去重
        recent_topics = self.load_recent_topics(days=7)
        dedup_instruction = ""
        if recent_topics:
            dedup_instruction = f"""
## 重要：内容去重要求
以下是过去7天已经报道过的话题，请**避免重复报道相同内容**：
- 如果某个话题已经报道过，除非有重大进展，否则不要再作为头条或主要内容
- 如果必须提及已报道的话题，请用新的角度、新的观点来解读
- 优先选择今天数据源中的新话题

### 已报道话题列表：
{recent_topics}

"""

        prompt = f"""你是一位在硅谷工作多年的华人技术老兵，同时运营一个小众但有深度的技术公众号「Tech老兵日记」。你的风格是：
- 说话直接，偶尔毒舌，但观点犀利
- 喜欢用类比和比喻解释复杂概念
- 会加入自己的判断和预测，敢于表态（比如"这个我不看好"、"这个值得关注"）
- 偶尔吐槽行业乱象或过度炒作
- 语气像跟朋友聊天，不是写报告
- 会分享一些"圈内人才知道"的洞察

请根据以下数据源，用你的风格写一份技术日报。

## 重要：内容新鲜度要求
- **今天日期是 {self.today}**
- **只使用最近 7 天内的新闻和信息**
- **严格过滤掉超过一周的旧新闻**（如去年的产品发布、旧模型发布等）
- 如果数据源中包含旧信息（如 DeepSeek R1 发布于2025年1月、GPT-4 发布于2023年等），直接忽略这些内容
- 宁可内容少一些，也不要使用过时的信息误导读者
{dedup_instruction}
## 数据源

### Hacker News
{hn_data}

### Product Hunt
{ph_data}

### AI Twitter
{twitter_data}

### Reddit r/MachineLearning
{reddit_data if reddit_data else "暂无数据"}

### GitHub Trending
{github_data if github_data else "暂无数据"}

## 输出要求

### 重要：文章长度和SEO优化
- **文章总长度必须在 1500-2500 字之间**，内容要充实有料
- **标题要包含热门关键词**（如：AI、Claude、GPT、效率工具、程序员 等），吸引搜索流量
- **正文自然融入长尾关键词**（如：AI工具推荐、程序员效率、科技趋势、硅谷见闻 等），每300字出现2-3次
- **设置互动钩子**：在文中和文末引导读者点赞、评论
- **引导关注**：在合适位置自然地提及关注公众号的好处

### Part 1: Markdown 版本
按照以下结构生成，注意保持个人风格和充实内容：

1. **开篇引言**（2-3句引人入胜的话，制造悬念或抛出观点，让读者想继续看下去）

2. **今日头条：XXX**（针对今天最重要的1个事件，深度分析 300-400字）
   - 这是什么：用大白话解释
   - 为什么重要：对行业/开发者的影响
   - 我的看法：个人判断和预测
   - 你应该关注的点：具体建议

3. **硅谷雷达：本周值得关注**（2-3个重要趋势，每个150-200字）
   - 用 🔥 标记强烈看好，⚠️ 标记需要观望，💀 标记不看好
   - 每个都要有"这意味着什么"的分析

4. **HN 热榜精选**（8-10个项目，表格+点评）
   | 排名 | 标题 | 热度 | 为什么值得看 |
   - 挑2-3个特别有意思的，在表格后额外写几句深度点评

5. **Product Hunt 今日发现**（4-5个产品）
   | 产品 | 一句话介绍 | 亮点 | 踩坑提醒 |
   - 对特别有意思的产品，补充"这个产品解决了什么痛点"的分析

6. **GitHub Trending 本周热门**（3-5个开源项目）
   | 项目 | 语言 | Star数 | 一句话点评 |
   - 优先选择 AI/ML 相关的项目
   - 简要说明项目解决什么问题、适合谁用

7. **AI 圈内幕**（这部分要写详细，400-500字）
   - 大厂动态：谁发布了什么，意味着什么
   - 开源社区：有什么新项目值得关注（结合 GitHub Trending 和 Reddit 讨论）
   - 工具推荐：我最近在用什么，体验如何
   - 行业八卦：有什么有意思的事情（如果有的话）

8. **本周实操建议**（2-3个具体可落地的行动项）
   - 不要假大空，要具体到"打开xxx，试试xxx功能"
   - 可以是工具推荐、学习资源、或者思维方式

9. **老兵碎碎念**（150-200字的个人感悟或思考）
   - 可以是对行业的思考、职业建议、或者生活感悟
   - 语气要真诚，像跟老朋友聊天

10. **互动时间**
    - 抛出1-2个问题，引导读者在评论区讨论
    - 例如："你觉得xxx怎么样？欢迎在评论区聊聊"
    - 加一句"觉得有用的话，点个赞支持一下👇"

11. **下期预告**（1-2句话，制造期待感）
    - 预告下一期可能会聊的话题
    - 引导关注："关注公众号，第一时间获取更新"

### Part 2: HTML 版本
生成适配微信公众号的富文本 HTML，严格遵循以下样式规范：

**布局规范（重要！）：**
- 卡片容器：padding: 15px; margin-bottom: 15px; （不要用过大的内边距）
- 标题和内容之间：margin-bottom: 10px; （标题下方紧跟内容，不要留大空白）
- 表格：margin-top: 10px; width: 100%; （表格紧跟标题，不要有大间距）
- 禁止使用 min-height 或固定 height
- 禁止在标题和表格之间添加空的 div 或 br 标签

**样式规范：**
- 使用内联样式
- 卡片背景：浅色渐变 linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) 或类似柔和色
- 卡片圆角：border-radius: 12px;
- **表格表头（重要！）**：必须有明显的深色背景 #667eea，白色粗体文字，确保表头清晰可见
- 表格数据行：交替背景色 #ffffff 和 #f8f9fa
- 表格单元格：padding: 8px 10px; （紧凑型）
- 字体大小：标题 16-18px，正文 14-15px，表格 13px
- 行间距：line-height: 1.8;（提升阅读体验）

**特殊区块样式：**
- **阅读时间提示（必须放在文章最开头！）**：统计全文字数，计算预计阅读时间（按300字/分钟），居中显示
- 今日头条区块：使用醒目的渐变背景 linear-gradient(135deg, #667eea 0%, #764ba2 100%)，白色文字
- 互动引导区块：使用橙色/红色系背景，加粗文字，居中对齐
- 个人观点/碎碎念：使用引用样式，左边框 4px solid #667eea，浅灰背景
- 关键词/标签：使用小圆角背景色块突出显示

**阅读时间提示样式（放在HTML最开头）：**
```html
<div style="text-align: center; color: #888; font-size: 13px; padding: 10px 0; margin-bottom: 15px; border-bottom: 1px dashed #e0e0e0;">
  本文共约XXXX字 | 预计阅读时间X分钟
</div>
```

**互动引导样式示例：**
```html
<div style="background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0;">
  <p style="color: white; font-size: 16px; font-weight: bold; margin: 0;">👇 觉得有用？点个赞支持一下</p>
</div>
```

**引用/个人观点样式：**
```html
<div style="border-left: 4px solid #667eea; background: #f8f9fa; padding: 15px; margin: 15px 0;">
  <p style="margin: 0; color: #555; font-style: italic;">个人观点内容...</p>
</div>
```

**表格样式示例（表头必须清晰可见）：**
```html
<table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
  <thead>
    <tr style="background: #667eea;">
      <th style="padding: 10px; color: white; font-weight: bold; text-align: left;">排名</th>
      <th style="padding: 10px; color: white; font-weight: bold; text-align: left;">标题</th>
      <th style="padding: 10px; color: white; font-weight: bold; text-align: left;">热度</th>
      <th style="padding: 10px; color: white; font-weight: bold; text-align: left;">为什么值得看</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background: #ffffff;"><td style="padding: 8px;">...</td>...</tr>
    <tr style="background: #f8f9fa;"><td style="padding: 8px;">...</td>...</tr>
  </tbody>
</table>
```

**【重要】请严格按以下格式返回，两部分缺一不可：**

[MARKDOWN]
（完整的 Markdown 内容）
[/MARKDOWN]

[WECHAT_HTML]
（完整的 HTML 内容，以 <div> 开始，不要包含 <!DOCTYPE>、<html>、<head>、<body> 等标签）
[/WECHAT_HTML]

**注意：**
1. 必须同时生成 MARKDOWN 和 WECHAT_HTML 两部分
2. WECHAT_HTML 是发布到微信公众号的必需格式，绝对不能省略
3. 确保 [WECHAT_HTML] 和 [/WECHAT_HTML] 标签完整闭合
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=16384,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # 提取响应文本
        full_response = ""
        for block in response.content:
            if hasattr(block, 'text'):
                full_response += block.text
        
        # 解析 Markdown 和 HTML（使用方括号标签避免与 HTML 内容冲突）
        md_match = re.search(r'\[MARKDOWN\](.*?)\[/MARKDOWN\]', full_response, re.DOTALL)
        html_match = re.search(r'\[WECHAT_HTML\](.*?)\[/WECHAT_HTML\]', full_response, re.DOTALL)

        # 记录解析结果
        if not md_match:
            logger.warning("未能解析到 [MARKDOWN] 标签，将使用原始响应")
        if not html_match:
            logger.warning("未能解析到 [WECHAT_HTML] 标签，HTML 内容为空")
            logger.debug(f"原始响应末尾 500 字符: {full_response[-500:]}")

        return {
            "markdown": md_match.group(1).strip() if md_match else full_response,
            "html": html_match.group(1).strip() if html_match else "",
            "raw": full_response
        }
    
    def run(self, max_retries: int = 3) -> Dict[str, str]:
        """执行完整的日报生成流程"""
        logger.info(f"=== 开始生成 {self.today} 技术日报 ===")

        # 获取数据源
        hn_data = self.fetch_hn_data()
        ph_data = self.fetch_producthunt_data()
        twitter_data = self.fetch_ai_twitter_data()
        reddit_data = self.fetch_reddit_ml_data()
        github_data = self.fetch_github_trending()

        # 生成日报，带重试逻辑确保 HTML 输出
        digest = {}
        for attempt in range(1, max_retries + 1):
            digest = self.generate_digest(hn_data, ph_data, twitter_data, reddit_data, github_data)
            if digest.get("html"):
                logger.info(f"日报生成成功 (第 {attempt} 次尝试)")
                break
            if attempt < max_retries:
                logger.warning(f"第 {attempt} 次生成未包含 HTML，重试中...")
            else:
                logger.warning(f"第 {attempt} 次生成未包含 HTML，已达最大重试次数")

        if not digest.get("html"):
            logger.error("所有尝试均未生成 HTML 内容，无法发布到公众号")
        
        # 保存文件
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        md_path = output_dir / f"tech_digest_{self.today_short}.md"
        html_path = output_dir / f"tech_digest_{self.today_short}.html"
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(digest["markdown"])
        logger.info(f"Markdown 已保存: {md_path}")
        
        if digest["html"]:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(digest["html"])
            logger.info(f"HTML 已保存: {html_path}")
        
        digest["md_path"] = str(md_path)
        digest["html_path"] = str(html_path) if digest["html"] else None
        
        return digest


class WeChatPublisher:
    """微信公众号发布器"""
    
    def __init__(self):
        self.app_id = os.getenv("WECHAT_APP_ID")
        self.app_secret = os.getenv("WECHAT_APP_SECRET")
        self.access_token = None
        
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
    
    def create_cover_image(self, title: str = "Tech Digest", keywords: List[str] = None) -> str:
        """生成封面图片，支持显示每日关键词"""
        img = Image.new('RGB', (900, 383), color='#667eea')
        draw = ImageDraw.Draw(img)

        # 渐变背景
        for i in range(383):
            r = int(102 + (118-102) * i / 383)
            g = int(126 + (75-126) * i / 383)
            b = int(234 + (162-234) * i / 383)
            draw.line([(0, i), (900, i)], fill=(r, g, b))

        # 字体
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 48)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 24)
            font_tag = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 18)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_tag = ImageFont.load_default()

        today = datetime.now().strftime("%Y年%m月%d日")
        draw.text((450, 120), title, font=font_large, fill='white', anchor='mm')
        draw.text((450, 175), today, font=font_small, fill='white', anchor='mm')

        # 绘制关键词标签
        if keywords:
            tags = keywords[:4]  # 最多显示4个关键词
            tag_y = 230
            total_width = sum(len(tag) * 18 + 30 for tag in tags) + (len(tags) - 1) * 10
            start_x = (900 - total_width) // 2

            for tag in tags:
                tag_width = len(tag) * 18 + 20
                # 绘制圆角矩形背景
                draw.rounded_rectangle(
                    [start_x, tag_y, start_x + tag_width, tag_y + 30],
                    radius=15,
                    fill=(255, 255, 255, 50)
                )
                # 绘制文字
                draw.text((start_x + tag_width // 2, tag_y + 15), f"#{tag}",
                         font=font_tag, fill='white', anchor='mm')
                start_x += tag_width + 10

        cover_path = "output/cover.jpg"
        img.save(cover_path, "JPEG", quality=95)
        logger.info(f"封面图片已生成: {cover_path}")
        return cover_path
    
    def upload_image(self, image_path: str) -> str:
        """上传图片到微信"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
        
        with open(image_path, "rb") as f:
            files = {"media": ("cover.jpg", f, "image/jpeg")}
            resp = requests.post(url, files=files, timeout=30)
            result = resp.json()
        
        if "media_id" in result:
            logger.info(f"图片上传成功: {result['media_id']}")
            return result["media_id"]
        else:
            raise Exception(f"图片上传失败: {result}")
    
    def create_draft(self, title: str, content: str, thumb_media_id: str) -> str:
        """创建草稿"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        
        article = {
            "articles": [{
                "title": title,
                "author": "Tech Digest",
                "digest": "每日技术趋势精选",
                "content": content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }]
        }
        
        # 关键：确保中文正确编码
        json_data = json.dumps(article, ensure_ascii=False).encode('utf-8')
        resp = requests.post(
            url,
            data=json_data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=30
        )
        result = resp.json()
        
        if "media_id" in result:
            logger.info(f"草稿创建成功: {result['media_id']}")
            return result["media_id"]
        else:
            raise Exception(f"草稿创建失败: {result}")
    
    def publish(self, draft_media_id: str) -> Optional[str]:
        """发布文章（需要认证公众号）"""
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
            raise Exception(f"发布失败: {result}")
    
    def run(self, html_content: str, title: str = "Tech Digest", keywords: List[str] = None) -> Dict[str, Any]:
        """执行完整发布流程"""
        logger.info("=== 开始发布到微信公众号 ===")

        # 生成封面（带关键词）
        cover_path = self.create_cover_image(title, keywords)
        
        # 上传封面
        thumb_media_id = self.upload_image(cover_path)
        
        # 创建草稿
        draft_media_id = self.create_draft(title, html_content, thumb_media_id)
        
        # 尝试发布
        publish_id = self.publish(draft_media_id)
        
        return {
            "thumb_media_id": thumb_media_id,
            "draft_media_id": draft_media_id,
            "publish_id": publish_id,
            "status": "published" if publish_id else "draft_created"
        }


def extract_keywords_from_markdown(markdown: str) -> List[str]:
    """从 Markdown 内容中提取关键词（用于封面图）"""
    keywords = []

    # 1. 从标题中提取（格式如：# Tech老兵日记 | 2026.01.16：Claude泄密、GitHub Actions被骂）
    title_match = re.search(r'^#\s+[^|]+\|[^：:]+[：:]\s*(.+)$', markdown, re.MULTILINE)
    if title_match:
        title_part = title_match.group(1)
        # 提取中文/英文关键词短语，用顿号或逗号分隔
        phrases = re.split(r'[、，,]', title_part)
        for phrase in phrases[:3]:
            phrase = phrase.strip()
            if phrase and len(phrase) <= 15:
                keywords.append(phrase)

    # 2. 如果标题没有提取到，尝试从今日头条部分提取
    if not keywords:
        headline_match = re.search(r'今日头条[：:]\s*(.+)', markdown)
        if headline_match:
            keywords.append(headline_match.group(1).strip()[:15])

    # 3. 补充常见 AI 关键词
    ai_keywords = ["Claude", "GPT", "OpenAI", "Anthropic", "AI Agent", "LLM"]
    for kw in ai_keywords:
        if kw.lower() in markdown.lower() and kw not in keywords:
            keywords.append(kw)
            if len(keywords) >= 4:
                break

    return keywords[:4]


def daily_task():
    """每日定时任务"""
    logger.info("=" * 50)
    logger.info("定时任务触发")
    logger.info("=" * 50)
    
    try:
        # 1. 生成日报
        agent = TechDigestAgent()
        digest = agent.run()
        
        # 2. 发布到微信（只使用 HTML 格式）
        if os.getenv("WECHAT_APP_ID") and os.getenv("WECHAT_APP_SECRET"):
            html_content = digest.get("html", "")

            if not html_content:
                logger.error("HTML 内容为空，拒绝发布到公众号")
                logger.error("请检查 Claude API 返回的内容是否包含 [WECHAT_HTML] 标签")
            else:
                publisher = WeChatPublisher()
                logger.info("使用 HTML 格式发布到公众号")
                today_short = datetime.now().strftime("%m.%d")
                # 从 markdown 提取关键词用于封面图
                keywords = extract_keywords_from_markdown(digest.get("markdown", ""))
                logger.info(f"提取到关键词: {keywords}")
                result = publisher.run(html_content, f"Tech Digest {today_short}", keywords)
                logger.info(f"发布结果: {result}")
        else:
            logger.warning("未配置微信公众号凭证，跳过发布")
        
        logger.info("每日任务完成！")
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Daily Tech Digest Agent")
    parser.add_argument("--schedule", action="store_true", help="启动定时任务模式")
    parser.add_argument("--test", action="store_true", help="测试模式（只生成不发布）")
    parser.add_argument("--time", default="08:00", help="定时执行时间（默认 08:00）")
    args = parser.parse_args()
    
    if args.schedule:
        # 定时任务模式
        logger.info(f"定时任务已启动，每天 {args.time} 执行")
        schedule.every().day.at(args.time).do(daily_task)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    elif args.test:
        # 测试模式
        logger.info("测试模式：只生成日报，不发布")
        agent = TechDigestAgent()
        digest = agent.run()
        print("\n=== 生成结果 ===")
        print(f"Markdown: {digest.get('md_path')}")
        print(f"HTML: {digest.get('html_path')}")
    
    else:
        # 立即执行一次
        daily_task()


if __name__ == "__main__":
    main()
