#!/bin/bash
#
# Daily Tech Digest 部署脚本
# 用法: ./deploy.sh [command]
#
# 命令:
#   deploy   - 【推荐】快速部署：上传代码到服务器并构建
#   build    - 本地构建 Docker 镜像
#   push     - 推送本地镜像到服务器并部署
#   logs     - 查看容器日志
#   status   - 查看容器状态
#   restart  - 重启容器
#   stop     - 停止容器
#   run      - 在服务器上立即执行一次
#   test     - 本地测试运行

set -e

# 配置
IMAGE_NAME="tech-digest"
CONTAINER_NAME="tech-digest"
SERVER="root@104.156.250.197"
REMOTE_DIR="/opt/tech-digest"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 构建镜像
build() {
    log_info "构建 Docker 镜像..."
    docker build -t $IMAGE_NAME .
    log_info "镜像构建完成: $IMAGE_NAME"
}

# 本地测试
test_local() {
    log_info "本地测试运行..."
    docker run --rm --env-file .env $IMAGE_NAME python tech_digest_agent.py --test
}

# 推送到服务器并部署
push() {
    log_info "检查 .env 文件..."
    if [ ! -f .env ]; then
        log_error ".env 文件不存在，请先创建"
        exit 1
    fi

    log_info "保存镜像为 tar 文件..."
    docker save $IMAGE_NAME | gzip > /tmp/${IMAGE_NAME}.tar.gz

    log_info "创建远程目录..."
    ssh $SERVER "mkdir -p $REMOTE_DIR"

    log_info "上传镜像到服务器..."
    scp /tmp/${IMAGE_NAME}.tar.gz $SERVER:$REMOTE_DIR/

    log_info "上传 .env 文件..."
    scp .env $SERVER:$REMOTE_DIR/

    log_info "在服务器上加载镜像并启动容器..."
    ssh $SERVER << 'ENDSSH'
cd /opt/tech-digest

# 加载镜像
echo "加载 Docker 镜像..."
gunzip -c tech-digest.tar.gz | docker load

# 停止旧容器
echo "停止旧容器..."
docker stop tech-digest 2>/dev/null || true
docker rm tech-digest 2>/dev/null || true

# 启动新容器
echo "启动新容器..."
docker run -d \
    --name tech-digest \
    --restart unless-stopped \
    --env-file .env \
    -v /opt/tech-digest/output:/app/output \
    tech-digest

# 清理
rm -f tech-digest.tar.gz

echo "部署完成！"
docker ps | grep tech-digest
ENDSSH

    log_info "清理本地临时文件..."
    rm -f /tmp/${IMAGE_NAME}.tar.gz

    log_info "部署完成！"
}

# 查看日志
logs() {
    ssh $SERVER "docker logs -f --tail 100 $CONTAINER_NAME"
}

# 查看状态
status() {
    ssh $SERVER "docker ps -a | grep $CONTAINER_NAME || echo '容器未运行'"
}

# 重启
restart() {
    log_info "重启容器..."
    ssh $SERVER "docker restart $CONTAINER_NAME"
    log_info "重启完成"
}

# 停止
stop() {
    log_info "停止容器..."
    ssh $SERVER "docker stop $CONTAINER_NAME"
    log_info "已停止"
}

# 立即执行一次
run_once() {
    log_info "在服务器上立即执行一次..."
    ssh $SERVER "docker exec $CONTAINER_NAME python tech_digest_agent.py --test"
}

# 快速部署（上传代码到服务器并重新构建）
deploy() {
    log_info "快速部署：上传代码并在服务器上构建..."

    log_info "上传代码文件..."
    scp Dockerfile requirements.txt tech_digest_agent.py $SERVER:$REMOTE_DIR/

    # 检查是否有 .env 更新
    if [ -f .env ]; then
        log_info "上传 .env 文件..."
        scp .env $SERVER:$REMOTE_DIR/
    fi

    log_info "在服务器上构建并部署..."
    ssh $SERVER << 'ENDSSH'
cd /opt/tech-digest

echo "构建 Docker 镜像..."
docker build -t tech-digest .

echo "重启容器..."
docker stop tech-digest 2>/dev/null || true
docker rm tech-digest 2>/dev/null || true

docker run -d \
    --name tech-digest \
    --restart unless-stopped \
    --env-file .env \
    -v /opt/tech-digest/output:/app/output \
    tech-digest

echo "部署完成！"
docker ps | grep tech-digest
ENDSSH

    log_info "部署完成！"
}

# 显示帮助
help() {
    echo "Daily Tech Digest 部署脚本"
    echo ""
    echo "用法: ./deploy.sh [command]"
    echo ""
    echo "命令:"
    echo "  deploy   - 【推荐】快速部署：上传代码到服务器并构建"
    echo "  build    - 本地构建 Docker 镜像"
    echo "  test     - 本地测试运行"
    echo "  push     - 推送本地镜像到服务器并部署"
    echo "  logs     - 查看容器日志"
    echo "  status   - 查看容器状态"
    echo "  restart  - 重启容器"
    echo "  stop     - 停止容器"
    echo "  run      - 在服务器上立即执行一次"
    echo "  help     - 显示此帮助"
}

# 主逻辑
case "${1:-help}" in
    deploy)  deploy ;;
    build)   build ;;
    test)    test_local ;;
    push)    push ;;
    logs)    logs ;;
    status)  status ;;
    restart) restart ;;
    stop)    stop ;;
    run)     run_once ;;
    help)    help ;;
    *)       log_error "未知命令: $1"; help; exit 1 ;;
esac
