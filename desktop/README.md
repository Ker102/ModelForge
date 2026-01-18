# ModelForge Desktop

Electron shell for the ModelForge Blender assistant.

## Development

```bash
# First, start the Next.js dev server in the main project
cd ..
npm run dev

# Then start the Electron app in development mode
cd desktop
npm install
npm run dev
```

## Production Build

The desktop app bundles the entire application for standalone distribution.

### Prerequisites

```bash
# Build the Next.js standalone output first
cd ..
npm run build:standalone

# Install desktop dependencies
cd desktop
npm install
```

### Build Commands

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build:win      # Windows (NSIS installer + portable)
npm run build:mac      # macOS (DMG)
npm run build:linux    # Linux (AppImage + .deb)

# Build for all platforms
npm run build:all
```

### Output

Builds are placed in `desktop/dist/`:
- **Windows**: `ModelForge-0.1.0-win-x64.exe` (installer), `ModelForge-0.1.0-win-x64-portable.exe`
- **macOS**: `ModelForge-0.1.0-mac-x64.dmg`, `ModelForge-0.1.0-mac-arm64.dmg`
- **Linux**: `ModelForge-0.1.0-linux-x64.AppImage`, `ModelForge-0.1.0-linux-x64.deb`

## App Icons

Place icons in `desktop/assets/`:
- `icon.ico` (256x256 for Windows)
- `icon.icns` (for macOS)
- `icon.png` (512x512 for Linux)

## Distribution

Users download the installer/portable and run it directly - **no additional setup required**.

The bundled app includes:
- ✅ Next.js server (standalone mode)
- ✅ All dependencies
- ✅ Auto-update support (via electron-updater)
