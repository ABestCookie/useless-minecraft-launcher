/* filepath: c:\Users\tsai cookie\Desktop\useless minecraft launcher\ui.js */
/**
 * 控制啟動時是否自動顯示 TIP
 * 設為 true 則頁面載入時自動彈出 tip，設為 false 則不自動顯示
 */
const AUTO_SHOW_TIP = true;
const keyboardEvent = window.event;

/* showMsg 函式已移至獨立的 msgbox.js */

/* ===== 更新說明面板函數（獨立於 showMsg） ===== */
let updatePanelBack = null;
let updatePanelClose = null;
let updatePanelTitle = null;
let updatePanelContent = null;
let lastUpdatePanelFocusedElement = null;

/**
 * 顯示更新說明面板
 * @param {string} title - 標題
 * @param {string|{html?:string, url?:string}} content - 內容（HTML 字符串或含 html/url 的對象）
 * @param {object} options - 其他選項（暫保留擴展）
 * @returns {Promise<'closed'>} - Promise，resolve 為 'closed'
 */
function showUpdatePanel(title = '更新說明', content = '', options = {}) {
  // 延遲初始化，確保 DOM 已加載
  if (!updatePanelBack) {
    updatePanelBack = document.getElementById('updatePanelBack');
    updatePanelClose = document.getElementById('updatePanelClose');
    updatePanelTitle = document.getElementById('updatePanelTitle');
    updatePanelContent = document.getElementById('updatePanelContent');
  }
  
  if (!updatePanelBack) return Promise.resolve('closed');

  // 設定標題
  updatePanelTitle.textContent = title;

  // 清空內容區
  updatePanelContent.innerHTML = '';
  //小小彩蛋
  if (options.subaru) {
    updatePanelContent.innerHTML = `<iframe width="560" height="315" src="https://www.youtube.com/embed/eQhMS-KYZEY?si=Qm1hQTRigpnR4ydp&amp;controls=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>`;

// 處理內容：支援字符串（HTML）或對象（html/url）
  } else if (typeof content === 'string') { 
    // 直接作為 HTML 插入
    updatePanelContent.innerHTML = content;
  } else if (typeof content === 'object' && content !== null) {
    if (content.url) {
      // 嵌入 iframe（用來加載別的網頁）
      const iframe = document.createElement('iframe');
      iframe.src = content.url;
      iframe.setAttribute('sandbox', 'allow-same-origin allow-scripts allow-popups');
      updatePanelContent.appendChild(iframe);
    } else if (content.html) {
      // 直接插入 HTML
      updatePanelContent.innerHTML = content.html;
    }
  }

  // 顯示面板
  updatePanelBack.classList.add('show');
  updatePanelBack.setAttribute('aria-hidden', 'false');

  // 管理焦點：記錄先前焦點、聚焦到關閉按鈕
  lastUpdatePanelFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  if (updatePanelClose && typeof updatePanelClose.focus === 'function') {
    updatePanelClose.focus();
  }

  // 回傳 Promise，resolve 為 'closed'
  return new Promise(resolve => {
    const clean = () => {
      updatePanelBack.classList.remove('show');
      updatePanelBack.setAttribute('aria-hidden', 'true');
      
      // 還原焦點
      try {
        const active = document.activeElement;
        if (active && updatePanelBack.contains(active)) {
          try { active.blur(); } catch (e) { /* ignore */ }
        }
        if (lastUpdatePanelFocusedElement && typeof lastUpdatePanelFocusedElement.focus === 'function') {
          lastUpdatePanelFocusedElement.focus();
        }
      } catch (e) { /* ignore */ }

      // 移除事件監聽
      updatePanelClose.removeEventListener('click', onClose);
      document.removeEventListener('keydown', onEscClose);

      lastUpdatePanelFocusedElement = null;
      setTimeout(() => resolve('closed'), 180);
    };

    const onClose = () => clean();
    const onEscClose = (e) => {
      if (e.key === 'Escape') clean();
    };

    // 綁定關閉按鈕與 Esc
    updatePanelClose.addEventListener('click', onClose);
    document.addEventListener('keydown', onEscClose);

    // 點擊背景關閉（可選，加上這個讓使用者體驗更直覺）
    const onBackClick = (e) => {
      if (e.target === updatePanelBack) clean();
    };
    updatePanelBack.addEventListener('click', onBackClick);
  });
}

