# 🗓️ Daily Tech Digest Agent

基于 Claude Agent SDK 的每日技术日报自动生成与发布系统。

## ✨ 功能特性

- **多源数据聚合**：自动抓取 Hacker News、Product Hunt、AI Twitter 动态
- **AI 智能分析**：使用 Claude 进行趋势识别和深度解读
- **自动排版**：生成适配微信公众号的富文本格式
- **定时发布**：支持每天定时自动执行
- **断点续传**：失败自动重试，支持只生成不发布

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写 API Key
```

### 3. 运行

```bash
# 立即执行一次（生成 + 发布）
python tech_digest_agent.py

# 测试模式（只生成，不发布）
python tech_digest_agent.py --test

# 定时任务模式（每天 8:00 执行）
python tech_digest_agent.py --schedule

# 自定义执行时间
python tech_digest_agent.py --schedule --time 09:30
```

## 📁 项目结构

```
daily_tech_digest/
├── tech_digest_agent.py   # 主程序
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量模板
├── .env                  # 环境变量（需自行创建）
├── output/               # 输出目录
│   ├── tech_digest_2026-01-10.md
│   ├── tech_digest_2026-01-10.html
│   └── cover.jpg
└── tech_digest.log       # 运行日志
```

## 🔧 配置说明

### 必需配置

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | [console.anthropic.com](https://console.anthropic.com/) |

### 可选配置（微信发布）

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `WECHAT_APP_ID` | 公众号 AppID | 微信公众平台 → 设置与开发 → 基本配置 |
| `WECHAT_APP_SECRET` | 公众号 AppSecret | 同上 |

> ⚠️ **注意**：使用微信发布功能需要将服务器 IP 添加到公众号 IP 白名单

## 🐳 Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 定时任务模式
CMD ["python", "tech_digest_agent.py", "--schedule"]
```

```bash
docker build -t tech-digest .
docker run -d --env-file .env tech-digest
```

## ☁️ 云服务部署

### 方案 A：Linux 服务器 + Cron

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天 8:00 执行）
0 8 * * * cd /path/to/daily_tech_digest && /usr/bin/python3 tech_digest_agent.py >> /var/log/tech_digest.log 2>&1
```

### 方案 B：GitHub Actions

创建 `.github/workflows/daily_digest.yml`：

```yaml
name: Daily Tech Digest

on:
  schedule:
    - cron: '0 0 * * *'  # UTC 00:00 = 北京时间 08:00
  workflow_dispatch:  # 支持手动触发

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          WECHAT_APP_ID: ${{ secrets.WECHAT_APP_ID }}
          WECHAT_APP_SECRET: ${{ secrets.WECHAT_APP_SECRET }}
        run: python tech_digest_agent.py
```

### 方案 C：AWS Lambda / 阿里云函数计算

使用 Serverless 框架部署，通过云服务的定时触发器执行。

## 📊 输出示例

### Markdown 格式

```markdown
# 🗓️ Tech Digest | 2026年1月10日

## ⚡ 60秒速览
> Anthropic 封杀第三方 Claude Code 接入...

## 🔥 趋势雷达
| 趋势 | 信号强度 | 业务相关度 |
|------|---------|-----------|
| AI Coding Agent | 🔴强 | ⭐⭐⭐ |
...
```

### 微信公众号效果

- 渐变色卡片标题
- 美化表格
- 移动端适配
- 自动生成封面图

## 🔍 技术架构

```
┌─────────────────────────────────────────────────┐
│                 定时调度器                        │
│              (schedule / cron)                  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│            TechDigestAgent                       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│  │ HN 数据   │ │ PH 数据   │ │ Twitter   │     │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘     │
│        └─────────────┼─────────────┘            │
│                      ▼                          │
│              Claude API                         │
│           (web_search + 分析)                   │
│                      │                          │
│        ┌─────────────┴─────────────┐           │
│        ▼                           ▼           │
│   Markdown 文件              HTML 文件         │
└────────┬───────────────────────────┬───────────┘
         │                           │
         ▼                           ▼
┌─────────────────────────────────────────────────┐
│            WeChatPublisher                       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│  │ 生成封面  │→│ 上传图片  │→│ 创建草稿  │→发布│
│  └───────────┘ └───────────┘ └───────────┘     │
└─────────────────────────────────────────────────┘
```

## ❓ 常见问题

### Q: 微信发布失败怎么办？

1. 检查 IP 白名单是否配置
2. 检查 AppID 和 AppSecret 是否正确
3. 未认证公众号无法使用自动发布 API，需手动到草稿箱发布

### Q: Claude API 调用失败？

1. 检查 API Key 是否有效
2. 检查账户余额
3. 确认模型名称正确（claude-sonnet-4-20250514）

### Q: 如何自定义日报模板？

修改 `TechDigestAgent.generate_digest()` 方法中的 prompt 即可。

## 📝 更新日志

- **v1.0.0** (2026-01-10): 初始版本，支持 HN/PH/Twitter 数据聚合和微信发布

## 📄 许可证

MIT License
