import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../api/api";
import { useAuth } from "../context/AuthContext";

const VotePage = () => {
  const navigate = useNavigate();
  // Grab the logged-in user and the logout function securely from Context
  const { user, logout } = useAuth();

  // UI State
  const [candidateId, setCandidateId] = useState("");
  const [message, setMessage] = useState({ text: "", type: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [receipt, setReceipt] = useState(null);

  const handleVoteSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({
      text: "Encrypting vote and minting to blockchain...",
      type: "info",
    });

    try {
      // Pass the Aadhaar from Context, and the Candidate ID from the form
      const res = await API.castVote(
        user.aadhaar_number,
        parseInt(candidateId),
      );

      // Clear any errors and set the success receipt
      setMessage({ text: "", type: "" });
      setReceipt(res.transaction_hash);
    } catch (err) {
      setMessage({ text: err.message, type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLeaveBooth = () => {
    logout();
    navigate("/auth");
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-64px)] py-10 px-4">
      <div className="bg-white p-8 rounded-xl shadow-2xl max-w-lg w-full border-t-8 border-blue-600">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-800 tracking-tight">
            Secure Voting Booth
          </h2>
          <p className="text-sm text-green-600 font-semibold mt-2 flex items-center justify-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            Identity Verified. Connection to Blockchain active.
          </p>
        </div>

        {/* Error Messaging Display */}
        {message.text && (
          <div
            className={`mb-6 p-4 rounded text-sm font-bold text-center ${
              message.type === "error"
                ? "bg-red-50 text-red-600 border border-red-200"
                : "bg-blue-50 text-blue-700"
            }`}
          >
            {message.text}
          </div>
        )}

        {/* If they haven't voted yet, show the form */}
        {!receipt ? (
          <form onSubmit={handleVoteSubmit} className="space-y-6">
            <div className="bg-blue-50 p-5 rounded-lg border border-blue-100">
              <label className="block text-sm font-bold text-blue-800 mb-2 uppercase tracking-wide">
                Enter Candidate ID
              </label>
              <input
                type="number"
                min="1"
                required
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
                disabled={isLoading}
                className="w-full px-4 py-3 text-xl border rounded focus:ring-4 focus:ring-blue-200 outline-none transition font-semibold text-gray-700"
                placeholder="e.g., 1 or 2"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-4 rounded-lg hover:bg-blue-700 font-extrabold text-xl shadow-lg transition transform hover:-translate-y-1 disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed"
            >
              {isLoading ? "PROCESSING..." : "CAST SECURE VOTE"}
            </button>
          </form>
        ) : (
          /* If they HAVE voted, show the immutable receipt */
          <div className="mt-2 p-6 bg-green-50 border-2 border-green-200 rounded-xl text-center animate-fade-in">
            <h3 className="text-2xl text-green-800 font-extrabold mb-2">
              Vote Minted!
            </h3>
            <p className="text-green-700 font-medium mb-4">
              Your vote has been permanently recorded on the blockchain.
            </p>

            <div className="bg-white p-3 rounded border border-green-100 break-all mb-6">
              <span className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">
                Transaction Hash
              </span>
              <span className="text-sm font-mono text-gray-700">{receipt}</span>
            </div>

            <button
              onClick={handleLeaveBooth}
              className="w-full bg-gray-800 text-white py-3 rounded hover:bg-gray-900 font-bold transition shadow"
            >
              Logout & Leave Booth
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VotePage;
