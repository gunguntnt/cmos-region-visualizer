@echo off
setlocal
cd /d "%~dp0\.."

python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --windowed --name CMOSRegionVisualizer --paths src src\cmos_region_visualizer\main.py

echo.
echo Build complete. Check dist\CMOSRegionVisualizer\ or dist\CMOSRegionVisualizer.exe depending on PyInstaller settings.
endlocal
