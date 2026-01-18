const path = require("node:path")
const { spawn } = require("node:child_process")
const { app, BrowserWindow, ipcMain, nativeTheme, dialog } = require("electron")

// Configuration
const DEFAULT_PORT = 3000
const IS_DEV = process.env.MODELFORGE_DESKTOP_ENV === "development"

let mainWindow = null
let serverProcess = null
let serverReady = false

/**
 * Get the URL to load in the renderer
 */
function getStartUrl() {
  const customUrl = process.env.MODELFORGE_DESKTOP_START_URL?.trim()
  if (customUrl) return customUrl

  const port = process.env.PORT || DEFAULT_PORT
  return `http://127.0.0.1:${port}/dashboard`
}

/**
 * Start the bundled Next.js server (production mode)
 */
function startBundledServer() {
  return new Promise((resolve, reject) => {
    if (IS_DEV) {
      // In dev mode, assume Next.js is running externally
      console.log("[Desktop] Development mode - expecting external Next.js server")
      serverReady = true
      resolve()
      return
    }

    // In production, start the bundled server
    const serverPath = path.join(process.resourcesPath, "server")
    const serverScript = path.join(serverPath, "server.js")

    console.log("[Desktop] Starting bundled server from:", serverPath)

    try {
      serverProcess = spawn(process.execPath.replace("electron", "node"), [serverScript], {
        cwd: serverPath,
        env: {
          ...process.env,
          PORT: String(DEFAULT_PORT),
          NODE_ENV: "production",
        },
        stdio: "pipe",
      })

      serverProcess.stdout.on("data", (data) => {
        const output = data.toString()
        console.log("[Server]", output)

        // Check if server is ready
        if (output.includes("Ready") || output.includes("started") || output.includes("listening")) {
          serverReady = true
          resolve()
        }
      })

      serverProcess.stderr.on("data", (data) => {
        console.error("[Server Error]", data.toString())
      })

      serverProcess.on("error", (error) => {
        console.error("[Desktop] Failed to start server:", error)
        reject(error)
      })

      serverProcess.on("exit", (code) => {
        console.log("[Desktop] Server exited with code:", code)
        serverProcess = null
      })

      // Timeout fallback
      setTimeout(() => {
        if (!serverReady) {
          serverReady = true
          resolve()
        }
      }, 5000)

    } catch (error) {
      console.error("[Desktop] Server spawn error:", error)
      reject(error)
    }
  })
}

/**
 * Get MCP configuration from environment
 */
function getMcpConfigFromEnv() {
  return {
    host: process.env.BLENDER_MCP_HOST || "127.0.0.1",
    port: Number.parseInt(process.env.BLENDER_MCP_PORT || "9876", 10),
  }
}

/**
 * Create the main application window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: "ModelForge",
    backgroundColor: nativeTheme.shouldUseDarkColors ? "#0f172a" : "#ffffff",
    icon: path.join(__dirname, "assets", "icon.png"),
    show: false, // Don't show until ready
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
  })

  // Prevent title changes from web content
  mainWindow.on("page-title-updated", (event) => {
    event.preventDefault()
  })

  // Show window when ready
  mainWindow.once("ready-to-show", () => {
    mainWindow.show()
  })

  // Load the app
  const url = getStartUrl()
  console.log("[Desktop] Loading URL:", url)

  mainWindow.loadURL(url).catch((error) => {
    console.error("[Desktop] Failed to load URL:", error)

    // Show error dialog
    dialog.showErrorBox(
      "Connection Error",
      IS_DEV
        ? "Could not connect to the Next.js development server.\n\nMake sure to run 'npm run dev' in the main project directory first."
        : "Could not start the ModelForge server.\n\nPlease try restarting the application."
    )

    // Load offline page
    mainWindow.loadFile(path.join(__dirname, "renderer", "offline.html")).catch(() => { })
  })

  mainWindow.on("closed", () => {
    mainWindow = null
  })

  return mainWindow
}

/**
 * App initialization
 */
app.on("ready", async () => {
  console.log("[Desktop] App ready, starting...")
  console.log("[Desktop] Mode:", IS_DEV ? "development" : "production")

  try {
    // Start bundled server if in production
    if (!IS_DEV) {
      await startBundledServer()
    }

    createWindow()
  } catch (error) {
    console.error("[Desktop] Startup error:", error)
    dialog.showErrorBox("Startup Error", error.message)
    app.quit()
  }

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

/**
 * Clean up on quit
 */
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit()
  }
})

app.on("before-quit", () => {
  // Kill server process if running
  if (serverProcess) {
    console.log("[Desktop] Stopping server...")
    serverProcess.kill()
    serverProcess = null
  }
})

/**
 * IPC Handlers
 */
ipcMain.handle("mcp:get-config", () => {
  return getMcpConfigFromEnv()
})

ipcMain.handle("app:get-info", () => {
  return {
    version: app.getVersion(),
    platform: process.platform,
    arch: process.arch,
    isDev: IS_DEV,
  }
})
