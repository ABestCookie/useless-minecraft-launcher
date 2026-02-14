/**
 * account-modal.js - 帳戶建立彈出視窗
 * 綁定到 account.html 的 offlineLoginBtn
 */

/* ===== 全局 account-modal 變數 ===== */
let lastFocusedElement = null;
let accountModalBack = null;
let accountModalClose = null;
let selectedSkinFile = null; // 存儲選中的皮膚文件

/**
 * 初始化 account-modal HTML 元素（動態創建）
 */
function initAccountModalHTML() {
  if (accountModalBack) return; // 已初始化過

  // 創建外層容器
  accountModalBack = document.createElement('div');
  accountModalBack.className = 'modal-back';
  accountModalBack.id = 'modalBack';
  accountModalBack.setAttribute('aria-hidden', 'true');
  
  // 創建 modal 本體
  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'modalTitle');
  modal.setAttribute('aria-describedby', 'modalBody');
  
  // 關閉按鈕
  accountModalClose = document.createElement('button');
  accountModalClose.className = 'close-x';
  accountModalClose.id = 'modalClose';
  accountModalClose.type = 'button';
  accountModalClose.title = '關閉';
  accountModalClose.textContent = '✕';
  
  // 標題
  const modalTitle = document.createElement('h3');
  modalTitle.id = 'modalTitle';
  modalTitle.textContent = '新增帳戶';
  
  // 內容區域
  const modalBody = document.createElement('div');
  modalBody.id = 'modalBody';
  
  // 帳戶名稱輸入
  const acctNameInput = document.createElement('input');
  acctNameInput.id = 'acctName';
  acctNameInput.className = 'acctNameInput';
  acctNameInput.type = 'text';
  acctNameInput.placeholder = '帳戶名稱';
  
  // skin 選項容器
  const skinDiv = document.createElement('div');
  skinDiv.id = 'skinDiv';
  skinDiv.style.cssText = 'margin-top:10px;display:flex;gap:8px;flex-direction:column';
  
  // 顯示已選皮膚的標籤
  const skinStatusLabel = document.createElement('label');
  skinStatusLabel.id = 'skinStatusLabel';
  skinStatusLabel.style.cssText = 'font-size:12px;color:#aaa;text-align:left';
  skinStatusLabel.textContent = '皮膚：未選擇（選填）';
  
  const skinBtnContainer = document.createElement('div');
  skinBtnContainer.style.cssText = 'display:flex;gap:8px';
  
  const pickSkinBtn = document.createElement('input');
  pickSkinBtn.id = 'pickSkin';
  pickSkinBtn.className = 'pickSkinBtn';
  pickSkinBtn.type = 'button';
  pickSkinBtn.value = '選取皮膚';
  
  const previewSkinBtn = document.createElement('button');
  previewSkinBtn.id = 'previewSkin';
  previewSkinBtn.className = 'previewSkinBtn';
  previewSkinBtn.type = 'button';
  previewSkinBtn.textContent = '預覽';
  
  skinBtnContainer.appendChild(pickSkinBtn);
  skinBtnContainer.appendChild(previewSkinBtn);
  
  skinDiv.appendChild(skinStatusLabel);
  skinDiv.appendChild(skinBtnContainer);
  
  // 建立按鈕容器
  const createDiv = document.createElement('div');
  createDiv.style.cssText = 'margin-top:18px';
  
  const createAcctBtn = document.createElement('button');
  createAcctBtn.id = 'createAcct';
  createAcctBtn.className = 'createAcctBtn';
  createAcctBtn.type = 'button';
  createAcctBtn.textContent = '新增';
  
  createDiv.appendChild(createAcctBtn);
  
  // 組合 modalBody
  modalBody.appendChild(acctNameInput);
  modalBody.appendChild(skinDiv);
  modalBody.appendChild(createDiv);
  
  // 組合 modal
  modal.appendChild(accountModalClose);
  modal.appendChild(modalTitle);
  modal.appendChild(modalBody);
  
  // 組合外層
  accountModalBack.appendChild(modal);
  
  // 加入 DOM
  document.body.appendChild(accountModalBack);
}

/**
 * 打開帳戶建立彈出視窗
 */
function openModal() {
  if (!accountModalBack) {
    initAccountModalHTML();
  }
  
  if (!accountModalBack) return;

  // 記住先前有焦點的元素（可能為 null）
  lastFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;

  // 顯示 modal（觸發 CSS enter 動畫）
  accountModalBack.classList.add('show');
  accountModalBack.setAttribute('aria-hidden', 'false');

  // focus 管理：把焦點放到第一個可輸入元素或關閉按鈕
  const firstFocusable = accountModalBack.querySelector('input, button, [tabindex]');
  if (firstFocusable && typeof firstFocusable.focus === 'function') firstFocusable.focus();

  // 加入 ESC 監聽器
  document.addEventListener('keydown', onEscClose);
}

/**
 * 關閉帳戶建立彈出視窗
 */
function closeModal() {
  if (!accountModalBack) return;

  // 先移除 show 以啟動 exit 動畫
  accountModalBack.classList.remove('show');

  // 如果目前焦點仍在 modal 內，嘗試移出焦點
  const active = document.activeElement;
  if (active && accountModalBack.contains(active)) {
    try {
      active.blur();
    } catch (e) { /* ignore */ }
  }

  // 嘗試把焦點還原到開啟前的元素；若沒有則聚焦到帳戶按鈕或其他備用
  try {
    if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
      lastFocusedElement.focus();
    } else {
      // fallback：嘗試把焦點交給 offlineLoginBtn 或其他按鈕
      const fallback = document.getElementById('offlineLoginBtn') || document.querySelector('button');
      if (fallback && typeof fallback.focus === 'function') fallback.focus();
    }
  } catch (e) {
    // ignore focus errors
  }

  // 在確保焦點已移出 modal 後，才把 aria-hidden 設回 true
  accountModalBack.setAttribute('aria-hidden', 'true');

  // 移除 ESC 監聽器
  document.removeEventListener('keydown', onEscClose);

  // 清除記錄
  lastFocusedElement = null;
  
  // 取消 modal 時清空皮膚選擇
  selectedSkinFile = null;
}

/**
 * ESC 鍵關閉 handler
 */
function onEscClose(e) {
  if (e.key === 'Escape') closeModal();
}

/**
 * 初始化事件綁定
 */
function initAccountModalEvents() {
  if (!accountModalBack) {
    initAccountModalHTML();
  }

  if (accountModalClose) {
    accountModalClose.addEventListener('click', closeModal);
  }

  if (accountModalBack) {
    accountModalBack.addEventListener('click', (e) => {
      if (e.target === accountModalBack) closeModal();
    });
  }
}

// 暴露給全局作用域
window.openModal = openModal;
window.closeModal = closeModal;
window.initAccountModalEvents = initAccountModalEvents;
