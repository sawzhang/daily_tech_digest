# /deploy - Daily Tech Digest 部署技能

## 描述
部署 Daily Tech Digest 到云端服务器，支持构建、推送、查看日志等操作。

## 服务器信息
- **地址**: `root@104.156.250.197`
- **项目路径**: `/opt/tech-digest`
- **容器名**: `tech-digest`
- **定时执行**: 每天 08:00 (北京时间)

## 快速命令

### 1. 查看状态
```bash
ssh root@104.156.250.197 "docker ps | grep tech-digest"
```

### 2. 查看日志
```bash
ssh root@104.156.250.197 "docker logs -f --tail 100 tech-digest"
```

### 3. 立即执行一次（测试模式）
```bash
ssh root@104.156.250.197 "docker exec tech-digest python tech_digest_agent.py --test"
```

### 4. 重新部署（代码更新后）
```bash
# 上传新代码
scp Dockerfile requirements.txt tech_digest_agent.py .env root@104.156.250.197:/opt/tech-digest/

# SSH 到服务器重新构建和部署
ssh root@104.156.250.197 << 'EOF'
cd /opt/tech-digest
docker build -t tech-digest .
docker stop tech-digest && docker rm tech-digest
docker run -d \
    --name tech-digest \
    --restart unless-stopped \
    --env-file .env \
    -v /opt/tech-digest/output:/app/output \
    tech-digest
docker logs tech-digest
EOF
```

### 5. 重启容器
```bash
ssh root@104.156.250.197 "docker restart tech-digest"
```

### 6. 停止容器
```bash
ssh root@104.156.250.197 "docker stop tech-digest"
```

### 7. 查看生成的文件
```bash
ssh root@104.156.250.197 "ls -la /opt/tech-digest/output/"
```

### 8. 下载生成的日报
```bash
scp root@104.156.250.197:/opt/tech-digest/output/tech_digest_$(date +%Y-%m-%d).md ./
```

## 使用 deploy.sh 脚本

项目根目录有 `deploy.sh` 脚本，支持以下命令：

```bash
./deploy.sh build    # 本地构建 Docker 镜像
./deploy.sh test     # 本地测试运行
./deploy.sh push     # 推送到服务器并部署
./deploy.sh logs     # 查看容器日志
./deploy.sh status   # 查看容器状态
./deploy.sh restart  # 重启容器
./deploy.sh stop     # 停止容器
./deploy.sh run      # 在服务器上立即执行一次
```

## 故障排查

### 容器无法启动
```bash
# 查看详细错误
ssh root@104.156.250.197 "docker logs tech-digest"

# 检查 .env 文件
ssh root@104.156.250.197 "cat /opt/tech-digest/.env"
```

### API 调用失败
检查 ANTHROPIC_API_KEY 是否正确配置在 .env 文件中。

### 微信发布失败
检查 WECHAT_APP_ID 和 WECHAT_APP_SECRET 是否正确配置。

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| ANTHROPIC_API_KEY | 是 | Anthropic API 密钥 |
| WECHAT_APP_ID | 否 | 微信公众号 AppID |
| WECHAT_APP_SECRET | 否 | 微信公众号 AppSecret |
| SCHEDULE_TIME | 否 | 定时执行时间，默认 08:00 |
