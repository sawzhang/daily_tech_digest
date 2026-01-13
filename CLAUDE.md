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
./deploy.sh build    # 本地构建镜像
./deploy.sh push     # 推送到服务器并部署
./deploy.sh logs     # 查看容器日志
./deploy.sh status   # 查看容器状态
./deploy.sh restart  # 重启容器
./deploy.sh stop     # 停止容器
./deploy.sh run      # 在服务器上立即执行一次
```

### 快速部署命令

```bash
# 上传代码并重新部署
scp Dockerfile requirements.txt tech_digest_agent.py .env root@104.156.250.197:/opt/tech-digest/
ssh root@104.156.250.197 "cd /opt/tech-digest && docker build -t tech-digest . && docker stop tech-digest && docker rm tech-digest && docker run -d --name tech-digest --restart unless-stopped --env-file .env -v /opt/tech-digest/output:/app/output tech-digest"

# 查看日志
ssh root@104.156.250.197 "docker logs -f --tail 100 tech-digest"

# 立即执行一次
ssh root@104.156.250.197 "docker exec tech-digest python tech_digest_agent.py --test"

# 查看生成的文件
ssh root@104.156.250.197 "ls -la /opt/tech-digest/output/"
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
    └── keywords.md       # /keywords 关键词管理
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
