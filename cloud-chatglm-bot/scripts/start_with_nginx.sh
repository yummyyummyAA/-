#!/bin/bash
# 先安装 nginx: sudo apt install nginx

# 启动多个 Uvicorn 工作进程（需 gunicorn）
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000 app.main:app &

# 启动 Nginx（确保配置已复制）
sudo nginx -c $(pwd)/config/nginx.conf

echo "服务已启动！访问 http://localhost"