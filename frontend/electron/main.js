const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 400,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadURL("http://localhost:5173");

  // CRITICAL: Don't ignore mouse events!
  mainWindow.setIgnoreMouseEvents(false);
}

ipcMain.on("resize-window", (event, width, height) => {
  if (mainWindow) {
    const newWidth = Math.round(width);
    const newHeight = Math.round(height);
    mainWindow.setSize(newWidth, newHeight);
  }
});

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
