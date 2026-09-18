@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem 找 Python：优先 py 启动器，其次 PATH 里的 python
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
  goto run
)
where python >nul 2>nul
if %errorlevel%==0 (
  set "PY=python"
  goto run
)
echo [X] 没找到 Python。请先安装 Python 3.9+ 并勾选 "Add Python to PATH"。
echo     下载地址：https://www.python.org/downloads/
pause
exit /b 1

:run
%PY% "%~dp0run.py"
if errorlevel 1 pause
