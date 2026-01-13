# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily Tech Digest Agent - an automated tech news digest generator and WeChat publisher built with the Anthropic SDK. It aggregates data from Hacker News, Product Hunt, and AI Twitter, uses Claude to analyze trends and generate formatted reports, then optionally publishes to WeChat Official Accounts.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run once (generate + publish)
python tech_digest_agent.py

# Test mode (generate only, no publishing)
python tech_digest_agent.py --test

# Scheduled mode (runs daily at 8:00)
python tech_digest_agent.py --schedule

# Custom schedule time
python tech_digest_agent.py --schedule --time 09:30
```

## Architecture

**TechDigestAgent** (main class):
- Uses Claude's `web_search_20250305` tool to fetch data from HN/PH/Twitter
- Generates both Markdown and WeChat-compatible HTML via Claude API
- Outputs to `output/` directory with date-stamped filenames

**WeChatPublisher** (optional):
- Creates gradient cover images using Pillow
- Uploads media and creates drafts via WeChat API
- Handles publishing (requires authenticated WeChat account)

**Entry points**:
- `daily_task()` - orchestrates full generate+publish flow
- `main()` - CLI argument parsing, supports `--schedule`, `--test`, `--time`

## Configuration

Required: `ANTHROPIC_API_KEY` in `.env` file

Optional (for WeChat publishing): `WECHAT_APP_ID`, `WECHAT_APP_SECRET`

## Docker Deployment

```bash
# Build image
docker build -t tech-digest .

# Run scheduled mode
docker run -d --env-file .env tech-digest

# Run once (test mode)
docker run --env-file .env tech-digest python tech_digest_agent.py --test
```

## Key Implementation Details

- Model: `claude-sonnet-4-5-20250929`
- Uses regex to parse `[MARKDOWN]` and `[WECHAT_HTML]` tags from Claude's response
- Logging to both console and `tech_digest.log`
- Schedule library handles recurring tasks in `--schedule` mode
- Multi-dimensional AI Twitter search with 5 categories (breaking news, companies, models, tools, technologies)

## Cloud Deployment

**Server**: `root@104.156.250.197`
**Path**: `/opt/tech-digest`
**Schedule**: Daily at 08:00 (Beijing time)

```bash
# Quick deploy (after code changes)
scp Dockerfile requirements.txt tech_digest_agent.py .env root@104.156.250.197:/opt/tech-digest/
ssh root@104.156.250.197 "cd /opt/tech-digest && docker build -t tech-digest . && docker restart tech-digest"

# View logs
ssh root@104.156.250.197 "docker logs -f --tail 100 tech-digest"

# Run once (test)
ssh root@104.156.250.197 "docker exec tech-digest python tech_digest_agent.py --test"
```

Or use `./deploy.sh` script: `build`, `push`, `logs`, `status`, `restart`, `stop`, `run`

## Skills (Claude Code)

Project skills are in `.claude/skills/`:
- `/deploy` - 云端部署命令
- `/run` - 本地运行命令
- `/keywords` - AI 关键词管理

## AI Keywords Configuration

Edit `AI_TWITTER_KEYWORDS` in `tech_digest_agent.py` (line ~54-86) to add/remove:
- Companies: OpenAI, Anthropic, DeepMind, etc.
- Models: GPT-5, Claude 4, Gemini, Llama 3, etc.
- Dev Tools: Claude Code, Cursor, Copilot, etc.
- Technologies: AI agent, LLM, RAG, etc.
- Breaking News: "Anthropic launches", "OpenAI announces", etc.
