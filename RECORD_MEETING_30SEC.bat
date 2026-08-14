@echo off
TITLE 30-Second Quick Meeting Audio Test
COLOR 0B
CD /D "%~dp0"

echo ================================================================
echo  🎙️ 30-SECOND QUICK MEETING AUDIO TEST (FFmpeg + Gemini)
echo ================================================================
echo.
echo  Recording 30 seconds of System / Meeting audio...
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0scripts\meeting_audio_pipeline.py" --duration 30

echo.
echo ================================================================
echo  ✅ 30-Second Test Complete! JSON transcript created in data\recordings\
echo ================================================================
pause
