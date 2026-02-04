import { Model } from "./components/Model";
import { OutlinedInput, Box, CircularProgress } from "@mui/material";
import ZoomOutMapIcon from "@mui/icons-material/ZoomOutMap";
import { useState, useEffect } from "react";

function App() {
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  // Listen for Python responses
  useEffect(() => {
    if (window.electron?.ipcRenderer) {
      window.electron.ipcRenderer.on("python-response", (event, message) => {
        console.log("Got response from Python:", message);
        setResponse(message);
        setLoading(false);
      });
    }
  }, []);
  return (
    <Box
      sx={{
        width: "min-content",
        height: "min-content",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        WebkitAppRegion: "drag",
      }}
    >
      <Box>
        <Box
          sx={{
            p: "10px",
            borderRadius: 5,
            WebkitAppRegion: "drag",
            display: "flex",
            justifyContent: "space-around",
            alignItems: "center",
            cursor: "grab",
            "&:active": {
              cursor: "grabbing",
            },
          }}
        >
          <OutlinedInput
            placeholder="Enter a Prompt"
            sx={{
              backgroundColor: "white",
              borderRadius: 5,
              WebkitAppRegion: "no-drag",
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                setResponse("");
                setLoading(true);
                const user_prompt = event.target.value;
                sendPrompt(user_prompt);
                event.target.value = "";
              }
            }}
          />
          <Box
            sx={{
              WebkitAppRegion: "drag",
              cursor: "grab",
              display: "inline-flex",
              position: "relative",
              "& svg": {
                fill: "url(#gradient1)",
              },
            }}
          >
            {loading && (
              <Box sx={{ color: "red" }}>
                <CircularProgress />
              </Box>
            )}
            {!loading && (
              <Box>
                <svg width="0" height="0">
                  <defs>
                    <linearGradient
                      id="gradient1"
                      x1="0%"
                      y1="0%"
                      x2="100%"
                      y2="100%"
                    >
                      <stop offset="0%" stopColor="#ff0080" />
                      <stop offset="33%" stopColor="#ff8c00" />
                      <stop offset="66%" stopColor="#40e0d0" />
                      <stop offset="100%" stopColor="#8a2be2" />
                    </linearGradient>
                  </defs>
                </svg>
                <ZoomOutMapIcon fontSize="large" />
              </Box>
            )}
          </Box>
        </Box>
        {response && (
          <Box
            sx={{
              color: "blue",
              fontSize: "18px",
              backgroundColor: "whitesmoke",
            }}
          >
            {response}
          </Box>
        )}
        <Box sx={{ WebkitAppRegion: "no-drag" }}>
          <Model />
        </Box>
      </Box>
    </Box>
  );
}
function sendPrompt(user_prompt) {
  if (user_prompt.length > 0) {
    console.log("enter", window.electronAPI);

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
