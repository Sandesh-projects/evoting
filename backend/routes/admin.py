from fastapi import APIRouter, HTTPException, status
from models import CandidateRequest
from utils.blockchain import contract, ADMIN_ACCOUNT
import logging
from database import results_collection
from datetime import datetime


# Set up a logger for real-world debugging
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

@router.post("/add-candidate", status_code=status.HTTP_201_CREATED)
def add_candidate(req: CandidateRequest):
    c = get_contract()
    try:
        # Note: We are now passing the new fields to the blockchain!
        tx_hash = c.functions.addCandidate(req.name, req.party_affiliation, req.age).transact({
            "from": ADMIN_ACCOUNT
        })
        
        return {
            "status": "success",
            "message": f"Candidate '{req.name}' added successfully",
            "transaction_hash": tx_hash.hex(),
            "data": req.model_dump() # Returns the validated Pydantic data back to the user
        }
    except Exception as e:
        logger.error(f"Blockchain Transaction Failed: {str(e)}")
        # We don't expose raw blockchain errors to the user in production
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to add candidate. Verify admin permissions and contract state."
        )
    
@router.post("/start-election", status_code=status.HTTP_200_OK)
def start_election():
    c = get_contract()
    try:
        tx_hash = c.functions.startElection().transact({
            "from": ADMIN_ACCOUNT
        })
        return {
            "status": "success",
            "message": "Election started successfully",
            "transaction_hash": tx_hash.hex()
        }
    except Exception as e:
        logger.error(f"Failed to start election: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not start election.")
    
@router.post("/stop-election", status_code=status.HTTP_200_OK)
def stop_election():
    c = get_contract()
    try:
        tx_hash = c.functions.stopElection().transact({
            "from": ADMIN_ACCOUNT
        })
        return {
            "status": "success",
            "message": "Election stopped successfully",
            "transaction_hash": tx_hash.hex()
        }
    except Exception as e:
        logger.error(f"Failed to stop election: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not stop election.")
    

@router.post("/publish-results", status_code=status.HTTP_201_CREATED)
def publish_results_to_db():
    c = get_contract()
    
    try:
        # 1. CRITICAL: Ensure the election is officially stopped first!
        is_active = c.functions.electionActive().call()
        if is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot publish results. The election is still active!"
            )

        # 2. Check if results are already published (Prevent duplicates)
        existing_result = results_collection.find_one({"status": "official"})
        if existing_result:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Results have already been published to the database."
            )

        # 3. Fetch the final immutable tally directly from the Blockchain
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

        # 4. Calculate the Winner(s)
        winners = []
        total_votes_cast = 0
        if results:
            max_votes = max(candidate["votes"] for candidate in results)
            if max_votes > 0:
                winners = [candidate for candidate in results if candidate["votes"] == max_votes]
            # Tally total votes cast for analytics
            total_votes_cast = sum(candidate["votes"] for candidate in results)

        # 5. Package the official record
        official_record = {
            "election_date": datetime.utcnow().isoformat(),
            "status": "official",
            "total_candidates": count,
            "total_votes_cast": total_votes_cast,
            "winners": winners,
            "detailed_results": results
        }

        # 6. Save to MongoDB
        results_collection.insert_one(official_record)

        # Remove the MongoDB ObjectId before returning the JSON to the user
        official_record.pop("_id", None)

        return {
            "message": "Official election results have been successfully archived to the database.",
            "data": official_record
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred while saving the results to the database."
        )