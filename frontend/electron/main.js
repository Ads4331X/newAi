let { PythonShell } = require("python-shell");
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

app.commandLine.appendSwitch("enable-features", "OnDeviceWebSpeech");
app.commandLine.appendSwitch("log-level", "3");
let mainWindow;

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

ipcMain.on("resize-window", (event, width, height) => {
  if (mainWindow) {
    const newWidth = Math.round(width);
    const newHeight = Math.round(height);
    mainWindow.setSize(newWidth, newHeight);
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
  });

  pyshell.on("error", (err) => {
    console.error("Python error:", err);
  });

  // Handle input from renderer
  ipcMain.on("prompt-to-py", (event, user_prompt) => {
    pyshell.send(user_prompt);
  });
});

app.commandLine.appendSwitch("enable-features", "OnDeviceWebSpeech");

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
