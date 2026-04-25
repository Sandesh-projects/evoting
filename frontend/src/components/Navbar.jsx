import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Navbar = () => {
  // We grab the user session state and the logout function directly from our Context!
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout(); // Clears localStorage and React state
    navigate("/auth"); // Redirects back to the login page
  };

  return (
    <nav className="bg-white shadow-md border-b-4 border-blue-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo / Brand Name */}
          <div className="flex items-center">
            <Link
              to="/auth"
              className="text-2xl font-extrabold text-gray-800 tracking-tight flex items-center gap-2"
            >
              <span className="text-blue-600">Secure</span>Vote
            </Link>
          </div>

          {/* Right side navigation links */}
          <div className="flex items-center space-x-2 md:space-x-4">
            {/* Anyone can view the results, so this is always visible */}
            <Link
              to="/results"
              className="text-gray-600 hover:text-blue-600 font-semibold px-3 py-2 rounded-md transition"
            >
              Results
            </Link>

            {/* Only show the Admin link if the admin flag is true */}
            {isAdmin && (
              <Link
                to="/admin"
                className="text-purple-600 hover:text-purple-800 font-bold px-3 py-2 rounded-md transition"
              >
                Admin Panel
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
