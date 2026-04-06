const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openDevTools: () => ipcRenderer.send('open-devtools'),

  // ter 視窗控制
  showTer:   () => ipcRenderer.send('show-ter'),
  hideTer:   () => ipcRenderer.send('hide-ter'),
  toggleTer: () => ipcRenderer.send('toggle-ter'),
});