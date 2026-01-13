FROM python:3.11-slim

# 设置时区为北京时间
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies using uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Install Chinese fonts for cover image generation
RUN apt-get update && \
    apt-get install -y --no-install-recommends fonts-wqy-zenhei && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# Create output directory
RUN mkdir -p output

# Default: scheduled mode
CMD ["python", "tech_digest_agent.py", "--schedule"]
