import hashlib

def hash_aadhaar(aadhaar: str):
    return hashlib.sha256(aadhaar.encode()).hexdigest()