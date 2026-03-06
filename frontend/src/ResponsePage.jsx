import { Box } from "@mui/material";
import ReactMarkDown from "react-markdown";
import { useState, useEffect, useRef } from "react";

function ResponsePage() {
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef();

  useEffect(() => {
    if (window.electron?.ipcRenderer) {
      window.electron.ipcRenderer.on("load-history", (event, history) => {
        setMessages(history);
      });

      window.electron.ipcRenderer.on("python-response", (event, message) => {
        if (
          message.startsWith("MEMORY") ||
          message.startsWith("BASH OUTPUT") ||
          message.startsWith("EXECUTING:")
        )
          return;
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.content === message) return prev;
          return [...prev, { role: "assistant", content: message }];
        });
      });

      window.electron.ipcRenderer.on("user-message", (event, text) => {
        setMessages((prev) => [...prev, { role: "user", content: text }]);
      });
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Box
      sx={{
        width: "100vw",
        height: "100vh",
        overflowY: "auto",
        overflowX: "hidden",
        backgroundColor: "#f5f5f5",
        p: 2,
        display: "flex",
        flexDirection: "column",
        gap: 1,
      }}
    >
      {messages.map((msg, i) => (
        <Box
          key={i}
          sx={{
            display: "flex",
            justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
          }}
        >
          <Box
            sx={{
              maxWidth: "75%",
              backgroundColor: msg.role === "user" ? "#7c3aed" : "white",
              color: msg.role === "user" ? "white" : "black",
              p: 1.5,
              borderRadius: 2,
              fontSize: 16,
              boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
              "& p": { margin: 0 },
            }}
          >
            <ReactMarkDown>{msg.content}</ReactMarkDown>
          </Box>
        </Box>
      ))}
      <div ref={bottomRef} />
    </Box>
  );
}

export default ResponsePage;
