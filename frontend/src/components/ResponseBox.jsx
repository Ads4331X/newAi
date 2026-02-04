import { Box } from "@mui/material";
import ReactMarkDown from "react-markdown";

export function ResponseBox({ response }) {
  return (
    <Box
      sx={{
        WebkitAppRegion: "no-drag",
        backgroundColor: "whitesmoke",
        fontSize: 18,
        p: 2,
        borderRadius: 2,
        width: "fit-content",
        textAlign: "left",
        whiteSpace: "pre-wrap",
        "& h1, & h2, & h3, & h4, & h5, & h6": {
          margin: "0.5em 0",
        },
        "& p": {
          margin: "-1em 0",
        },
      }}
    >
      <ReactMarkDown>{response}</ReactMarkDown>
    </Box>
  );
}
