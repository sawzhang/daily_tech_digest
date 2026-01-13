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
- Uses regex to parse `<markdown>` and `<html>` tags from Claude's response
- Logging to both console and `tech_digest.log`
- Schedule library handles recurring tasks in `--schedule` mode
