import { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("access") || null);
  const [role, setRole] = useState(localStorage.getItem("role") || null);

  const login = (accessToken, userRole) => {
    localStorage.setItem("access", accessToken);
    localStorage.setItem("role", userRole);
    setToken(accessToken);
    setRole(userRole);
  };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("role");
    setToken(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider value={{ token, role, login, logout }}>{children}</AuthContext.Provider>
  );
};

import PropTypes from "prop-types";

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
