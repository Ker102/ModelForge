const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("modelforge", {
  getMcpConfig: async () => {
    return ipcRenderer.invoke("mcp:get-config")
  },
})

