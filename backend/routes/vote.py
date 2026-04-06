from fastapi import APIRouter, HTTPException
from database import users_collection
from models import VoteRequest
from utils.security import hash_aadhaar
from utils.blockchain import contract, ADMIN_ACCOUNT

router = APIRouter()

@router.post("/vote")
def cast_vote(req: VoteRequest):
    if not contract:
        raise HTTPException(status_code=500, detail="Blockchain not connected")

    hashed = hash_aadhaar(req.aadhaar)
    user = users_collection.find_one({"aadhaar_hash": hashed})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Security Checks
    if not user.get("otp_verified"):
        raise HTTPException(status_code=403, detail="OTP not verified. Please verify your identity first.")
    if user.get("has_voted"):
        raise HTTPException(status_code=400, detail="You have already cast your vote.")

    try:
        # 🔧 THE FIX: Send the hashed Aadhaar to the Smart Contract
        tx_hash = contract.functions.vote(req.candidate_id, hashed).transact({
            "from": ADMIN_ACCOUNT
        })

        # Update MongoDB after successful blockchain transaction
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"has_voted": True}}
        )

        return {
            "message": "Vote casted successfully",
            "transaction_hash": tx_hash.hex()
        }

    except Exception as e:
        # Catches Solidity 'require' failures
        raise HTTPException(status_code=400, detail=f"Blockchain Error: {str(e)}")
    
@router.get("/results")
def get_results():
    if not contract:
        raise HTTPException(status_code=500, detail="Blockchain not connected")

    results = []
    count = contract.functions.getCandidatesCount().call()

    for i in range(1, count + 1):
        candidate = contract.functions.getCandidate(i).call()
        results.append({
            "id": candidate[0],
            "name": candidate[1],
            "votes": candidate[2]
        })

    return {"results": results}