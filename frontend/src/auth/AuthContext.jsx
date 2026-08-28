import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getCurrentUser, loginUser } from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

  const clearSession = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setUser(null);
  };

  useEffect(() => {
    const handleUnauthorized = () => clearSession();
    window.addEventListener("skilloutcome:unauthorized", handleUnauthorized);

    const token = localStorage.getItem("token");
    if (!token) {
      setInitializing(false);
      return () => window.removeEventListener("skilloutcome:unauthorized", handleUnauthorized);
    }

    getCurrentUser()
      .then((response) => {
        const currentUser = response.data;
        setUser(currentUser);
        localStorage.setItem("role", currentUser.role);
      })
      .catch(() => clearSession())
      .finally(() => setInitializing(false));

    return () => window.removeEventListener("skilloutcome:unauthorized", handleUnauthorized);
  }, []);

  const login = async (email, password) => {
    const response = await loginUser(email, password);
    const { access_token: token, role } = response.data;
    localStorage.setItem("token", token);
    localStorage.setItem("role", role);

    const account = await getCurrentUser();
    setUser(account.data);
    return account.data;
  };

  const logout = () => clearSession();

  const value = useMemo(
    () => ({ user, loading: initializing, isAuthenticated: Boolean(user), login, logout }),
    [user, initializing]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
