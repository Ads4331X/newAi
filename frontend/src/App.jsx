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
            WebkitAppRegion: "drag",
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
          <ZoomOutMapIcon
            fontSize="large"
            sx={{
              WebkitAppRegion: "drag",
              cursor: "grab",
              color: "white",
            }}
          />
        </Box>

        <Box sx={{ WebkitAppRegion: "no-drag" }}>
          <Model />
        </Box>
      </Box>
    </Box>
  );
}

export default App;
