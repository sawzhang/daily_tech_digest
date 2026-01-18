# /deploy - Daily Tech Digest 部署技能

## 描述
部署 Daily Tech Digest 到云端服务器。

## 服务器信息
- **地址**: `root@104.156.250.197`
- **项目路径**: `/opt/tech-digest`
- **容器名**: `tech-digest`
- **定时执行**: 每天 08:00 (北京时间)

## 快速部署（推荐）

修复代码问题后，一条命令完成部署：

```bash
./deploy.sh deploy
```

这会自动：
1. 上传代码文件到服务器
2. 在服务器上构建 Docker 镜像
3. 重启容器

## deploy.sh 命令一览

| 命令 | 说明 |
|------|------|
| `./deploy.sh deploy` | **【推荐】快速部署：上传代码并在服务器构建** |
| `./deploy.sh logs` | 查看容器日志 |
| `./deploy.sh status` | 查看容器状态 |
| `./deploy.sh run` | 在服务器上立即执行一次（测试模式） |
| `./deploy.sh restart` | 重启容器 |
| `./deploy.sh stop` | 停止容器 |
| `./deploy.sh build` | 本地构建 Docker 镜像 |
| `./deploy.sh push` | 推送本地镜像到服务器（镜像较大，较慢） |
| `./deploy.sh test` | 本地测试运行 |

## 常用操作

### 查看日志
```bash
./deploy.sh logs
```

### 立即执行一次
```bash
./deploy.sh run
```

### 查看生成的文件
```bash
ssh root@104.156.250.197 "ls -la /opt/tech-digest/output/"
```

### 下载生成的日报
```bash
scp root@104.156.250.197:/opt/tech-digest/output/tech_digest_$(date +%Y-%m-%d).md ./
```

## 故障排查

### 容器无法启动
```bash
./deploy.sh logs
```

### 检查 .env 配置
```bash
ssh root@104.156.250.197 "cat /opt/tech-digest/.env"
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| ANTHROPIC_API_KEY | 是 | Anthropic API 密钥 |
| WECHAT_APP_ID | 否 | 微信公众号 AppID |
| WECHAT_APP_SECRET | 否 | 微信公众号 AppSecret |
| SCHEDULE_TIME | 否 | 定时执行时间，默认 08:00 |
