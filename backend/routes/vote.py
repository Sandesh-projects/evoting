from fastapi import APIRouter, HTTPException, status
from database import users_collection
from models import VoteRequest
from utils.security import hash_aadhaar
from utils.blockchain import contract, ADMIN_ACCOUNT
import logging

# Set up logging for audit trails
logger = logging.getLogger(__name__)
router = APIRouter()

# Helper function to prevent repeating the connection check
def get_contract():
    if not contract:
        logger.error("Blockchain connection failed: Contract not initialized.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Blockchain service is currently unavailable."
        )
    return contract

@router.post("/vote", status_code=status.HTTP_200_OK)
def cast_vote(req: VoteRequest):
    c = get_contract()
    
    # 🔧 Match the upgraded Pydantic model
    hashed = hash_aadhaar(req.aadhaar_number)
    user = users_collection.find_one({"aadhaar_hash": hashed})

    if not user:
        logger.warning("Vote attempt rejected: Unregistered user.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Citizen not found in voter registry.")

    # ---------------- Security Checks ----------------
    if not user.get("otp_verified"):
        logger.warning(f"Vote attempt rejected: OTP not verified for user {user['_id']}.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Identity not verified. Please complete OTP verification first."
        )
        
    if user.get("has_voted"):
        logger.warning(f"Double voting attempt blocked for user {user['_id']}.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Our records indicate you have already cast your vote. Double voting is prohibited."
        )

    try:
        # Send the hashed ID to the Smart Contract via the Relayer (Admin)
        tx_hash = c.functions.vote(req.candidate_id, hashed).transact({
            "from": ADMIN_ACCOUNT
        })

        # Lock the user's account in Web2 Database immediately after Web3 success
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"has_voted": True, "otp_verified": False}} # Reset OTP status for extreme security
        )

        logger.info(f"Vote successfully cast and minted on blockchain for user {user['_id']}.")
        return {
            "status": "success",
            "message": "Your vote has been securely cryptographically recorded.",
            "transaction_hash": tx_hash.hex()
        }

    except Exception as e:
        logger.error(f"Blockchain Revert Error during voting: {str(e)}")
        # Mask the raw Solidity error from the user for security
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Blockchain rejected the vote. Ensure the election is active and the candidate ID is valid."
        )
    
@router.get("/results", status_code=status.HTTP_200_OK)
def get_results():
    c = get_contract()
    
    try:
        is_active = c.functions.electionActive().call()
        
        if is_active:
            logger.warning("Attempt to access live results blocked. Election is still ongoing.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="The election is currently active. Results remain classified until the admin officially stops the election."
            )

        results = []
        count = c.functions.candidatesCount().call()

        for i in range(1, count + 1):
            candidate = c.functions.candidates(i).call()
            results.append({
                "id": candidate[0],
                "name": candidate[1],
                "party": candidate[2], 
                "age": candidate[3],   
                "votes": candidate[4]  
            })

        # 🏆 THE NEW FEATURE: Calculate the Winner(s)
        winners = []
        if results:
            # 1. Find the highest vote count among all candidates
            max_votes = max(candidate["votes"] for candidate in results)
            
            # 2. Only declare a winner if at least one vote was cast
            if max_votes > 0:
                # 3. Find everyone who has that max score (This gracefully handles ties!)
                winners = [candidate for candidate in results if candidate["votes"] == max_votes]

        return {
            "status": "success",
            "total_candidates": count,
            "winners": winners,  # The new key is added here!
            "results": results
        }
        
    except HTTPException:
        raise 
    except Exception as e:
        logger.error(f"Failed to fetch results from blockchain: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to retrieve election data from the blockchain ledger."
        )