from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    aadhaar: str

class OTPRequest(BaseModel):
    aadhaar: str

class OTPVerify(BaseModel):
    aadhaar: str
    otp: str

class VoteRequest(BaseModel):
    candidate_id: int
    aadhaar: str

class CandidateRequest(BaseModel):
    name: str