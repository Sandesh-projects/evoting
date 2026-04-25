import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../api/api";
import { useAuth } from "../context/AuthContext";

const AuthPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  // UI State
  const [otpSent, setOtpSent] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });
  const [isLoading, setIsLoading] = useState(false);

  // Form State
  const [aadhaar, setAadhaar] = useState("");
  const [otp, setOtp] = useState("");

  const handleSendOtp = async () => {
    if (aadhaar.length !== 12) {
      setMessage({ text: "Aadhaar must be exactly 12 digits.", type: "error" });
      return;
    }
    setIsLoading(true);
    try {
      setMessage({ text: "Sending OTP...", type: "info" });
      await API.sendOtp(aadhaar);
      setOtpSent(true);
      setMessage({
        text: "OTP sent to your registered email.",
        type: "success",
      });
    } catch (err) {
      // If the admin hasn't registered them, they will get a 404/400 error here!
      setMessage({
        text: err.message || "Aadhaar not found in the voter roll.",
        type: "error",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await API.verifyOtp(aadhaar, otp);
      login({ aadhaar_number: aadhaar });
      navigate("/vote");
    } catch (err) {
      setMessage({ text: err.message, type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-64px)] py-10 px-4">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full border-t-4 border-blue-600">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-extrabold text-gray-800">
            Citizen Voting Portal
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Authentication powered by Aadhaar & OTP
          </p>
        </div>

        {message.text && (
          <div
            className={`mb-6 p-3 rounded text-sm font-medium ${
              message.type === "error"
                ? "bg-red-50 text-red-600 border border-red-200"
                : message.type === "success"
                  ? "bg-green-50 text-green-700 border border-green-200"
                  : "text-blue-600"
            }`}
          >
            {message.text}
          </div>
        )}

        <form onSubmit={handleLoginSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Aadhaar Number
            </label>
            <input
              type="text"
              value={aadhaar}
              onChange={(e) => setAadhaar(e.target.value)}
              disabled={otpSent}
              className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-100"
              placeholder="12-digit Aadhaar"
              required
            />
          </div>

          {!otpSent ? (
            <button
              type="button"
              onClick={handleSendOtp}
              disabled={isLoading}
              className="w-full bg-gray-100 text-gray-800 py-3 rounded-md hover:bg-gray-200 font-bold transition disabled:opacity-50"
            >
              {isLoading ? "Processing..." : "Request OTP"}
            </button>
          ) : (
            <div className="space-y-4 pt-4 border-t animate-fade-in">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Enter 6-Digit OTP
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="w-full px-4 py-2 border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition"
                  placeholder="000000"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 font-bold transition shadow-md disabled:opacity-50"
              >
                {isLoading ? "Verifying..." : "Verify & Enter Voting Booth"}
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default AuthPage;
