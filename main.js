const { app, BrowserWindow, shell, ipcMain } = require('electron');  // ipcMain 移到這裡
const path = require('path');
const http = require('http');

// 共用的 webPreferences
const sharedWebPrefs = {
  preload: path.join(__dirname, 'preload.js'),
  nodeIntegration: false,
  contextIsolation: true,
};

function createWindow() {
  // ── 主視窗 ──────────────────────────────────────────
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    show: false,                          // 加上這個避免白屏
    alwaysOnTop: false,
    autoHideMenuBar: true,
    icon: path.join(__dirname, 'art/java.ico'),
    webPreferences: sharedWebPrefs
  });

  // ── ter 視窗（背景常駐）─────────────────────────────
  const terWindow = new BrowserWindow({
    width: 900,
    height: 650,
    show: false,                          // 隱藏，等前端呼叫才顯示
    alwaysOnTop: true,                    // 呼出時保持最上層
    autoHideMenuBar: true,
    skipTaskbar: true,                    // 不出現在工作列
    icon: path.join(__dirname, 'art/java.ico'),
    webPreferences: sharedWebPrefs
  });

  // ── IPC 事件 ─────────────────────────────────────────
  ipcMain.on('open-devtools', () => {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  });

  ipcMain.on('show-ter', () => {
    if (terWindow.isVisible()) {
      terWindow.focus();
    } else {
      terWindow.show();
    }
  });

  ipcMain.on('hide-ter', () => {
    terWindow.hide();
  });

  ipcMain.on('toggle-ter', () => {
    terWindow.isVisible() ? terWindow.hide() : terWindow.show();
  });

  // ── 載入邏輯（共用，帶重試）──────────────────────────
  function loadWhenReady(window, url) {
    let isLoaded = false;

    function check() {
      if (isLoaded) return;
      const req = http.request(
        { hostname: 'localhost', port: 486, path: new URL(url).pathname, method: 'GET', timeout: 5000 },
        (res) => {
          if (res.statusCode === 200) {
            window.loadURL(url);
          } else {
            setTimeout(check, 1000);
          }
        }
      );
      req.on('error', () => setTimeout(check, 1000));
      req.on('timeout', () => { req.destroy(); setTimeout(check, 1000); });
      req.end();
    }

    window.webContents.on('did-finish-load', () => { isLoaded = true; });
    check();
  }

  // 兩個視窗同時開始嘗試載入
  loadWhenReady(mainWindow, 'http://localhost:486');
  loadWhenReady(terWindow,  'http://localhost:486/ter.html');

  // 主視窗渲染完才顯示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // ter 視窗關閉按鈕改成「隱藏」而非真的關閉
  terWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      terWindow.hide();
    }
  });

  // ── 攔截跳轉（主視窗）────────────────────────────────
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith('http://localhost:486')) {
      event.preventDefault();
      shell.openExternal(url);
    }
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.includes('setting.html') || url.startsWith('http://localhost:486')) {
      return {
        action: 'allow',
        overrideBrowserWindowOptions: {
          width: 700,
          height: 800,
          alwaysOnTop: true,
          autoHideMenuBar: true
        }
      };
    }
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

app.whenReady().then(createWindow);

app.on('before-quit', () => { app.isQuiting = true; });

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});