'use strict';
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { quote, debugSnapshot } = require('./lib/pricing');

let w;

function _mk() {
  w = new BrowserWindow({
    width: 480,
    height: 360,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  w.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

ipcMain.handle('coupon:quote', (_evt, code, subtotal) => {
  return quote(String(code || ''), Number(subtotal) || 0);
});

ipcMain.handle('coupon:debug', () => {
  return debugSnapshot(process.env);
});

app.whenReady().then(_mk);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
