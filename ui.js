/* filepath: c:\Users\tsai cookie\Desktop\useless minecraft launcher\ui.js */
/**
 * 控制啟動時是否自動顯示 TIP
 * 設為 true 則頁面載入時自動彈出 tip，設為 false 則不自動顯示
 */
const AUTO_SHOW_TIP = true;

document.addEventListener('DOMContentLoaded', () => {
  const $ = id => document.getElementById(id);

  // 追蹤開啟 modal 前的焦點，用來在關閉時還原
  let lastFocusedElement = null;

  // 取得 modal 相關節點
  const openModalBtn = $('openModalBtn');
  const modalBack = $('modalBack');
  const modalClose = $('modalClose');

  // ESC handler 名義（會在 open 時加入，close 時移除）
  function onEscClose(e) {
    if (e.key === 'Escape') closeModal();
  }

  // 開啟 modal：記錄先前焦點、加上 .show、更新 aria 並將焦點移到第一個輸入
  function openModal() {
    if (!modalBack) return;

    // 記住先前有焦點的元素（可能為 null）
    lastFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;

    // 顯示 modal（觸發 CSS enter 動畫）
    modalBack.classList.add('show');
    modalBack.setAttribute('aria-hidden', 'false');

    // focus 管理：把焦點放到第一個可輸入元素或關閉按鈕
    const firstFocusable = modalBack.querySelector('input, button, [tabindex]');
    if (firstFocusable && typeof firstFocusable.focus === 'function') firstFocusable.focus();

    // 加入 ESC 監聽器
    document.addEventListener('keydown', onEscClose);
  }

  // 關閉 modal：移除 .show，先還原焦點再設定 aria-hidden（避免 aria-hidden 在有焦點時被套用）
  function closeModal() {
    if (!modalBack) return;

    // 先移除 show 以啟動 exit 動畫
    modalBack.classList.remove('show');

    // 如果目前焦點仍在 modal 內，嘗試移出焦點：先 blur，然後 restore 到先前元素或 fallback
    const active = document.activeElement;
    if (active && modalBack.contains(active)) {
      try {
        (active).blur();
      } catch (e) { /* ignore */ }
    }

    // 嘗試把焦點還原到開啟前的元素；若沒有則聚焦到開啟 modal 的按鈕或帳戶按鈕
    try {
      if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
        lastFocusedElement.focus();
      } else {
        const fallback = openModalBtn || $('accountBtn') || $('sidebarToggle');
        if (fallback && typeof fallback.focus === 'function') fallback.focus();
      }
    } catch (e) {
      // ignore focus errors
    }

    // 在確保焦點已移出 modal 後，才把 aria-hidden 設回 true（避免 assistive tech 被隱藏時仍有 descendant 保持 focus）
    modalBack.setAttribute('aria-hidden', 'true');

    // 移除 ESC 監聽器
    document.removeEventListener('keydown', onEscClose);

    // 清除記錄（非必要）
    lastFocusedElement = null;
  }

  // 綁定按鈕與遮罩點擊（點遮罩空白處關閉）
  if (openModalBtn) openModalBtn.addEventListener('click', openModal);
  if (modalClose) modalClose.addEventListener('click', closeModal);
  if (modalBack) {
    modalBack.addEventListener('click', (e) => {
      if (e.target === modalBack) closeModal();
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
  if (tipClose && tip) {
    tipClose.addEventListener('click', () => tip.classList.remove('show'));
  }

  // 依 AUTO_SHOW_TIP 決定是否在載入時顯示 tip（短延遲以確保 transition 正確觸發）
  if (tip && AUTO_SHOW_TIP) {
    // 若想立即無延遲顯示可移除 setTimeout
    setTimeout(() => tip.classList.add('show'), 60);
  }

  /* 帳戶面板顯示/隱藏：改為使用 classList，以觸發 CSS 動畫 */
  const accountBtn = $('accountBtn');
  const accountPanel = $('accountPanel');
  if (accountBtn && accountPanel) {
    accountBtn.addEventListener('click', () => {
      const isOpen = accountPanel.classList.toggle('show');
      if (isOpen) populateAccounts();
    });
  }

  function populateAccounts() {
    const container = $('accountsList');
    if (!container) return;
    container.innerHTML = '';
    const users = [
      { name: 'WafflyBat', type: 'Microsoft' },
      { name: 'PlayerOne', type: 'offline' },
      { name: 'Guest', type: 'offline' }
    ];

    users.forEach(u => {
      const div = document.createElement('div');
      div.className = 'entry';
      div.innerHTML = `
        <img alt="" src="" style="background:#ddd"/>
        <div style="flex:1">
          <div style="font-weight:700">${u.name}</div>
          <div style="font-size:12px;color:#888">${u.type} 帳戶</div>
        </div>
        <div style="display:flex;gap:6px">
          <button class="controlBtn" onclick="alert('刷新 ${u.name}')">🔄</button>
          <button class="controlBtn" onclick="alert('個人資料 ${u.name}')">👤</button>
          <button class="controlBtn" onclick="if(confirm('刪除 ${u.name}?')){ this.closest('.entry').remove(); }">🗑️</button>
        </div>
      `;
      container.appendChild(div);
    });
  }

  /* settings 按鈕改為開啟 panel（同上） */
  const settingsBtn = $('settingsBtn');
  if (settingsBtn && accountPanel) {
    settingsBtn.addEventListener('click', () => {
      accountPanel.classList.add('show');
      const list = $('accountsList');
      if (list) list.innerHTML = '<div style="padding:12px;color:#666">設定內容（模擬）</div>';
    });
  }

  /* 其餘互動不變 */
  if ($('pickSkin')) $('pickSkin').addEventListener('click', () => alert('開啟檔案對話框（模擬）'));
  if ($('previewSkin')) $('previewSkin').addEventListener('click', () => alert('啟動 skinviewer（模擬）'));
  if ($('createAcct')) {
    $('createAcct').addEventListener('click', () => {
      const name = $('acctName').value.trim();
      if (!name) { alert('帳戶名稱不能為空'); return; }
      alert('新增帳戶：' + name + '（模擬）');
      // 使用 closeModal() 取代直接操作 style.display，保持行為一致
      closeModal();
    });
  }
  // 用 closeModal 替代直接修改 style（確保 focus/aria 正確處理）
  if ($('modalClose')) $('modalClose').addEventListener('click', () => { closeModal(); });

  // openCreateAccount 也改用 openModal()
  window.openCreateAccount = () => {
    openModal();
    if ($('acctName')) $('acctName').value = '';
  };

  // launchBtn 行為保持不變
  const launchBtn = $('launchBtn');
  if (launchBtn) {
    launchBtn.addEventListener('click', () => {
      alert('啟動遊戲（模擬）');
    });
  }

  // 新增：msgbox 行為（tkinter.msgbox 類似）
  const showMsgBtn = $('showMsgBtn');
  const msgboxBack = $('msgboxBack');
  const msgboxOk = $('msgboxOk');
  const msgboxCancel = $('msgboxCancel');
  const msgboxTitle = document.getElementById('msgboxTitle');
  const msgboxMsg = document.getElementById('msgboxMsg');

  // 顯示訊息框：可傳入 title 與 message
  function showMsg(title = '提示', message = '', options = {}) {
    if (!msgboxBack) return Promise.resolve(null);

    // 設定內容
    msgboxTitle.textContent = title;
    msgboxMsg.textContent = message;

    // 顯示
    msgboxBack.classList.add('show');
    msgboxBack.setAttribute('aria-hidden', 'false');

    // 回傳一個 Promise，resolve 為按鈕結果 ('ok'|'cancel')
    return new Promise(resolve => {
      const clean = (result) => {
        msgboxBack.classList.remove('show');
        msgboxBack.setAttribute('aria-hidden', 'true');
        // 移除事件聆聽器
        msgboxOk.removeEventListener('click', onOk);
        msgboxCancel.removeEventListener('click', onCancel);
        // small delay 以等待動畫結束（非必要）
        setTimeout(() => resolve(result), 180);
      };
      const onOk = () => clean('ok');
      const onCancel = () => clean('cancel');

      msgboxOk.addEventListener('click', onOk);
      msgboxCancel.addEventListener('click', onCancel);

      // 可按 Esc 關閉
      const onKey = (e) => {
        if (e.key === 'Escape') { onCancel(); document.removeEventListener('keydown', onKey); }
      };
      document.addEventListener('keydown', onKey, { once: true });
    });
  }

  // 連接按鈕（panel 內的按鈕）
  if (showMsgBtn) {
    showMsgBtn.addEventListener('click', () => {
      showMsg('訊息', '這是一個模擬的訊息框（tkinter.msgbox 風格）').then(result => {
        // 簡單示範處理結果
        if (result === 'ok') alert('你按了 確定');
        else alert('你按了 取消');
      });
    });
  }

  // 若需程式載入時就自動顯示 msgbox，可在此呼叫：
  // showMsg('歡迎', '啟動完成').then(...);
});