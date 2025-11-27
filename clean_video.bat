@echo off
REM Simple Windows Batch Script for Non-Technical Users
REM Double-click this file to clean your videos!

echo ========================================
echo   Video Profanity Filter
echo   FREE VidAngel Alternative
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

echo Python detected: OK
echo.

REM Check if dependencies are installed
python -c "import faster_whisper" >nul 2>&1
if errorlevel 1 (
    echo Installing required software (one-time only)...
    echo This may take 2-5 minutes...
    echo.
    pip install -r requirements.txt
    echo.
    echo Installation complete!
    echo.
)

REM Prompt for video file
echo Drag and drop your video file here, then press Enter:
set /p VIDEO_FILE=

REM Remove quotes if user dragged and dropped
set VIDEO_FILE=%VIDEO_FILE:"=%

REM Check if file exists
if not exist "%VIDEO_FILE%" (
    echo.
    echo ERROR: Video file not found!
    echo Please make sure the file path is correct.
    echo.
    pause
    exit /b
)

echo.
echo ========================================
echo Processing your video...
echo ========================================
echo.
echo This may take 15-45 minutes depending on:
echo - Video length
echo - Your computer speed
echo - Amount of profanity detected
echo.
echo You can minimize this window and do other work.
echo DO NOT close this window until processing completes!
echo.

REM Run the cleaning script
python clean.py "%VIDEO_FILE%"

echo.
echo ========================================
echo Processing Complete!
echo ========================================
echo.
echo Your cleaned video is saved in the same folder as the original.
echo Filename: [original_name]_cleaned.mp4
echo.
echo Press any key to exit...
pause >nul
