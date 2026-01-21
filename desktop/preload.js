const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("modelforge", {
  // MCP Configuration
  getMcpConfig: async () => {
    return ipcRenderer.invoke("mcp:get-config")
  },

  // App Info
  getAppInfo: async () => {
    return ipcRenderer.invoke("app:get-info")
  },

  // Addon Management
  getAddonPath: async () => {
    return ipcRenderer.invoke("addon:get-path")
  },

  openAddonFolder: async () => {
    return ipcRenderer.invoke("addon:open-folder")
  },
})
