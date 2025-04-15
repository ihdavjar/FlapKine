#!/bin/bash

set -e

echo "🚀 Starting Flapkine release pipeline"

# 1. Read current version
VERSION=$(python -c "from flapkine.version import __version__; print(__version__)")
echo "📦 Current version: $VERSION"

# 2. Clean old builds
rm -rf build/ dist/
echo "🧹 Cleaned previous builds"

# 3. Run PyInstaller
echo "🛠️ Building with PyInstaller..."
pyinstaller flapkine.spec

# 4. Update Inno Setup version
echo "📝 Updating Inno Setup script with version..."
sed -i "s/^AppVersion=.*/AppVersion=$VERSION/" installer/flapkine_installer.iss

# 5. Build installer
echo "📦 Creating Windows installer..."
ISCC "installer/flapkine_installer.iss"

# 6. Optional: Create Git tag
echo "🏷️ Tagging release in Git"
git add flapkine/version.py
git commit -m "Release v$VERSION"
git tag v$VERSION
git push origin main --tags

echo "✅ Release v$VERSION completed"
