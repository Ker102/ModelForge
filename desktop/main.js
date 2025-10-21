const path = require("node:path")
const { app, BrowserWindow, ipcMain, nativeTheme } = require("electron")

const DEFAULT_START_URL = "http://localhost:3000/dashboard"

function resolveStartUrl() {
  return (
    process.env.MODELFORGE_DESKTOP_START_URL?.trim() ||
    (process.env.NODE_ENV === "production"
      ? DEFAULT_START_URL.replace("localhost:3000", "127.0.0.1:3000")
      : DEFAULT_START_URL)
  )
}

function getMcpConfigFromEnv() {
  return {
    host: process.env.BLENDER_MCP_HOST || "127.0.0.1",
    port: Number.parseInt(process.env.BLENDER_MCP_PORT || "9876", 10),
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 640,
    title: "ModelForge",
    backgroundColor: nativeTheme.shouldUseDarkColors ? "#0f172a" : "#ffffff",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
  })

  win.on("page-title-updated", (event) => {
    event.preventDefault()
  })

  const url = resolveStartUrl()
  win.loadURL(url).catch((error) => {
    console.error("Failed to load renderer URL:", error)
    win.loadFile(path.join(__dirname, "renderer", "offline.html")).catch(() => {
      // If the offline fallback fails to load we simply show a blank window.
    })
  })

  return win
}

app.on("ready", () => {
  createWindow()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit()
  }
})

ipcMain.handle("mcp:get-config", () => {
  return getMcpConfigFromEnv()
})
