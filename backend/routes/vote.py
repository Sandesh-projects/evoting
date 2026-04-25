from fastapi import APIRouter, HTTPException, status
from database import users_collection, results_collection
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
    
@router.get("/official-results", status_code=status.HTTP_200_OK)
def get_official_results():
    try:
        # Fetch the official published record from MongoDB
        official_record = results_collection.find_one({"status": "official"})
        
        if not official_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The official election results have not been published yet."
            )

        # Remove the MongoDB internal ID before sending to the user
        official_record.pop("_id", None)

        return {
            "message": "Official archived election results retrieved from database.",
            "data": official_record
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error while fetching official results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error while fetching official results."
        )