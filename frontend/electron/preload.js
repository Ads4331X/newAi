const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  resizeWindow: (width, height) =>
    ipcRenderer.send("resize-window", width, height),
  getPrompt: (user_prompt) => ipcRenderer.send("prompt-to-py", user_prompt),
});

contextBridge.exposeInMainWorld("electron", {
  ipcRenderer: {
    on: (channel, func) => {
      ipcRenderer.on(channel, (event, ...args) => func(event, ...args));
    },
  },
});
