# Cloud ChatGLM Bot - 课程设计项目

基于 ChatGLM3-6B 的云端智能聊天机器人系统，实现模型服务化部署。

## 功能特性
- 用户注册与登录
- 聊天历史持久化（SQLite）
- RESTful API 接口
- 支持多进程部署（Nginx + Uvicorn）
- 可扩展为云服务

## 运行方式（Windows）

1. 安装 Python 3.10
2. 运行 `scripts/setup_env.bat`
3. 运行 `scripts/start_api.bat`
4. 新窗口运行：`streamlit run frontend/chat_ui.py`
5. 访问 http://localhost:8501

## 技术栈
FastAPI, Streamlit, SQLite, Transformers, Nginx
