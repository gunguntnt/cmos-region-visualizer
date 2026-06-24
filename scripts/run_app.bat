@echo off
setlocal
cd /d "%~dp0\.."
set PYTHONPATH=%CD%\src
python -m cmos_region_visualizer.main
endlocal
