from fastapi import APIRouter, HTTPException, status
from database import users_collection
from models import UserRegister, OTPRequest, OTPVerify
from utils.security import hash_aadhaar, generate_otp, otp_expiry
from utils.email import send_otp
import time
import logging

# Set up a logger for security audits
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    try:
        # Match the new Pydantic model: user.aadhaar_number
        hashed = hash_aadhaar(user.aadhaar_number)
        
        # Check if user already exists
        if users_collection.find_one({"aadhaar_hash": hashed}):
            logger.warning(f"Registration attempt failed: ID hash already exists.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="A citizen with this ID is already registered."
            )

        user_dict = {
            "full_name": user.full_name, # Match new model
            "email": user.email,
            "phone_number": user.phone_number, # Added from new model
            "date_of_birth": user.date_of_birth.isoformat(), # Store as string
            "aadhaar_hash": hashed,
            "has_voted": False,
            "otp_verified": False,
            "last_otp_request": 0 # Track this to prevent email spamming
        }
        
        users_collection.insert_one(user_dict)
        logger.info(f"New user registered successfully: {user.full_name}")
        return {"status": "success", "message": "Citizen registered successfully."}
        
    except Exception as e:
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during registration."
        )

@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp_api(req: OTPRequest):
    hashed = hash_aadhaar(req.aadhaar_number)
    user = users_collection.find_one({"aadhaar_hash": hashed})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Citizen not found in voter registry.")

    current_time = int(time.time())
    
    # 🔧 REAL WORLD FIX: Prevent Email Spam (60-second cooldown)
    if current_time - user.get("last_otp_request", 0) < 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Please wait 60 seconds before requesting another OTP."
        )

    otp = generate_otp()
    expiry = otp_expiry()

    try:
        # Update user with new OTP, Expiry, and reset verification status
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "otp": otp, 
                "otp_expiry": expiry, 
                "otp_verified": False,
                "last_otp_request": current_time
            }}
        )

        email_sent = send_otp(user["email"], otp)
        if not email_sent:
            raise Exception("SMTP Server rejected the email.")
            
        logger.info(f"OTP sent successfully to {user['email']}")
        return {"status": "success", "message": f"Secure OTP sent to {user['email']}"}
        
    except Exception as e:
        logger.error(f"Failed to send OTP to {user.get('email')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to dispatch OTP email. Please try again later."
        )

@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp(req: OTPVerify):
    hashed = hash_aadhaar(req.aadhaar_number)
    user = users_collection.find_one({"aadhaar_hash": hashed})

    # Generic error messages for security (Don't let hackers know if the user exists or if the OTP is just wrong)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")

    current_time = int(time.time())

    # Check expiration first
    if current_time > user.get("otp_expiry", 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired. Please request a new one.")

    # Check OTP validity
    if user.get("otp") != req.otp:
        logger.warning(f"Failed OTP attempt for user ID: {user['_id']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP.")

    try:
        # 🔧 REAL WORLD FIX: Unlock voting and scrub the OTP from the database immediately
        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"otp_verified": True}, 
                "$unset": {"otp": "", "otp_expiry": ""} # Immediately delete the OTP so it cannot be reused
            }
        )
        logger.info(f"User {user['_id']} successfully verified OTP.")
        return {"status": "success", "message": "Identity verified. You are now authorized to cast your vote."}
        
    except Exception as e:
        logger.error(f"Database error during OTP verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred while verifying your identity."
        )