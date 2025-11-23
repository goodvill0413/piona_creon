@echo off
chcp 65001 >nul
title 크레온연결복구 — PIONA 연구소 (디버그 모드)

echo.
echo ================================================
echo     PIONA_CREON 연구소 — 연결복구 + 실행기
echo ================================================
echo.

cd /d "D:\PIONA_Creon"
if %errorlevel% neq 0 (
    echo [실패] D:\PIONA_Creon 폴더가 없습니다!
    pause
    exit /b
)

echo ✓ 루트 폴더 이동 완료

if not exist creon_venv (
    echo 창고 없음 → 32bit 가상환경 새로 만드는 중...
    C:\Python38-32\python.exe -m venv creon_venv
)

echo 가상환경 활성화 중...
call creon_venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [실패] 가상환경 활성화 실패!
    pause
    exit /b
)

echo 필수 패키지 확인/설치 중...
pip install --quiet pywin32 pandas numpy >nul 2>&1

echo.
echo CREON 연결 상태 확인 중...
python -c "import win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('→ CREON 연결 성공' if c.IsConnect else '→ CREON Plus 실행 후 로그인하세요')" 

echo.
echo ================================================
echo               main.py 실행 시작
echo ================================================
echo.

python get_data_only.py

echo.
echo ================================================
echo                실행 종료
echo ================================================

echo.
echo ================================================================
echo   ⚠️  반드시 관리자 권한으로 실행하세요
echo ================================================================
echo   • CREON Plus 는 관리자권한이 아닐 경우 COM 연결이 끊어질 수 있습니다.
echo   • "크레온연결복구.bat" 도 반드시 관리자권한으로 실행해야 합니다.
echo   • 관리자권한이 아니면 연결 상태가 0 으로 나오거나
echo     주문/조회 기능이 정상 동작하지 않습니다.
echo ================================================================
echo.


pause