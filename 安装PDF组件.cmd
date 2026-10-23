@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "TESTLAB_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%TESTLAB_PY%" goto bundled
where py >nul 2>nul
if %errorlevel%==0 goto launcher
where python >nul 2>nul
if %errorlevel%==0 goto normal
echo 请先安装Python 3.10或更高版本。
pause
exit /b 1
:bundled
"%TESTLAB_PY%" -m pip install -r requirements.txt
goto finish
:launcher
py -3 -m pip install -r requirements.txt
goto finish
:normal
python -m pip install -r requirements.txt
:finish
pause