// 暴露給 eel（Python 可直接呼叫）
if (typeof eel !== 'undefined' && eel.expose) {
  try {
    eel.expose(showUpdatePanel);
  } catch (e) {
    console.debug('eel.expose for showUpdatePanel failed', e);
  }
}

/* showMsg 函式已移至 msgbox.js，showMsg 已暴露給 eel，可直接在 eel 中呼叫 */

/* 新增：管理 terminal 的 focus 與 ESC handler（用於可靠關閉） */
let lastTerminalFocusedElement = null;
let terminalEscHandler = null;



/* 更新：讓 terminal_show 也處理 focus 與 aria，並註冊 ESC 可以關閉 */
function terminal_show(message, e) {
    const terminalOutput = document.getElementById('terminalOutput');
    const terminalBack = document.getElementById('terminal');
    if (terminalOutput && terminalBack) {
        // 記錄顯示前的焦點，以便關閉時還原
        lastTerminalFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;

        terminalBack.classList.add('show');
        terminalBack.setAttribute('aria-hidden', 'false');

        terminalOutput.value += message + '\n';
        terminalOutput.scrollTop = terminalOutput.scrollHeight;

        // 把焦點放到 textarea 以便使用者可以直接滾動 / 複製
        if (typeof terminalOutput.focus === 'function') terminalOutput.focus();

        // 註冊 ESC 關閉（儲存引用以便後續移除）
        terminalEscHandler = function(evt) {
            if (evt.key === 'Escape') closeTerminal();
        };
        document.addEventListener('keydown', terminalEscHandler);
    }
}

eel.expose(terminal_show);

/* 新增：可從其他地方呼叫的關閉函式（負責 aria / focus 還原 / 清除事件） */
function closeTerminal() {
    
    const terminalOutput = document.getElementById('terminalOutput');
    const terminalBack = document.getElementById('terminal');
    if (!terminalBack) return;

    // 啟動離場（CSS transition）
    terminalBack.classList.remove('show');
    terminalOutput.value = ''; //清除

    // 如果目前焦點仍在 terminal 內，先 blur 再還原到先前元素（或 fallback）
    try {
        const active = document.activeElement;
        if (active && terminalBack.contains(active)) {
            try { active.blur(); } catch (e) { /* ignore */ }
        }

        if (lastTerminalFocusedElement && typeof lastTerminalFocusedElement.focus === 'function') {
            lastTerminalFocusedElement.focus();
        } else {
            // fallback：嘗試把焦點交給某些常見按鈕（若存在）
            const fallback = document.getElementById('openModalBtn') || document.getElementById('accountBtn') || document.getElementById('sidebarToggle');
            if (fallback && typeof fallback.focus === 'function') fallback.focus();
        }
    } catch (e) { /* ignore focus errors */ }

    // 在確保 focus 移出後更新 aria（避免 assistive tech 在有 focus 時被隱藏）
    terminalBack.setAttribute('aria-hidden', 'true');

    // 移除 ESC 監聽
    if (terminalEscHandler) {
        document.removeEventListener('keydown', terminalEscHandler);
        terminalEscHandler = null;
    }
    lastTerminalFocusedElement = null;
}

function aboutAPP() {
    showUpdatePanel('關於 UMCL', {url: './docs/index.html#/about.md' });
}


function terminal_show(message, e) {
    const terminalOutput = document.getElementById('terminalOutput');
    const terminalBack = document.getElementById('terminal');
    if (terminalOutput) {
        terminalBack.classList.add('show');
        terminalOutput.value += message + '\n';
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }
}


