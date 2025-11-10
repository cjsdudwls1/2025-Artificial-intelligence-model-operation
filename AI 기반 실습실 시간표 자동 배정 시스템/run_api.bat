@echo off
echo FastAPI 서버를 시작합니다...
cd /d %~dp0
uvicorn api:app --reload --host 127.0.0.1 --port 8000
pause

