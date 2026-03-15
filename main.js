const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const http = require('http');


function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    alwaysOnTop: false,
    autoHideMenuBar: true,
    icon: path.join(__dirname, 'art/java.ico'), // 實現你之前想要的強制最上層
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // 載入剛剛建的檔案
      nodeIntegration: false, // 為了安全，通常設為 false
      contextIsolation: true, // 啟用上下文隔離，增強安全性
    }
  });
  // 監聽前端發來的訊號
  const { ipcMain } = require('electron');
  ipcMain.on('open-devtools', () => {
      mainWindow.webContents.openDevTools({mode: 'detach' });
  });
  
    
    
  // 載入你的本地 HTTP 伺服器網址，並重試直到連上
  let isLoaded = false;

  function checkServerAndLoad() {
    if (isLoaded) return;

    const req = http.request({
      hostname: 'localhost',
      port: 486,
      path: '/',
      method: 'GET',
      timeout: 5000
    }, (res) => {
      
      if (res.statusCode === 200) {
        mainWindow.loadURL('http://localhost:486');
      } else {
        
        setTimeout(checkServerAndLoad, 1000);
      }
    });

    req.on('error', (err) => {
      
      setTimeout(checkServerAndLoad, 1000);
    });

    req.on('timeout', () => {
      
      req.destroy();
      setTimeout(checkServerAndLoad, 1000);
    });

    req.end();
  }

  mainWindow.webContents.on('did-finish-load', () => {
    
    isLoaded = true;
  });

  checkServerAndLoad(); // 初始檢查並載入 
  

  // --- 攔截跳轉邏輯 ---
  
  // 1. 防止主視窗內容被換掉 (will-navigate)
  mainWindow.webContents.on('will-navigate', (event, url) => {
    const currentUrl = mainWindow.webContents.getURL();
    // 如果跳轉目標不是原本的伺服器，就攔截
    if (!url.startsWith('http://localhost:8080')) {
      event.preventDefault();
      shell.openExternal(url); // 改用外部瀏覽器開啟 (如 Chrome)
    }
  });

  // 2. 處理 window.open(url, '_blank')
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // 檢查：如果網址包含 'setting.html' 或者是你本地伺服器的檔案
    if (url.includes('setting.html') || url.startsWith('http://localhost:486')) {
      
      return { 
        action: 'allow',
        overrideBrowserWindowOptions: {
          width: 700,
          height: 800,
          alwaysOnTop: true, // 設定頁面也可以考慮置頂
          autoHideMenuBar: true // 隱藏上方選單讓它更像一個獨立 App
        }
      };
    }

    // 其他外部連結（如 Google, Discord）依然丟給瀏覽器
    
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

app.whenReady().then(createWindow);

// 當所有視窗關閉時退出程式 (Windows/Linux 標準)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});