# /run - 本地运行 Daily Tech Digest

## 描述
在本地运行 Daily Tech Digest 生成技术日报。

## 前置条件
1. Python 3.11+ 已安装
2. 虚拟环境已创建: `python3 -m venv venv`
3. 依赖已安装: `source venv/bin/activate && pip install -r requirements.txt`
4. `.env` 文件已配置 ANTHROPIC_API_KEY

## 快速命令

### 1. 测试模式（只生成，不发布）
```bash
source venv/bin/activate && python tech_digest_agent.py --test
```

### 2. 完整运行（生成 + 发布到微信）
```bash
source venv/bin/activate && python tech_digest_agent.py
```

### 3. 定时模式（每天自动执行）
```bash
source venv/bin/activate && python tech_digest_agent.py --schedule
```

### 4. 自定义执行时间
```bash
source venv/bin/activate && python tech_digest_agent.py --schedule --time 09:30
```

## 输出文件

生成的文件保存在 `output/` 目录：
- `tech_digest_YYYY-MM-DD.md` - Markdown 格式
- `tech_digest_YYYY-MM-DD.html` - 微信公众号 HTML 格式

## Docker 本地运行

### 构建镜像
```bash
docker build -t tech-digest .
```

### 测试运行
```bash
docker run --rm --env-file .env tech-digest python tech_digest_agent.py --test
```

### 定时运行
```bash
docker run -d --name tech-digest --env-file .env tech-digest
```
