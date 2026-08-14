@echo off
TITLE Meeting Audio Recorder & AI Transcriber
COLOR 0A
CD /D "%~dp0"

echo ================================================================
echo  🎙️ MEETING AUDIO RECORDER & AI TRANSCRIBER (FFmpeg + Gemini)
echo ================================================================
echo.
echo  Starting recording...
echo  - Recording System Audio & Meeting Calls (WASAPI)
echo  - Filtered for Vocal Frequency (Noise & Mouse Click Reduction)
echo.
echo  [IMPORTANT] Press Ctrl+C in this window when your meeting ends
echo              to stop recording and start AI transcription!
echo.
echo ================================================================
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0scripts\meeting_audio_pipeline.py"

echo.
echo ================================================================
echo  ✅ Processing complete! Check data\recordings\ for JSON output.
echo ================================================================
pause
