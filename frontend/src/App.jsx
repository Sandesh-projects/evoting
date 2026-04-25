import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";

// Page Imports
import AuthPage from "./pages/AuthPage";
import AdminPage from "./pages/AdminPage";
import VotePage from "./pages/VotePage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    // AuthProvider gives every component inside it access to the user's session state
    <AuthProvider>
      <Router>
        {/* Tailwind styling for the main app shell */}
        <div className="min-h-screen bg-gray-100 flex flex-col text-gray-800 antialiased selection:bg-blue-200">
          {/* Our top navigation bar will sit on every single page */}
          <Navbar />

          <main className="flex-grow">
            <Routes>
              {/* If they hit the root URL, immediately bounce them to the Auth page */}
              <Route path="/" element={<Navigate to="/auth" replace />} />

              {/* Public Routes */}
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/results" element={<ResultsPage />} />
              <Route path="/admin" element={<AdminPage />} />

              {/* 🔒 Protected Route: Only verified citizens can access this! */}
              <Route
                path="/vote"
                element={
                  <ProtectedRoute>
                    <VotePage />
                  </ProtectedRoute>
                }
              />

              {/* 404 Fallback */}
              <Route
                path="*"
                element={
                  <h1 className="text-center text-red-500 font-bold text-2xl mt-20">
                    404 - Page Not Found
                  </h1>
                }
              />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
