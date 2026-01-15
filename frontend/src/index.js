/* eslint-disable prettier/prettier */
import React from "react";
import ReactDOM from "react-dom/client";
import App from "App";
import { BrowserRouter } from "react-router-dom";

// Material Dashboard 2 React Provider
import { MaterialUIControllerProvider } from "context";

// Your Auth Provider
import { AuthProvider } from "context/AuthContext";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <BrowserRouter>
    <MaterialUIControllerProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MaterialUIControllerProvider>
  </BrowserRouter>
);
