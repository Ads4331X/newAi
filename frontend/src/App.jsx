import { Model } from "./components/Model";
import { OutlinedInput, Box } from "@mui/material";
import ZoomOutMapIcon from "@mui/icons-material/ZoomOutMap";

function App() {
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
        </Box>

        <Box sx={{ WebkitAppRegion: "no-drag" }}>
          <Model />
        </Box>
      </Box>
    </Box>
  );
}

export default App;
