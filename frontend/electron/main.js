let { PythonShell } = require("python-shell");
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");

app.commandLine.appendSwitch("enable-features", "OnDeviceWebSpeech");
app.commandLine.appendSwitch("log-level", "3");

let mainWindow;
let responseWindow;
const preloadPath = path.resolve(__dirname, "preload.js");

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
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.loadURL("http://localhost:5173");
  mainWindow.setIgnoreMouseEvents(false);
}

function createResponseWindow() {
  if (responseWindow && !responseWindow.isDestroyed()) return;
  responseWindow = new BrowserWindow({
    width: 450,
    height: 300,
    frame: true,
    autoHideMenuBar: true,
    alwaysOnTop: true,
    skipTaskbar: false,
    resizable: true,
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  responseWindow.loadURL("http://localhost:5173/#response");

  responseWindow.webContents.on("did-finish-load", () => {
    const historyPath = path.join(
      __dirname,
      "../../backend/data/conversation_history.json",
    );
    try {
      const history = JSON.parse(fs.readFileSync(historyPath, "utf8"));
      responseWindow.webContents.send("load-history", history);
    } catch (e) {}
  });
}

ipcMain.on("resize-window", (event, width, height) => {
  if (mainWindow) {
    mainWindow.setSize(Math.round(width), Math.round(height));
  }
});

ipcMain.on("close-response", () => {
  if (responseWindow && !responseWindow.isDestroyed()) {
    responseWindow.close();
    responseWindow = null;
  }
});

app.whenReady().then(() => {
  createWindow();

  let options = {
    mode: "text",
    pythonPath: "/home/erza/git_projects/newAi/.venv_tts/bin/python",
    pythonOptions: ["-u"],
    scriptPath: path.join(__dirname, "../../backend"),
    env: Object.assign({}, process.env, {
      DISPLAY: process.env.DISPLAY || ":1",
      DBUS_SESSION_BUS_ADDRESS:
        process.env.DBUS_SESSION_BUS_ADDRESS || "unix:path=/run/user/1000/bus",
      XDG_RUNTIME_DIR: process.env.XDG_RUNTIME_DIR || "/run/user/1000",
    }),
  };

  let pyshell = new PythonShell("main.py", options);
  pyshell.on("message", (message) => {
    console.log("FROM PYTHON:", message);
    mainWindow.webContents.send("python-response", message);

    if (
      !message.startsWith("STT:") &&
      !message.startsWith("MEMORY") &&
      !message.startsWith("BASH OUTPUT") &&
      !message.startsWith("EXECUTING:")
    ) {
      if (responseWindow && !responseWindow.isDestroyed()) {
        responseWindow.webContents.send("python-response", message);
      }
    }
  });

  pyshell.on("error", (err) => {
    console.error("Python error:", err);
  });

  ipcMain.on("user-message-to-response", (event, text) => {
    createResponseWindow();
    setTimeout(() => {
      if (responseWindow && !responseWindow.isDestroyed()) {
        responseWindow.webContents.send("user-message", text);
      }
    }, 600);
  });

  ipcMain.on("prompt-to-py", (event, user_prompt) => {
    createResponseWindow();
    setTimeout(() => {
      if (responseWindow && !responseWindow.isDestroyed()) {
        responseWindow.webContents.send("user-message", user_prompt);
      }
    }, 600);
    pyshell.send(user_prompt);
  });
});

app.commandLine.appendSwitch("enable-features", "OnDeviceWebSpeech");

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
