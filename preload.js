const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openDevTools: () => ipcRenderer.send('open-devtools'),
  readLogFile: (filename) => ipcRenderer.invoke('read-log-file', filename),
});