import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext.jsx";

const rolePath = {
  ADMIN: "/login/admin",
  TRAINEE: "/login/trainee",
  EMPLOYER: "/login/employer",
  PROVIDER: "/login/provider",
};

export default function ProtectedRoute({ allowedRoles }) {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) return <div className="simple-page"><p>Validating session...</p></div>;
  if (!isAuthenticated) {
    const fallback = allowedRoles?.[0] ? rolePath[allowedRoles[0]] : "/login";
    return <Navigate to={fallback} replace state={{ from: location }} />;
  }
  if (allowedRoles?.length && !allowedRoles.includes(user.role)) {
    return <Navigate to={rolePath[user.role] || "/role"} replace />;
  }
  return <Outlet />;
}
