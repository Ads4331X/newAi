import { Box } from "@mui/material";
import { useState, useEffect, useRef } from "react";
import { ResponseBox } from "./components/ResponseBox";

function ResponsePage() {
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef();

  useEffect(() => {
    if (!window.electron?.ipcRenderer) return;

    const dedupeMessages = (list) => {
      const deduped = [];
      for (const msg of list) {
        const last = deduped[deduped.length - 1];
        if (last?.role === msg.role && last?.content === msg.content) continue;
        deduped.push(msg);
      }
      return deduped;
    };

    const offLoadHistory = window.electron.ipcRenderer.on(
      "load-history",
      (event, history) => {
        if (!Array.isArray(history)) return;
        setMessages((prev) => {
          const normalizedHistory = dedupeMessages(history);
          if (prev.length === 0) return normalizedHistory;
          if (normalizedHistory.length >= prev.length) return normalizedHistory;

          // If backend sends a shorter snapshot, preserve newer in-memory items.
          return dedupeMessages([
            ...normalizedHistory,
            ...prev.slice(normalizedHistory.length),
          ]);
        });
      },
    );

    const offPythonResponse = window.electron.ipcRenderer.on(
      "python-response",
      (event, message) => {
        if (
          message.startsWith("STT:") ||
          message.startsWith("MEMORY") ||
          message.startsWith("BASH OUTPUT") ||
          message.startsWith("EXECUTING:")
        ) {
          return;
        }

        setMessages((prev) =>
          dedupeMessages([...prev, { role: "assistant", content: message }]),
        );
      },
    );

    const offUserMessage = window.electron.ipcRenderer.on(
      "user-message",
      (event, text) => {
        setMessages((prev) =>
          dedupeMessages([...prev, { role: "user", content: text }]),
        );
      },
    );

    return () => {
      offLoadHistory?.();
      offPythonResponse?.();
      offUserMessage?.();
    };
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Box
      sx={{
        width: "100%",
        height: "100vh",
        overflowY: "auto",
        overflowX: "hidden",
        backgroundColor: "#f5f5f5",
        p: 2,
        display: "flex",
        flexDirection: "column",
        gap: 1,
        boxSizing: "border-box",
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
          <ResponseBox response={msg.content} role={msg.role} />
        </Box>
      ))}
      <div ref={bottomRef} />
    </Box>
  );
}

export default ResponsePage;
