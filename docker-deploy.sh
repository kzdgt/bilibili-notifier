#!/bin/bash

# Docker部署测试脚本

echo "🐳 开始测试Docker配置..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker环境检查通过"


echo "🔨 清除旧Docker镜像..."
docker rmi bilibili-notifier-bilibili-notifier

echo "🚀 启动服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "📋 查看服务状态..."
docker-compose ps

echo "📝 查看日志..."
docker-compose logs --tail=20

echo ""
echo "✅ Docker部署完成！"
echo "📖 使用说明："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "  - 进入容器: docker-compose exec bilibili-notifier /bin/bash"