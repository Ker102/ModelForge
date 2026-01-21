const path = require("node:path")
const { spawn } = require("node:child_process")
const { app, BrowserWindow, ipcMain, nativeTheme, dialog, shell } = require("electron")

// Configuration
const DEFAULT_PORT = 3000
const IS_DEV = process.env.MODELFORGE_DESKTOP_ENV === "development"
const PROTOCOL = "modelforge"

// Register deep link protocol (for OAuth callback)
if (process.defaultApp) {
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient(PROTOCOL, process.execPath, [path.resolve(process.argv[1])])
  }
} else {
  app.setAsDefaultProtocolClient(PROTOCOL)
}

let mainWindow = null
let serverProcess = null
let serverReady = false
let pendingDeepLink = null

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

  // Handle external URLs (OAuth, etc.) - open in system browser
  const { shell } = require("electron")

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // Open external URLs in system browser
    if (url.startsWith("https://") && !url.includes("127.0.0.1") && !url.includes("localhost")) {
      shell.openExternal(url)
      return { action: "deny" }
    }
    return { action: "allow" }
  })

  mainWindow.webContents.on("will-navigate", (event, url) => {
    // If navigating to OAuth provider, open in system browser
    if (url.includes("supabase.co") || url.includes("accounts.google.com")) {
      event.preventDefault()
      shell.openExternal(url)
    }
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
 * Handle deep links (OAuth callback)
 * Windows/Linux: second-instance event
 * macOS: open-url event
 */
function handleDeepLink(url) {
  console.log("[Desktop] Deep link received:", url)

  if (url.startsWith(`${PROTOCOL}://`)) {
    // Parse the deep link URL
    const urlObj = new URL(url)
    const params = urlObj.searchParams

    // Check if this is an auth callback
    if (urlObj.pathname === "/auth/callback" || urlObj.host === "auth") {
      const accessToken = params.get("access_token")
      const refreshToken = params.get("refresh_token")

      if (accessToken && mainWindow) {
        // Send tokens to renderer to complete auth
        mainWindow.webContents.send("auth:token", { accessToken, refreshToken })
        mainWindow.focus()
      } else if (mainWindow) {
        // Navigate to callback URL in app
        const port = process.env.PORT || DEFAULT_PORT
        const callbackUrl = `http://127.0.0.1:${port}/auth/callback?${params.toString()}`
        mainWindow.loadURL(callbackUrl)
        mainWindow.focus()
      }
    }
  }
}

// Windows/Linux: Handle protocol when app is already running
const gotTheLock = app.requestSingleInstanceLock()
if (!gotTheLock) {
  app.quit()
} else {
  app.on("second-instance", (event, commandLine) => {
    // Find the deep link URL in command line args
    const deepLinkUrl = commandLine.find((arg) => arg.startsWith(`${PROTOCOL}://`))
    if (deepLinkUrl) {
      handleDeepLink(deepLinkUrl)
    }

    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })
}

// macOS: Handle protocol
app.on("open-url", (event, url) => {
  event.preventDefault()
  if (app.isReady()) {
    handleDeepLink(url)
  } else {
    pendingDeepLink = url
  }
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

ipcMain.handle("addon:get-path", () => {
  // In production, addon is in resources/assets
  // In dev, it's in desktop/assets
  const addonPath = IS_DEV
    ? path.join(__dirname, "assets", "modelforge-addon.py")
    : path.join(process.resourcesPath, "assets", "modelforge-addon.py")

  return {
    path: addonPath,
    exists: require("fs").existsSync(addonPath)
  }
})

ipcMain.handle("addon:open-folder", () => {
  const { shell } = require("electron")
  const addonPath = IS_DEV
    ? path.join(__dirname, "assets")
    : path.join(process.resourcesPath, "assets")

  shell.openPath(addonPath)
  return { opened: true, path: addonPath }
})
