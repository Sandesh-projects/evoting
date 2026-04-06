from fastapi import APIRouter, HTTPException
from database import users_collection
from models import UserRegister, OTPRequest, OTPVerify
from utils.security import hash_aadhaar, generate_otp, otp_expiry
from utils.email import send_otp
import time

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    hashed = hash_aadhaar(user.aadhaar)
    
    # Check if user already exists
    if users_collection.find_one({"aadhaar_hash": hashed}):
        raise HTTPException(status_code=400, detail="Aadhaar already registered")

    user_dict = {
        "name": user.name,
        "email": user.email,
        "aadhaar_hash": hashed,
        "has_voted": False,
        "otp_verified": False  # Explicitly tracking this now
    }
    
    users_collection.insert_one(user_dict)
    return {"message": "User registered successfully"}

@router.post("/send-otp")
def send_otp_api(req: OTPRequest):
    hashed = hash_aadhaar(req.aadhaar)
    user = users_collection.find_one({"aadhaar_hash": hashed})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    expiry = otp_expiry()

    # Reset otp_verified to False every time a new OTP is requested
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"otp": otp, "otp_expiry": expiry, "otp_verified": False}}
    )

    email_sent = send_otp(user["email"], otp)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
def verify_otp(req: OTPVerify):
    hashed = hash_aadhaar(req.aadhaar)
    user = users_collection.find_one({"aadhaar_hash": hashed})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("otp") != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if int(time.time()) > user.get("otp_expiry", 0):
        raise HTTPException(status_code=400, detail="OTP expired")

    # 🔧 THE FIX: Unlock the user's ability to vote
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"otp_verified": True}, "$unset": {"otp": "", "otp_expiry": ""}} # Clean up used OTP
    )

    return {"message": "OTP verified successfully. You may now vote."}