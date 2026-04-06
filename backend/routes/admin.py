from fastapi import APIRouter, HTTPException
from models import CandidateRequest
from utils.blockchain import contract, ADMIN_ACCOUNT

router = APIRouter()

@router.post("/add-candidate")
def add_candidate(req: CandidateRequest):
    if not contract:
        raise HTTPException(status_code=500, detail="Blockchain not connected")

    try:
        tx_hash = contract.functions.addCandidate(req.name).transact({
            "from": ADMIN_ACCOUNT
        })
        return {
            "message": f"Candidate '{req.name}' added successfully",
            "transaction_hash": tx_hash.hex()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/start-election")
def start_election():
    if not contract:
        raise HTTPException(status_code=500, detail="Blockchain not connected")

    try:
        tx_hash = contract.functions.startElection().transact({
            "from": ADMIN_ACCOUNT
        })
        return {
            "message": "Election started successfully",
            "transaction_hash": tx_hash.hex()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/stop-election")
def stop_election():
    if not contract:
        raise HTTPException(status_code=500, detail="Blockchain not connected")

    try:
        tx_hash = contract.functions.stopElection().transact({
            "from": ADMIN_ACCOUNT
        })
        return {
            "message": "Election stopped successfully",
            "transaction_hash": tx_hash.hex()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))