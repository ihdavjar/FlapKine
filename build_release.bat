@echo off
setlocal enabledelayedexpansion

REM 💡 Get version from Python
for /f %%i in ('python -c "from version import __version__; print(__version__)"') do set VERSION=%%i

echo 🚀 Starting Flapkine release pipeline
echo 📦 Current version: %VERSION%

REM 🧹 Clean previous builds
echo Deleting build and dist folders...
rmdir /s /q build
rmdir /s /q dist

REM 🛠️ Run PyInstaller
echo Running PyInstaller...
pyinstaller flapkine.spec

REM 📝 Update Inno Setup version
echo Updating Inno Setup script version to %VERSION%...
powershell -Command "(Get-Content installer\flapkine_installer.iss) -replace 'AppVersion=.*', 'AppVersion=%VERSION%' | Set-Content installer\flapkine_installer.iss"

REM 📦 Run Inno Setup compiler
echo Compiling installer with Inno Setup...
ISCC installer\flapkine_installer.iss

REM 🏷️ Git commit + tag
echo Tagging release...
git add flapkine\version.py
git commit -m "Release v%VERSION%"
git tag v%VERSION%
git push origin main --tags

echo ✅ Release pipeline complete for version %VERSION%
pause
