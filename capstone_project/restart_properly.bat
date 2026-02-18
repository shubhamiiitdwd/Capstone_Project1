@echo off
echo ========================================
echo RESTARTING STREAMLIT APP
echo ========================================
echo.
echo This will restart the app with the new configuration
echo.
echo Step 1: Stopping any running Streamlit processes...
taskkill /F /IM streamlit.exe 2>nul
timeout /t 2 >nul
echo.
echo Step 2: Starting Streamlit with new configuration...
echo.
streamlit run app.py
