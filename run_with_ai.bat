@echo off
echo 🚀 AI-Powered Market Intelligence System
echo ==========================================

echo ✅ Using API key from .env file
echo.

REM Ask user what they want to do
echo What would you like to do?
echo 1. Run demo with AI insights
echo 2. Launch Streamlit web interface  
echo 3. Launch CLI interface
echo 4. Run full pipeline
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" (
    echo Running demo with AI insights...
    python main.py demo
) else if "%choice%"=="2" (
    echo Launching Streamlit web interface...
    python -m streamlit run streamlit_app.py
) else if "%choice%"=="3" (
    echo Launching CLI interface...
    python main.py interface --interface cli
) else if "%choice%"=="4" (
    echo Running full pipeline...
    python main.py pipeline --data data/raw/googleplaystore.csv
) else (
    echo Invalid choice. Running demo by default...
    python main.py demo
)

echo.
echo Press any key to exit...
pause >nul
