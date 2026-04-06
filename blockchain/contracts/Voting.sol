// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;

contract Voting {
    // 🔐 Admin
    address public admin;

    // 🗳️ Election state
    bool public electionActive;

    // 👤 Candidate structure
    struct Candidate {
        uint id;
        string name;
        uint voteCount;
    }

    // 📦 Storage
    mapping(uint => Candidate) public candidates;
    // FIXED: Track by Aadhaar hash instead of msg.sender (since backend proxy makes all calls)
    mapping(string => bool) public hasVoted; 
    uint public candidatesCount;

    // 📡 Events (Useful for transaction receipts)
    event CandidateAdded(uint id, string name);
    event ElectionStarted();
    event ElectionStopped();
    event VoteCasted(uint candidateId, string voterHash);

    // 🔐 Modifiers
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin allowed");
        _;
    }

    modifier electionRunning() {
        require(electionActive, "Election is not currently active");
        _;
    }

    modifier electionStopped() {
        require(!electionActive, "Election is already running");
        _;
    }

    // 🚀 Constructor
    constructor() {
        admin = msg.sender;
    }

    // ➕ Add Candidate
    function addCandidate(string memory _name) public onlyAdmin electionStopped {
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
        emit CandidateAdded(candidatesCount, _name);
    }

    // ▶️ Start Election
    function startElection() public onlyAdmin electionStopped {
        require(candidatesCount > 0, "Cannot start election with 0 candidates");
        electionActive = true;
        emit ElectionStarted();
    }

    // ⏹️ Stop Election
    function stopElection() public onlyAdmin electionRunning {
        electionActive = false;
        emit ElectionStopped();
    }

    // 🗳️ Vote Function (Now requires Aadhaar hash)
    function vote(uint _candidateId, string memory _voterHash) public onlyAdmin electionRunning {
        require(!hasVoted[_voterHash], "User has already voted on the blockchain");
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate ID");

        hasVoted[_voterHash] = true;
        candidates[_candidateId].voteCount++;
        
        emit VoteCasted(_candidateId, _voterHash);
    }

    // 📊 Get Total Candidates
    function getCandidatesCount() public view returns (uint) {
        return candidatesCount;
    }

    // 📊 Get Candidate Details
    function getCandidate(uint _id) public view returns (uint, string memory, uint) {
        require(_id > 0 && _id <= candidatesCount, "Invalid candidate ID");
        Candidate memory c = candidates[_id];
        return (c.id, c.name, c.voteCount);
    }
}