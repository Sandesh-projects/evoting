from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date

# ---------------------------------------------------------
# 1. Registration Model
# ---------------------------------------------------------
class UserRegister(BaseModel):
    full_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        pattern=r"^[A-Za-z\s]+$", 
        description="Legal name as per government ID (Letters and spaces only)"
    )
    email: EmailStr = Field(
        ..., 
        description="Used for sending secure OTPs and voting receipts"
    )
    aadhaar_number: str = Field(
        ..., 
        pattern=r"^\d{12}$", 
        description="Strictly 12 numeric digits without spaces or dashes"
    )
    phone_number: Optional[str] = Field(
        None, 
        pattern=r"^\+91\d{10}$", 
        description="Optional: Indian phone number for SMS OTP (+91 followed by 10 digits)"
    )
    date_of_birth: date = Field(
        ..., 
        description="Required to verify legal voting age"
    )

    # Real-world business logic: Automatically verify they are 18+
    @field_validator('date_of_birth')
    @classmethod
    def check_legal_age(cls, v: date) -> date:
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Citizen must be at least 18 years old to register for voting.')
        return v


# ---------------------------------------------------------
# 2. OTP Models
# ---------------------------------------------------------
class OTPRequest(BaseModel):
    aadhaar_number: str = Field(
        ..., 
        pattern=r"^\d{12}$", 
        description="The 12-digit ID of the user requesting the OTP"
    )

class OTPVerify(BaseModel):
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    otp: str = Field(
        ..., 
        pattern=r"^\d{6}$", 
        description="Strictly a 6-digit One Time Password"
    )


# ---------------------------------------------------------
# 3. Voting Model
# ---------------------------------------------------------
class VoteRequest(BaseModel):
    aadhaar_number: str = Field(
        ..., 
        pattern=r"^\d{12}$",
        description="Will be hashed by the backend before sending to the blockchain"
    )
    candidate_id: int = Field(
        ..., 
        gt=0, 
        description="Candidate ID must be a positive integer matching the smart contract"
    )


# ---------------------------------------------------------
# 4. Candidate Administration Model
# ---------------------------------------------------------
class CandidateRequest(BaseModel):
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Candidate's full name"
    )
    party_affiliation: str = Field(
        default="Independent", 
        max_length=50,
        description="Political party name, defaults to 'Independent'"
    )
    age: int = Field(
        ..., 
        ge=25, 
        description="Legal minimum age to contest an election (e.g., 25 in India)"
    )