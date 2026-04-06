import hashlib
import random
import time

def hash_aadhaar(aadhaar: str) -> str:
    """Hashes the Aadhaar string using SHA-256 for secure DB storage."""
    return hashlib.sha256(aadhaar.encode('utf-8')).hexdigest()

def generate_otp() -> str:
    """Generates a random 6-digit OTP."""
    return str(random.randint(100000, 999999))

def otp_expiry() -> int:
    """Returns the UNIX timestamp for 60 seconds from now."""
    return int(time.time()) + 60