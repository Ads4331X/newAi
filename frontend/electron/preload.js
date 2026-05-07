const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  resizeWindow: (width, height) =>
    ipcRenderer.send("resize-window", width, height),
  getPrompt: (user_prompt) => ipcRenderer.send("prompt-to-py", user_prompt),
  closeResponse: () => ipcRenderer.send("close-response"),
  stopSpeaking: () => ipcRenderer.send("stop-speaking"),
});

contextBridge.exposeInMainWorld("electron", {
  ipcRenderer: {
    on: (channel, func) => {
      const listener = (event, ...args) => func(event, ...args);
      ipcRenderer.on(channel, listener);
      return () => ipcRenderer.removeListener(channel, listener);
    },
    once: (channel, func) => {
      ipcRenderer.once(channel, (event, ...args) => func(event, ...args));
    },
    removeAllListeners: (channel) => {
      ipcRenderer.removeAllListeners(channel);
    },
    send: (channel, ...args) => {
      ipcRenderer.send(channel, ...args);
    },
  },
});
