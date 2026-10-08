'use strict';
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('couponApi', {
  getQuote: (code, subtotal) => ipcRenderer.invoke('coupon:quote', code, subtotal),
  getDebug: () => ipcRenderer.invoke('coupon:debug'),
});
