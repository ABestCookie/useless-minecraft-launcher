/**
 * msgbox.js - 獨立的消息框組件
 * 提供全局 showMsg 函數，支援自訂標題和內容
 */

/* ===== 全局 msgbox 變數 ===== */
let msgboxBack = null;
let msgboxOk = null;
let msgboxCancel = null;
let msgboxTitle = null;
let msgboxMsg = null;
let aa12 = null;

/**
 * 初始化 msgbox HTML 元素（動態創建）
 */
function initMsgboxHTML() {
  if (msgboxBack) return; // 已初始化過

  // 創建外層容器
  msgboxBack = document.createElement('div');
  msgboxBack.className = 'modal-back msgbox-back';
  msgboxBack.id = 'msgboxBack';
  msgboxBack.setAttribute('aria-hidden', 'true');
  
  // 創建 modal 本體
  const modal = document.createElement('div');
  modal.className = 'modal msgbox-modal';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'msgboxTitle');
  
  // 標題
  msgboxTitle = document.createElement('h3');
  msgboxTitle.id = 'msgboxTitle';
  msgboxTitle.textContent = '提示';
  
  // 內容
  msgboxMsg = document.createElement('div');
  msgboxMsg.id = 'msgboxMsg';
  msgboxMsg.style.cssText = 'margin: 4px 0; padding: 0px; white-space: pre-wrap; line-height: 1.2;';
  msgboxMsg.textContent = '訊息內容';
  
  // 按鈕容器
  aa12 = document.createElement('div');
  aa12.id = 'aa12';
  aa12.style.cssText = 'display:flex;gap:8px;justify-content:flex-end;margin-top:12px';
  
  // 按鈕：取消
  msgboxCancel = document.createElement('button');
  msgboxCancel.id = 'msgboxCancel';
  msgboxCancel.type = 'button';
  msgboxCancel.textContent = '取消';
  
  // 按鈕：確定
  msgboxOk = document.createElement('button');
  msgboxOk.id = 'msgboxOk';
  msgboxOk.type = 'button';
  msgboxOk.textContent = '確定';
  
  // 組合
  aa12.appendChild(msgboxCancel);
  aa12.appendChild(msgboxOk);
  
  modal.appendChild(msgboxTitle);
  modal.appendChild(msgboxMsg);
  modal.appendChild(aa12);
  
  msgboxBack.appendChild(modal);
  
  // 加入 DOM
  document.body.appendChild(msgboxBack);
}

/**
 * 顯示消息框
 * @param {string} title - 標題
 * @param {string} message - 訊息內容（支援 HTML）
 * @returns {Promise<'ok'|'cancel'>} 返回按鈕結果
 */
function showMsg(title, message) {
  // 確保 HTML 已初始化
  if (!msgboxBack) {
    initMsgboxHTML();
  }
  
  if (!msgboxBack) return Promise.resolve(null);

  // 設定內容（使用 innerHTML 以支持 HTML 內容）
  msgboxTitle.innerHTML = title;
  msgboxMsg.innerHTML = message;

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
      // 等待動畫結束
      setTimeout(() => resolve(result), 180);
    };
    
    const onOk = () => clean('ok');
    const onCancel = () => clean('cancel');

    msgboxOk.addEventListener('click', onOk);
    msgboxCancel.addEventListener('click', onCancel);

    // 可按 Esc 關閉
    const onKey = (e) => {
      if (e.key === 'Escape') { 
        onCancel();
        document.removeEventListener('keydown', onKey);
      }
    };
    document.addEventListener('keydown', onKey, { once: true });
  });
}

// 暴露給 eel（Python 可直接呼叫）
if (typeof eel !== 'undefined' && eel.expose) {
  try {
    eel.expose(showMsg);
  } catch (e) {
    console.debug('eel.expose for showMsg failed', e);
  }
}

// 暴露給全局作用域
window.showMsg = showMsg;
