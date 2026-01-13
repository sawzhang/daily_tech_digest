# /keywords - 管理 AI Twitter 搜索关键词

## 描述
管理和更新 AI Twitter 数据获取的关键词配置，确保能捕捉到最新的 AI 动态。

## 关键词配置位置

文件：`tech_digest_agent.py`
变量：`AI_TWITTER_KEYWORDS`（约第54-86行）

## 当前配置

```python
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
    # AI 领域KOL
    "influencers": [
        "@sama", "@ylecun", "@kaborevsky", "@emaborevsky",
        "@AnthropicAI", "@OpenAI", "@GoogleDeepMind"
    ],
    # 突发新闻/产品发布
    "breaking_news": [
        "Anthropic launches", "OpenAI announces", "Google AI releases",
        "new AI tool", "AI product launch", "just released", "now available"
    ]
}
```

## 搜索维度

1. **AI突发新闻** - 捕捉最新产品发布
2. **AI公司动态** - 主流公司动态
3. **AI模型产品** - 模型相关新闻
4. **AI开发工具** - 开发工具动态
5. **AI技术趋势** - 技术概念讨论

## 添加新关键词

当有新的 AI 产品/公司出现时，在对应类别中添加：

```python
# 例如添加新工具
"dev_tools": [
    "Claude Code", "Claude Cowork", "新工具名称", ...
]
```

## 添加新搜索维度

在 `fetch_ai_twitter_data` 方法的 `search_dimensions` 列表中添加：

```python
{
    "name": "新维度名称",
    "keywords": AI_TWITTER_KEYWORDS["new_category"],
}
```

## 注意事项

1. 每个维度取前5-6个关键词，避免搜索过长
2. 关键词用 OR 连接
3. 修改后需要重新部署才能生效
