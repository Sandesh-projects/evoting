import React, { useState } from "react";
import { API } from "../api/api";

const AdminPage = () => {
  const [message, setMessage] = useState({ text: "", type: "" });
  const [isLoading, setIsLoading] = useState(false);

  // Form States
  const [candidate, setCandidate] = useState({
    name: "",
    party_affiliation: "",
    age: "",
  });
  const [voter, setVoter] = useState({
    full_name: "",
    email: "",
    aadhaar_number: "",
    phone_number: "",
    date_of_birth: "",
  });

  // ---- Handlers ----
  const handleAddCandidate = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: "Deploying candidate to blockchain...", type: "info" });
    try {
      const res = await API.addCandidate({
        name: candidate.name,
        party_affiliation: candidate.party_affiliation,
        age: parseInt(candidate.age),
      });
      setMessage({
        text: `Success: ${res.message}. TX: ${res.transaction_hash.substring(0, 10)}...`,
        type: "success",
      });
      setCandidate({ name: "", party_affiliation: "", age: "" });
    } catch (err) {
      setMessage({ text: err.message, type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegisterVoter = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: "Adding citizen to voter roll...", type: "info" });
    try {
      await API.register(voter);
      setMessage({
        text: `Success: ${voter.full_name} has been added to the official voter roll.`,
        type: "success",
      });
      setVoter({
        full_name: "",
        email: "",
        aadhaar_number: "",
        phone_number: "",
        date_of_birth: "",
      });
    } catch (err) {
      setMessage({ text: err.message, type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAction = async (actionFn, successMsg) => {
    setIsLoading(true);
    setMessage({ text: "Processing transaction...", type: "info" });
    try {
      await actionFn();
      setMessage({ text: successMsg, type: "success" });
    } catch (err) {
      setMessage({ text: err.message, type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-10 px-4">
      <div className="mb-8 border-b pb-4">
        <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight">
          Election Commission Panel
        </h1>
        <p className="text-gray-500 mt-1">
          Manage voter rolls, candidates, and blockchain state.
        </p>
      </div>

      {message.text && (
        <div
          className={`mb-8 p-4 rounded-md font-medium shadow-sm animate-fade-in ${
            message.type === "error"
              ? "bg-red-50 text-red-700 border border-red-200"
              : message.type === "success"
                ? "bg-green-50 text-green-700 border border-green-200"
                : "bg-blue-50 text-blue-700 border border-blue-200"
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* 1. Register Voter Card (Web2 DB) */}
        <div className="bg-white p-6 rounded-xl shadow-md border-t-4 border-blue-500">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            Register Citizen (Voter Roll)
          </h2>
          <form onSubmit={handleRegisterVoter} className="space-y-3">
            <input
              type="text"
              placeholder="Full Name"
              required
              value={voter.full_name}
              onChange={(e) =>
                setVoter({ ...voter, full_name: e.target.value })
              }
              className="w-full px-4 py-2 border rounded"
            />
            <input
              type="email"
              placeholder="Email Address"
              required
              value={voter.email}
              onChange={(e) => setVoter({ ...voter, email: e.target.value })}
              className="w-full px-4 py-2 border rounded"
            />
            <input
              type="text"
              placeholder="12-Digit Aadhaar"
              required
              value={voter.aadhaar_number}
              onChange={(e) =>
                setVoter({ ...voter, aadhaar_number: e.target.value })
              }
              className="w-full px-4 py-2 border rounded"
            />
            <input
              type="text"
              placeholder="Phone (+91...)"
              value={voter.phone_number}
              onChange={(e) =>
                setVoter({ ...voter, phone_number: e.target.value })
              }
              className="w-full px-4 py-2 border rounded"
            />
            <input
              type="date"
              required
              value={voter.date_of_birth}
              onChange={(e) =>
                setVoter({ ...voter, date_of_birth: e.target.value })
              }
              className="w-full px-4 py-2 border rounded text-gray-600"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-2 rounded font-bold hover:bg-blue-700 transition shadow disabled:opacity-50"
            >
              Add to DB
            </button>
          </form>
        </div>

        {/* 2. Add Candidate Card (Web3 Blockchain) */}
        <div className="bg-white p-6 rounded-xl shadow-md border-t-4 border-purple-500">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            Add Candidate (Ballot)
          </h2>
          <form onSubmit={handleAddCandidate} className="space-y-4">
            <input
              type="text"
              placeholder="Candidate Name"
              required
              value={candidate.name}
              onChange={(e) =>
                setCandidate({ ...candidate, name: e.target.value })
              }
              className="w-full px-4 py-2 border rounded"
            />
            <input
              type="text"
              placeholder="Party Affiliation"
              required
              value={candidate.party_affiliation}
              onChange={(e) =>
                setCandidate({
                  ...candidate,
                  party_affiliation: e.target.value,
                })
              }
              className="w-full px-4 py-2 border rounded"
            />
            <input
              type="number"
              placeholder="Age"
              min="25"
              required
              value={candidate.age}
              onChange={(e) =>
                setCandidate({ ...candidate, age: e.target.value })
              }
              className="w-full px-4 py-2 border rounded"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-purple-600 text-white py-2 rounded font-bold hover:bg-purple-700 transition shadow disabled:opacity-50"
            >
              Deploy to Blockchain
            </button>
          </form>
        </div>

        {/* 3. Master Controls Card */}
        <div className="bg-white p-6 rounded-xl shadow-md border-t-4 border-red-500 flex flex-col space-y-4">
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            Master Controls
          </h2>
          <button
            onClick={() =>
              handleAction(
                API.startElection,
                "Election is now LIVE. Blockchain is accepting votes.",
              )
            }
            disabled={isLoading}
            className="w-full bg-green-500 text-white py-3 rounded shadow hover:bg-green-600 font-bold text-lg transition disabled:opacity-50"
          >
            ▶ Start Election
          </button>
          <button
            onClick={() =>
              handleAction(
                API.stopElection,
                "Election STOPPED. Voting closed on the blockchain.",
              )
            }
            disabled={isLoading}
            className="w-full bg-red-500 text-white py-3 rounded shadow hover:bg-red-600 font-bold text-lg transition disabled:opacity-50"
          >
            ⏹ Stop Election
          </button>
          <hr className="my-2 border-gray-200" />
          <button
            onClick={() =>
              handleAction(
                API.publishResults,
                "Results successfully archived to MongoDB!",
              )
            }
            disabled={isLoading}
            className="w-full bg-gray-800 text-white py-3 rounded shadow hover:bg-gray-900 font-bold text-lg transition disabled:opacity-50"
          >
            Archive Final Results to DB
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
