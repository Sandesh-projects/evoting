// The base URL of your FastAPI server
const BASE_URL = 'http://127.0.0.1:8000';

// A reusable helper function to process all HTTP requests cleanly
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 
            'Content-Type': 'application/json' 
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, options);
        const data = await response.json();
        
        if (!response.ok) {
            // 🔧 THE UPGRADE: Handle FastAPI 422 Validation Arrays cleanly
            if (response.status === 422 && Array.isArray(data.detail)) {
                // Extracts the field name and the error message (e.g., "phone_number: invalid format")
                const exactErrors = data.detail.map(err => `${err.loc[err.loc.length - 1]}: ${err.msg}`).join(', ');
                throw new Error(`Validation Error -> ${exactErrors}`);
            }
            
            // Handle standard string errors (like 400 or 403)
            throw new Error(typeof data.detail === 'string' ? data.detail : 'An error occurred connecting to the server.');
        }
        
        return data; 
    } catch (error) {
        console.error(`API Error [${method} ${endpoint}]:`, error.message);
        throw error;
    }
}

// ---- The Main API Object ----
// We export this so any React component can just call API.register(data), etc.
export const API = {
    // 👤 Auth Routes
    register: (data) => fetchAPI('/auth/register', 'POST', data),
    sendOtp: (aadhaar) => fetchAPI('/auth/send-otp', 'POST', { aadhaar_number: aadhaar }),
    verifyOtp: (aadhaar, otp) => fetchAPI('/auth/verify-otp', 'POST', { aadhaar_number: aadhaar, otp: otp }),

    // 🗳️ Voting Routes
    castVote: (aadhaar, candidateId) => fetchAPI('/election/vote', 'POST', { aadhaar_number: aadhaar, candidate_id: candidateId }),
    getLiveResults: () => fetchAPI('/election/results', 'GET'),
    getOfficialResults: () => fetchAPI('/election/official-results', 'GET'), // The Web2 MongoDB endpoint

    // 🔐 Admin Routes
    addCandidate: (data) => fetchAPI('/admin/add-candidate', 'POST', data),
    startElection: () => fetchAPI('/admin/start-election', 'POST'),
    stopElection: () => fetchAPI('/admin/stop-election', 'POST'),
    publishResults: () => fetchAPI('/admin/publish-results', 'POST')
};