document.addEventListener('DOMContentLoaded', () => {
  const $ = id => document.getElementById(id);

  // 追蹤開啟 modal 前的焦點，用來在關閉時還原
  let lastFocusedElement = null;

  // 取得 modal 相關節點（已移除，modal 現在在 account.html）
  const openModalBtn = $('openModalBtn');

  // openModalBtn 改為開啟 account.html（獨立視窗）
  if (openModalBtn) {
    openModalBtn.addEventListener('click', () => {
      window.open('account.html', '_blank', 'width=800,height=600');
    });
  }

  /* Sidebar 切換（保持原本行為） */
  const sidebar = $('sidebar');
  const toggle = $('sidebarToggle');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      const collapsed = sidebar.classList.toggle('collapsed');
      toggle.setAttribute('aria-expanded', String(!collapsed));

      // 若 accountPanel 正開啟，調整 left（保留樣式控制，不直接改 display）
      const panel = $('accountPanel');
      if (panel && panel.classList.contains('show')) {
        panel.style.left = collapsed ? '66px' : '';
      }
    });
  }

  /* TIP：改為使用 class 切換 show */
  const tip = $('tip');
  const tipClose = $('tipClose');
  const tipStatus = $('tipStatus');
  const tipProgress = $('tipProgress');
  const tipProgressBar = $('tipProgressBar');
  const tipProgressLabel = $('tipProgressLabel');
  let tipMax = 0;

  

  // 依 AUTO_SHOW_TIP 決定是否在載入時顯示 tip（短延遲以確保 transition 正確觸發）
  if (tip && AUTO_SHOW_TIP) {
    // 若想立即無延遲顯示可移除 setTimeout
    tip.classList.add('show'), 60;
  }

  // Tip API: setStatus, setMax, setProgress, hide
  function tip_set_status(status) {
    if (!tip) return;
    if (tipStatus) tipStatus.textContent = status;
    tip.classList.add('show');
  }

  function tip_set_max(n) {
    if (!tip || !tipProgress) return;
    tipMax = Number(n) || 0;
    tipProgress.hidden = false;
    tipProgress.setAttribute('aria-hidden', 'false');
    if (tipProgressBar) {
      try { tipProgressBar.max = tipMax; tipProgressBar.value = 0; } catch(e) {}
      tipProgressBar.setAttribute('aria-valuemin', '0');
      tipProgressBar.setAttribute('aria-valuemax', String(tipMax));
      tipProgressBar.setAttribute('aria-valuenow', '0');
      tipProgressBar.classList.remove('indeterminate');
    }
    tip.classList.add('show');
  }

  function tip_set_progress(p) {
    if (!tip || !tipProgress) return;
    const val = Number(p) || 0;
    if (tipMax && tipMax > 0) {
      if (tipProgressBar) {
        try { tipProgressBar.value = val; } catch(e) {}
        tipProgressBar.setAttribute('aria-valuenow', String(val));
        tipProgressBar.classList.remove('indeterminate');
      }
      if (tipProgressLabel) tipProgressLabel.textContent = `${val}/${tipMax}`;
    } else {
      // indeterminate mode: remove value to trigger indeterminate appearance and animate
      if (tipProgressBar) {
        try { tipProgressBar.removeAttribute('value'); } catch(e) {}
        tipProgressBar.classList.add('indeterminate');
      }
      if (tipProgressLabel) tipProgressLabel.textContent = `${val}`;
    }
    tip.classList.add('show');
  }

  function tip_hide() {
    if (!tip) return;
    tip.classList.remove('show');
    if (tipProgress) {
      tipProgress.hidden = true;
      tipProgress.setAttribute('aria-hidden', 'true');
      if (tipProgressBar) {
        try { tipProgressBar.value = 0; } catch(e) {}
        tipProgressBar.classList.remove('indeterminate');
        tipProgressBar.setAttribute('aria-valuenow', '0');
        tipProgressBar.setAttribute('aria-valuemax', '0');
      }
      if (tipProgressLabel) tipProgressLabel.textContent = '0/0';
      tipMax = 0;
    }
  }

  if (tipClose && tip) {
    tipClose.addEventListener('click', () => tip_hide());
  }

  // 讓 Python 端可以直接呼叫這些函式（eel）
  if (typeof eel !== 'undefined' && eel.expose) {
    try {
      eel.expose(tip_set_status);
      eel.expose(tip_set_max);
      eel.expose(tip_set_progress);
      eel.expose(tip_hide);
    } catch (e) {
      // ignore; older eel 版本可能行為不同
      console.debug('eel.expose for tip API failed', e);
    }
  }

  // Tip 測試序列：可從按鈕、console 或 Python (eel) 呼叫
  function tip_test_sequence({ status='測試中...', total=100, step=8, interval=220 } = {}) {
    return new Promise(resolve => {
      tip_set_status(status);
      if (total && total > 0) tip_set_max(total);

      let current = 0;
      const timer = setInterval(() => {
        current = Math.min(total || current + step, total || current + step);
        tip_set_progress(current);
        if (total && current >= total) {
          clearInterval(timer);
          tip_set_status('完成');
          setTimeout(() => { tip_hide(); resolve(true); }, 300000);
        }
      }, interval);

      // 如果是 indeterminate（沒傳 total），設定一個安全停止點
      if (!total || total <= 0) {
        setTimeout(() => {
          clearInterval(timer);
          tip_set_status('完成（indeterminate 模式）');
          setTimeout(() => { tip_hide(); resolve(true); }, 300000);
        }, Math.max(4000, interval * 20));
      }
    });
  }

  // 綁定頁面上的測試按鈕
  const demoProgressBtn = $('demoProgressBtn');
  if (demoProgressBtn) {
    demoProgressBtn.addEventListener('click', () => {
      tip_test_sequence({ status: '開始安裝（測試）...', total: 100, step: 10, interval: 180 });
    });
  }

  // 暴露給 console 與 Python (eel)
  window.tip_test_sequence = tip_test_sequence;
  if (typeof eel !== 'undefined' && eel.expose) {
    try { eel.expose(tip_test_sequence); } catch (e) { console.debug('Cannot expose tip_test_sequence to eel', e); }
  }

  /* 帳戶面板顯示/隱藏：改為使用 classList，以觸發 CSS 動畫 */
  const accountBtn = $('accountBtn');
  const accountPanel = $('accountPanel');
  const mainbtn = $('account-txt');
  
  // 保存原始的 account-txt 內容
  const originalAccountTxt = mainbtn ? mainbtn.innerHTML : '';
  
  if (accountBtn && accountPanel) {
    accountBtn.addEventListener('click', () => {
      const isOpen = accountPanel.classList.toggle('show');
      if (isOpen) {
        // accountPanel 打開時
        populateAccounts();
        // 改為返回
        if (mainbtn) {
          mainbtn.innerHTML = `
            <div style="font-weight:700">返回</div>
            <div style="font-size:12px;color:#666"></div>
          `;
        }
      } else {
        // accountPanel 關閉時，恢復原始內容
        if (mainbtn) {
          mainbtn.innerHTML = originalAccountTxt;
        }
      }
    });
  }

  function populateAccounts() {
    const container = $('accountsList');
    if (!container) return;
    container.innerHTML = '';
    
    // eel.account_get 返回 Promise，需要用 callback 或 async/await 處理
    eel.account_get("list")(function(users) {
      console.log('收到的原始資料：', users);
      
      // 如果返回空物件或 null，顯示提示
      if (!users || Object.keys(users).length === 0) {
        container.innerHTML = '<div style="padding:12px;color:#999">沒有帳號</div>';
        return;
      }

      

      // users 現在是一個字典，鍵是帳號名，值是帳號資訊物件
      // 直接遍歷字典的值
      Object.values(users).forEach((u, index) => {
        console.log(`第 ${index} 個帳號：`, u);
        const div = document.createElement('div');
        eel.skin_face_get(u.skin.path)(function(skinDataUrl) {
          const img = div.querySelector('img');
          if (img) img.src = skinDataUrl;
        });
        div.className = 'entry';
        div.innerHTML = `
          <img alt="" src="" style="background:#ddd"/>
          <div style="flex:1">
            <div style="font-weight:700">${u.user_name || '未知帳號'}</div>
            <div style="font-size:12px;color:#888">${u.account_type || '未知類型'} 帳戶</div>
          </div>
          <div style="display:flex;gap:6px">
            <button class="controlBtn" onclick="alert('刷新 ${u.user_name}')">🔄</button>
            <button class="controlBtn" onclick="alert('個人資料 ${u.user_name}')">👤</button>
            <button class="controlBtn" onclick="if(confirm('刪除 ${u.user_name}?')){ this.closest('.entry').remove(); }">🗑️</button>
          </div>
        `;
        container.appendChild(div);
      });
    });
  }

  /* settings 按鈕改為開啟 panel（同上） */
  const settingsBtn = $('settingsBtn');
  if (settingsBtn && accountPanel) {
    settingsBtn.addEventListener('click', () => {
      accountPanel.classList.add('show');
      const list = $('accountsList');
      if (list) list.innerHTML = `
      <div style="padding:12px;color:#666">
        <button class="menu-btn" style="text-align: center;" onclick="window.open('./setting.html', '_blank', 'width=700,height=800')">⚙️ 更改設定</button><br/><br/>
        <button class="menu-btn" style="text-align: center;" onclick="showUpdatePanel('日誌', {url: 'http://localhost:1936/logs/'})">📄 查看日誌</button><br/><br/>
        <button class="menu-btn" style="text-align: center;" onclick="showMsg('測試 Msgbox', '這是一個全局的訊息框測試')">🧪 測試 Msgbox</button><br/><br/>
        <button class="menu-btn" style="text-align: center;" onclick="aboutAPP()">ℹ️ 關於 UMCL</button>
      </div>`;
      // 改為返回
      if (mainbtn) {
        mainbtn.innerHTML = `
          <div style="font-weight:700">返回</div>
          <div style="font-size:12px;color:#666"></div>
        `;
      }
    });
  }

  async function openFilePicker() {
    try {
        const [fileHandle] = await window.showOpenFilePicker();
        const file = await fileHandle.getFile();
        console.log(file); // 獲取 File 物件
    } catch (err) {
        console.error("User canceled the file picker or an error occurred", err);
    }
}


  /* 其餘互動不變 */
  if ($('pickSkin')) $('pickSkin').addEventListener('click', () => {
    openFilePicker();
  });
  if ($('previewSkin')) $('previewSkin').addEventListener('click', () => {
    window.open('./plugin/mc-skinviewer/index.html', '_blank');
  });
  
  // modal 相關的事件聆聽器已移至 account.html 和 account-modal.js
  // createAcct, modalClose, openCreateAccount 等已廢棄

  // launchBtn 行為保持不變
  const launchBtn = $('launchBtn');
  if (launchBtn) {
    launchBtn.addEventListener('click', () => {
      terminalBack.classList.add('show');
      eel.launch_game()(function(response) {
        alert(response);
      });
    });
  }

  const versionSelect = document.getElementById('versionSelect');
  eel.get_local_ver()(function(ver) {
    console.log(ver);
    versionSelect.innerHTML = '';
    ver.forEach(v => {
      const option = document.createElement('option');
      option.innerHTML = v;
      versionSelect.appendChild(option);
    });
  });
  versionSelect.addEventListener('change', function(e) {
    const selectedVersion = e.target.value;
    console.log('選擇的版本：', selectedVersion);
    eel.load_versionSelect(selectedVersion);
  });

  const terminalClose = document.getElementById('terminalClose');
  const terminalBack = document.getElementById('terminal');
  
  // 綁定 terminal 關閉按鈕
  if (terminalClose) {
    terminalClose.addEventListener('click', closeTerminal);
  }

  // 若需程式載入時就自動顯示 msgbox，可在此呼叫：
  // showMsg('歡迎', '啟動完成').then(...);
});