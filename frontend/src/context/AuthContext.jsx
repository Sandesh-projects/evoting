import React, { createContext, useState, useContext } from "react";

// 1. Create the Context
const AuthContext = createContext();

// 2. Create the Provider Component
export const AuthProvider = ({ children }) => {
  // Initialize state directly from localStorage so they stay logged in upon refresh
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("voter_session");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // Simple admin toggle (for your college presentation)
  const [isAdmin, setIsAdmin] = useState(() => {
    return localStorage.getItem("is_admin") === "true";
  });

  // ---- Actions ----
  const login = (userData) => {
    setUser(userData);
    localStorage.setItem("voter_session", JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("voter_session");
  };

  const setAdminStatus = (status) => {
    setIsAdmin(status);
    localStorage.setItem("is_admin", status);
  };

  // 3. Provide this data to the rest of the app
  return (
    <AuthContext.Provider
      value={{ user, login, logout, isAdmin, setAdminStatus }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// 4. Create a custom hook for ultra-clean code in your components
export const useAuth = () => {
  return useContext(AuthContext);
};
