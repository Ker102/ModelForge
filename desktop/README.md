# ModelForge Desktop (Electron)

This folder contains the Electron shell that wraps the ModelForge web experience and exposes local integrations such as the Blender MCP bridge.

## Development

1. Install dependencies:
   ```bash
   cd desktop
   npm install
   ```
   (Run in a network-enabled environment—no dependencies are vendored in this repo.)

2. Start the Next.js app from the repository root:
   ```bash
   npm run dev
   ```

3. In another terminal, launch the Electron shell:
   ```bash
   cd desktop
   npm run dev
   ```

By default the window loads `http://localhost:3000/dashboard`. Override with `MODELFORGE_DESKTOP_START_URL`.

## Environment

The Electron process forwards Blender MCP configuration to the renderer via the secure preload bridge:

- `BLENDER_MCP_HOST` (defaults to `127.0.0.1`)
- `BLENDER_MCP_PORT` (defaults to `9876`)

Access the values in the renderer using:

```ts
const config = await window.modelforge.getMcpConfig()
```

> Never hard-code secrets in the renderer bundle. Keep credentials in local `.env` files.

## Packaging

Production bundling is not configured yet. Recommended tools for the next phase:

- [`electron-builder`](https://www.electron.build/)
- [`electron-vite`](https://electron-vite.org/) or [`vite`](https://vitejs.dev/) for a richer renderer pipeline
- Auto-updates via GitHub releases or custom distribution

Contributions welcome!
