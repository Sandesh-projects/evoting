import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();

  // If there is no user session, redirect to the auth page immediately.
  // The 'replace' keyword prevents them from using the back button to return to the protected route.
  if (!user) {
    return <Navigate to="/auth" replace />;
  }

  // If they are logged in, render the protected component (like the VotePage)
  return children;
};

export default ProtectedRoute;
