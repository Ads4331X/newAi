import { Box } from "@mui/material";
import ReactMarkDown from "react-markdown";

export function ResponseBox({ response, role = "assistant" }) {
  const isUser = role === "user";

  return (
    <Box
      sx={{
        WebkitAppRegion: "no-drag",
        backgroundColor: isUser ? "#7c3aed" : "whitesmoke",
        color: isUser ? "white" : "black",
        fontSize: 16,
        p: 1.5,
        borderRadius: 2,
        maxWidth: "75%",
        width: "fit-content",
        textAlign: "left",
        whiteSpace: "pre-wrap",
        overflowWrap: "break-word",
        wordBreak: "break-word",
        boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
        "& h1, & h2, & h3, & h4, & h5, & h6": {
          margin: "0.5em 0 0.2em 0",
        },
        "& li": {
          margin: "0.2em 0",
        },
        "& p": {
          margin: 0,
        },
      }}
    >
      <ReactMarkDown>{response}</ReactMarkDown>
    </Box>
  );
}
