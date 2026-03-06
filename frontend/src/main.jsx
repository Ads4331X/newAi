import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import ResponsePage from "./ResponsePage.jsx";

const isResponse = window.location.hash === "#response";

createRoot(document.getElementById("root")).render(
  isResponse ? <ResponsePage /> : <App />,
);
