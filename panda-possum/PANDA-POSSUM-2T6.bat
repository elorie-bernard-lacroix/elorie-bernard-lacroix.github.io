@echo off
setlocal


REM Define absolute paths based on the script location to ensure correct execution
set "BASE_DIR=%~dp0"
set "VENV_DIR=%BASE_DIR%venv"
set "REQ_FILE=%BASE_DIR%cc-code\requirements.txt"
set "MAIN_SCRIPT=%BASE_DIR%cc-code\main.py"

REM Ensure we are in the correct directory (go into parent directory of the script)
cd /d "%BASE_DIR%"


REM 1. Create strict virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating isolated virtual environment...
    python -m venv "%VENV_DIR%"
)


REM 2. Detect Python Executable Location (Scripts vs bin)

REM Standard Windows Python uses 'Scripts', but some setups use 'bin'
if exist "%VENV_DIR%\Scripts\python.exe" (
    set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
    set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"
) else if exist "%VENV_DIR%\bin\python.exe" (
    set "PYTHON_EXE=%VENV_DIR%\bin\python.exe"
    set "PIP_EXE=%VENV_DIR%\bin\pip.exe"
) else (
    echo Error: Python executable not found in venv.
    echo Searched in:
    echo  - %VENV_DIR%\Scripts\python.exe
    echo  - %VENV_DIR%\bin\python.exe
    echo.
    echo It is possible the venv is corrupted. Try deleting the 'venv' folder and running this script again.
    pause
    exit /b 1
)


REM 3. Install dependencies strictly into the venv, bypassing cache
echo checking dependencies...

REM We use --no-cache-dir to ensure we don't use cached wheels
"%PIP_EXE%" install --no-cache-dir --upgrade -r "%REQ_FILE%"

echo.
echo Dependencies secured. Starting PANDA-POSSUM...
echo ---------------------------------------------------


REM 4. Execute the main program using the VENV python executable
"%PYTHON_EXE%" "%MAIN_SCRIPT%"

if %errorlevel% neq 0 (
    echo.
    echo The program encountered an error (Code: %errorlevel%).
    pause
) else (
    echo.
    echo Execution finished successfully.
    pause
)