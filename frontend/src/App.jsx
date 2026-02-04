import { Model } from "./components/Model";
import { Box, CircularProgress } from "@mui/material";
import ZoomOutMapIcon from "@mui/icons-material/ZoomOutMap";
import { useState, useEffect } from "react";

import { ResponseBox } from "./components/ResponseBox";
function App() {
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState("");

  // Listen for Python responses
  useEffect(() => {
    if (window.electron?.ipcRenderer) {
      window.electron.ipcRenderer.on("python-response", (event, message) => {
        setResponse((prev) => prev + message + " \n "); // replace instead of append
        setLoading(false);
      });
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

  return (
    <Box
      sx={{
        width: "min-content",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        WebkitAppRegion: "drag",
        p: 2,
      }}
    >
      {/* Input and Send */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
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
            border: "none",
            outline: "none",
            fontSize: "16px",
            WebkitAppRegion: "no-drag",
          }}
        />
        <Box sx={{ ml: 1, WebkitAppRegion: "drag" }}>
          {loading ? (
            <CircularProgress />
          ) : (
            <ZoomOutMapIcon
              fontSize="large"
              sx={{
                color: "violet",
              }}
            />
          )}
        </Box>
      </Box>

      {/* Model output */}
      <Model />

      {/* Response box */}
      {response && (
        <Box
          sx={{
            fontSize: "18px",
            backgroundColor: "whitesmoke",
            p: 2,
            borderRadius: 2,
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
    } else {
      console.error(
        "Bridge is still not found. Try hitting 'Enter' again in 1 second.",
      );
    }
  }
}

export default App;
