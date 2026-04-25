import React, { useState, useEffect } from "react";
import { API } from "../api/api";

const ResultsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // UseEffect runs exactly once when the page loads to fetch the data
  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await API.getOfficialResults();
        setData(response.data);
      } catch (err) {
        // This handles our 404 "Not Published Yet" error beautifully
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-64px)]">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-12 w-12 bg-blue-500 rounded-full mb-4"></div>
          <p className="text-gray-500 font-semibold text-xl tracking-wide">
            Querying Official Database...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-64px)] px-4">
        <div className="text-center bg-white p-10 rounded-xl shadow border-t-4 border-red-500">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Results Unavailable
          </h2>
          <p className="text-xl text-red-600 font-medium">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-10 px-4 animate-fade-in">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
          Official Election Results
        </h1>
        <p className="text-gray-500 mt-2 font-medium">
          Verified by the Immutable Blockchain Ledger
        </p>
      </div>

      {/* Winner Banner */}
      <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-2xl p-8 shadow-xl text-center text-white mb-10 transform scale-105 transition hover:scale-110 duration-300">
        <h2 className="text-xl font-bold uppercase tracking-widest opacity-90 mb-1">
          Declared Winner
        </h2>
        {data.winners && data.winners.length > 0 ? (
          <>
            <h3 className="text-5xl font-extrabold mt-2 mb-2 drop-shadow-md">
              {data.winners.map((w) => w.name).join(" & ")}
            </h3>
            <p className="text-2xl font-semibold opacity-90 drop-shadow">
              {data.winners.map((w) => w.party).join(" / ")}
            </p>
          </>
        ) : (
          <h3 className="text-4xl font-extrabold mt-4">No Votes Cast</h3>
        )}
      </div>

      {/* Full Breakdown Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden border border-gray-100">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-bold text-gray-700">
            Detailed Vote Tally
          </h3>
          <span className="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full font-bold">
            Total Turnout: {data.total_votes_cast}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white text-gray-400 uppercase text-xs tracking-wider border-b">
                <th className="py-4 px-6 font-semibold">ID</th>
                <th className="py-4 px-6 font-semibold">Candidate</th>
                <th className="py-4 px-6 font-semibold">Party</th>
                <th className="py-4 px-6 text-right font-semibold">
                  Verified Votes
                </th>
              </tr>
            </thead>
            <tbody className="text-gray-700">
              {/* Sort candidates by highest votes first */}
              {[...data.detailed_results]
                .sort((a, b) => b.votes - a.votes)
                .map((cand) => (
                  <tr
                    key={cand.id}
                    className="border-b border-gray-50 hover:bg-gray-50 transition duration-150"
                  >
                    <td className="py-4 px-6 font-bold text-gray-400">
                      #{cand.id}
                    </td>
                    <td className="py-4 px-6 font-bold text-gray-800 text-lg">
                      {cand.name}
                    </td>
                    <td className="py-4 px-6">
                      <span className="bg-gray-100 text-gray-600 border border-gray-200 text-xs px-2 py-1 rounded-md uppercase font-bold tracking-wider">
                        {cand.party}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right font-extrabold text-2xl text-blue-600">
                      {cand.votes}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
