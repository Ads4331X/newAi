let { PythonShell } = require("python-shell");
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");

app.commandLine.appendSwitch("enable-features", "OnDeviceWebSpeech");
app.commandLine.appendSwitch("log-level", "3");

let mainWindow;
let responseWindow;
let pyshell;
let responseReady = false;
const pendingResponseEvents = [];
const preloadPath = path.resolve(__dirname, "preload.js");
const preferredRendererUrl = process.env.FRONTEND_URL || "http://localhost:5173";
let activeRendererUrl = preferredRendererUrl;
const historyPath = path.join(
  __dirname,
  "../../backend/data/conversation_history.json",
);

function getRendererCandidates() {
  const candidates = [preferredRendererUrl];
  for (let port = 5173; port <= 5183; port += 1) {
    candidates.push(`http://localhost:${port}`);
  }
  return [...new Set(candidates)];
}

function loadWindowWithFallback(win, hash = "") {
  const candidates = getRendererCandidates();
  const wc = win.webContents;
  let index = 0;
  let loaded = false;

  const tryLoad = () => {
    if (!win || win.isDestroyed() || loaded) return;
    const url = `${candidates[index % candidates.length]}${hash}`;
    index += 1;
    win.loadURL(url).catch(() => {
      setTimeout(tryLoad, 300);
    });
  };

  const onFailLoad = () => {
    if (loaded) return;
    setTimeout(tryLoad, 300);
  };

  const onDidFinishLoad = () => {
    if (win.isDestroyed()) return;
    loaded = true;
    activeRendererUrl = wc.getURL().split("#")[0];
    wc.removeListener("did-fail-load", onFailLoad);
  };

  wc.on("did-fail-load", onFailLoad);
  wc.on("did-finish-load", onDidFinishLoad);
  win.on("closed", () => {
    loaded = true;
  });

  tryLoad();
}

function loadHistory() {
  try {
    return JSON.parse(fs.readFileSync(historyPath, "utf8"));
  } catch (e) {
    return [];
  }
}

function sendToResponse(channel, data) {
  if (!responseWindow || responseWindow.isDestroyed()) return;

  if (!responseReady) {
    pendingResponseEvents.push({ channel, data });
    return;
  }

  responseWindow.webContents.send(channel, data);
}

function flushResponseEvents() {
  if (!responseWindow || responseWindow.isDestroyed() || !responseReady) return;
  while (pendingResponseEvents.length > 0) {
    const event = pendingResponseEvents.shift();
    responseWindow.webContents.send(event.channel, event.data);
  }
}

function sendToMain(channel, data) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(channel, data);
  }
}

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
  loadWindowWithFallback(mainWindow);
  mainWindow.setIgnoreMouseEvents(false);
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function createResponseWindow() {
  if (responseWindow && !responseWindow.isDestroyed()) return;
  responseReady = false;
  responseWindow = new BrowserWindow({
    width: 450,
    height: 500,
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
  loadWindowWithFallback(responseWindow, "#response");
  responseWindow.webContents.on("did-finish-load", () => {
    responseReady = true;
    flushResponseEvents();
    // Keep both windows aligned after whichever Vite port wins.
    if (mainWindow && !mainWindow.isDestroyed()) {
      const currentMainUrl = mainWindow.webContents.getURL().split("#")[0];
      if (currentMainUrl !== activeRendererUrl) {
        mainWindow.loadURL(activeRendererUrl);
      }
    }
    sendToResponse("load-history", loadHistory());
  });
  responseWindow.on("focus", () => {
    sendToResponse("load-history", loadHistory());
  });
  responseWindow.on("closed", () => {
    responseReady = false;
    pendingResponseEvents.length = 0;
    responseWindow = null;
  });
}

ipcMain.on("resize-window", (event, width, height) => {
  if (mainWindow) mainWindow.setSize(Math.round(width), Math.round(height));
});

ipcMain.on("close-response", () => {
  if (responseWindow && !responseWindow.isDestroyed()) {
    responseWindow.close();
    responseWindow = null;
  }
});

ipcMain.on("stop-speaking", () => {
  if (pyshell) pyshell.send("STOP_SPEAKING");
});

app.whenReady().then(() => {
  createWindow();
  createResponseWindow();

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

  pyshell = new PythonShell("main.py", options);
  pyshell.on("message", (message) => {
    console.log("FROM PYTHON:", message);
    sendToMain("python-response", message);

    if (
      !message.startsWith("STT:") &&
      !message.startsWith("MEMORY") &&
      !message.startsWith("BASH OUTPUT") &&
      !message.startsWith("EXECUTING:")
    ) {
      sendToResponse("python-response", message);
    }
  });

  pyshell.on("error", (err) => console.error("Python error:", err));

  ipcMain.on("user-message-to-response", (event, text) => {
    sendToResponse("user-message", text);
  });

  ipcMain.on("prompt-to-py", (event, user_prompt) => {
    if (pyshell) pyshell.send(user_prompt);
  });
});

app.on("before-quit", () => {
  if (pyshell) {
    try {
      pyshell.terminate();
    } catch (err) {
      console.error("Python terminate error:", err);
    }
    pyshell = null;
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
