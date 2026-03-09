const { contextBridge, ipcRenderer } = require('electron');

// 暴露一個安全的方法給前端 HTML
contextBridge.exposeInMainWorld('electronAPI', {
    openDevTools: () => ipcRenderer.send('open-devtools')
});