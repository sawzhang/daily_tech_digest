# CLAUDE.md

本文件为 Claude Code 提供项目指导。

## 项目概述

**Daily Tech Digest Agent** - 自动化技术日报生成器和微信公众号发布工具。

功能：
- 聚合 Hacker News、Product Hunt、AI Twitter 数据
- 使用 Claude API 分析趋势并生成有个人风格的技术日报
- 支持 Markdown 和微信公众号 HTML 格式输出
- 可选自动发布到微信公众号

## 本地开发

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 ANTHROPIC_API_KEY

# 测试运行（只生成，不发布）
python tech_digest_agent.py --test

# 完整运行（生成 + 发布）
python tech_digest_agent.py

# 定时模式（每天 08:00 执行）
python tech_digest_agent.py --schedule

# 自定义时间
python tech_digest_agent.py --schedule --time 09:30
```

## 云端部署

**服务器**: `root@104.156.250.197`
**路径**: `/opt/tech-digest`
**定时**: 每天 08:00 (北京时间)

### 使用 deploy.sh 脚本

```bash
./deploy.sh deploy   # 【推荐】快速部署：上传代码到服务器并构建
./deploy.sh logs     # 查看容器日志
./deploy.sh status   # 查看容器状态
./deploy.sh run      # 在服务器上立即执行一次
./deploy.sh restart  # 重启容器
./deploy.sh stop     # 停止容器
./deploy.sh build    # 本地构建镜像
./deploy.sh push     # 推送本地镜像到服务器（较慢）
```

### 快速部署（修复问题后）

```bash
# 一条命令完成部署
./deploy.sh deploy

# 查看日志确认
./deploy.sh logs
```

## 项目结构

```
daily_tech_digest/
├── tech_digest_agent.py   # 主程序
├── requirements.txt       # Python 依赖
├── Dockerfile            # Docker 构建文件
├── deploy.sh             # 部署脚本
├── .env                  # 环境变量（不提交）
├── .env.example          # 环境变量示例
├── output/               # 生成的日报文件
└── .claude/skills/       # Claude Code Skills
    ├── deploy.md         # /deploy 部署技能
    ├── run.md            # /run 运行技能
    ├── keywords.md       # /keywords 关键词管理
    ├── wechat-publish.md # /wechat-publish 微信发文
    ├── napkin-images.md  # /napkin-images Napkin.ai 插图生成
    └── wechat_publish.py # 微信发布脚本
```

## 核心配置

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `ANTHROPIC_API_KEY` | 是 | Anthropic API 密钥 |
| `WECHAT_APP_ID` | 否 | 微信公众号 AppID |
| `WECHAT_APP_SECRET` | 否 | 微信公众号 AppSecret |
| `SCHEDULE_TIME` | 否 | 定时执行时间，默认 08:00 |

### AI 关键词配置

编辑 `tech_digest_agent.py` 中的 `AI_TWITTER_KEYWORDS` (约第54-86行)：

```python
AI_TWITTER_KEYWORDS = {
    "companies": ["OpenAI", "Anthropic", "Claude", ...],      # AI 公司
    "models": ["GPT-5", "Claude 4", "Gemini", ...],           # AI 模型
    "dev_tools": ["Claude Code", "Claude Cowork", ...],       # 开发工具
    "technologies": ["AI agent", "LLM", "RAG", ...],          # 技术概念
    "influencers": ["@sama", "@ylecun", ...],                 # KOL
    "breaking_news": ["Anthropic launches", ...],             # 突发新闻
}
```

**添加新关键词后需要重新部署才能生效。**

## 关键实现

- **模型**: `claude-sonnet-4-5-20250929`
- **搜索工具**: `web_search_20250305`
- **输出解析**: 正则匹配 `[MARKDOWN]` 和 `[WECHAT_HTML]` 标签
- **搜索策略**: 5 维度搜索（突发新闻、公司动态、模型产品、开发工具、技术趋势）
- **内容风格**: 硅谷技术老兵人设，有态度有深度，1500-2500字
- **SEO 优化**: 融入热门关键词，引导互动和关注

## 常见问题

### API 调用失败
检查 `.env` 中的 `ANTHROPIC_API_KEY` 是否正确。

### 微信发布失败
1. 检查 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`
2. 确认公众号已完成认证
3. 查看日志了解具体错误

### Docker 构建失败
服务器上构建：
```bash
ssh root@104.156.250.197 "cd /opt/tech-digest && docker build -t tech-digest ."
```

### 内容风格调整
编辑 `tech_digest_agent.py` 中 `generate_digest` 方法的 prompt（约第186-260行）。

## 微信公众号图文发布

### 使用 /wechat-publish 技能

```bash
# 发布指定目录的文章
/wechat-publish /path/to/article-folder
```

### 文章目录结构要求

```
article-folder/
├── *.html           # 文章内容（必需）
├── cover.png/jpg    # 封面图片（必需）
└── *.png/jpg        # 正文图片（可选，自动上传并替换路径）
```

### 文章制作完整流程

1. **撰写 HTML 文章**：按微信排版规范编写，图片用本地文件名引用
2. **准备封面图片**：cover.png/jpg，建议 900x383 比例
3. **生成正文插图**：使用 `/napkin-images` 通过 Napkin.ai 生成专业可视化图表
4. **所有文件放入同一目录**
5. **执行 `/wechat-publish <目录路径>` 发布**

### 使用 Napkin.ai 生成插图

通过浏览器自动化操作 Napkin.ai（https://app.napkin.ai），输入结构化文本自动生成可视化图表：

```bash
# 使用 /napkin-images 技能
/napkin-images "Layer 1: BDD Scenarios\nLayer 2: SDD Skills\nLayer 3: AI Agent Team"
```

**操作流程**：New Napkin → 输入标题和结构化内容 → Cmd+A 全选 → Generate Visual → 导出 PNG (2x) → 复制到文章目录

**内容类型**：流程图、时间线、数据仪表盘、架构层次图等（根据文本结构自动识别）

**前置条件**：已安装 Claude in Chrome 扩展，已登录 Napkin.ai 账号

### 发布执行流程

1. 读取 HTML 文件，提取 `<title>` 和 `<body>` 内容
2. 上传正文图片到微信素材库，获取 URL 并替换本地路径
3. 上传封面图片，获取 media_id
4. 优化 HTML（颜色转十六进制、清理空白、添加图片样式）
5. 创建草稿 → 尝试发布（无权限则提示手动发布）

### 微信排版规范

- **颜色**: 必须使用十六进制格式（#ffffff），不能用 white/black
- **列表**: 标签之间不能有空白字符
- **图片**: 宽度 100%，圆角 8px，居中显示
- **字体**: 正文 15px，行高 2.0，字间距 1px

### 直接运行脚本

```bash
source venv/bin/activate
python .claude/skills/wechat_publish.py "/path/to/article-folder"
```
