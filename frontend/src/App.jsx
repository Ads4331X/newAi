import { Model } from "./components/Model";
import { Box, CircularProgress } from "@mui/material";
import ZoomOutMapIcon from "@mui/icons-material/ZoomOutMap";
import { useState, useEffect } from "react";
import MicIcon from "@mui/icons-material/Mic";
import MicOffIcon from "@mui/icons-material/MicOff";
import { ResponseBox } from "./components/ResponseBox";

function App() {
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    if (window.electron?.ipcRenderer) {
      const handler = (event, message) => {
        if (message.startsWith("STT:")) {
          const text = message.slice(4).trim();
          setPrompt(text);
          setIsListening(false);
          setResponse("");
          setLoading(true);
          sendPrompt(text);
        } else {
          setResponse((prev) =>
            prev ? prev + message + " \n " : message + " \n ",
          );
          setLoading(false);
        }
      };
      window.electron.ipcRenderer.on("python-response", handler);
    }
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!prompt.trim()) return;
      setResponse("");
      setLoading(true);
      sendPrompt(prompt);
      setPrompt("");
    }
  };

  const toggleMic = () => {
    if (isListening) {
      setIsListening(false);
    } else {
      setIsListening(true);
      setPrompt("");
      window.electronAPI.getPrompt("MIC_START");
    }
  };

  return (
    <Box
      sx={{
        width: "min-content",
        display: "flex",
        justifyContent: "center",
        flexDirection: "column",
        alignItems: "center",
        WebkitAppRegion: "drag",
        p: 2,
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          p: 1,
          borderRadius: 2,
          WebkitAppRegion: "drag",
        }}
      >
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter your prompt..."
          style={{
            resize: "none",
            padding: "12px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            outline: "none",
            fontSize: "16px",
            width: "300px",
            height: "60px",
            WebkitAppRegion: "no-drag",
          }}
        />

        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            WebkitAppRegion: "no-drag",
            cursor: "pointer",
          }}
          onClick={toggleMic}
        >
          {isListening ? (
            <MicIcon fontSize="large" sx={{ color: "red" }} />
          ) : (
            <MicOffIcon fontSize="large" sx={{ color: "violet" }} />
          )}
        </Box>

        <Box sx={{ ml: 1, WebkitAppRegion: "drag" }}>
          {loading ? (
            <CircularProgress />
          ) : (
            <ZoomOutMapIcon fontSize="large" sx={{ color: "violet" }} />
          )}
        </Box>
      </Box>

      <Model />

      {response && (
        <Box
          sx={{
            fontSize: "18px",
            backgroundColor: "whitesmoke",
            p: 2,
            borderRadius: 2,
            maxWidth: 400,
            WebkitAppRegion: "no-drag",
          }}
        >
          <ResponseBox response={response} />
        </Box>
      )}
    </Box>
  );
}

function sendPrompt(user_prompt) {
  if (user_prompt.length > 0) {
    if (window.electronAPI && window.electronAPI.getPrompt) {
      window.electronAPI.getPrompt(user_prompt);
    }
  }
}

export default App;
