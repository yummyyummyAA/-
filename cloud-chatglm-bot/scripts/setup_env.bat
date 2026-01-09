@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r ..\requirements.txt
echo.
echo 环境安装完成！运行 start_api.bat 启动服务。
pause