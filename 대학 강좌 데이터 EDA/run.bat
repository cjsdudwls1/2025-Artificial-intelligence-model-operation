@echo off
echo ====================================
echo 대학 강좌 데이터 EDA 애플리케이션
echo ====================================
echo.

echo [1/2] 필요한 패키지 설치 중...
pip install -r requirements.txt

echo.
echo [2/2] 애플리케이션 시작...
echo.
echo 브라우저가 자동으로 열립니다.
echo 외부 공유 링크는 터미널에서 확인하세요.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

python app.py

pause

