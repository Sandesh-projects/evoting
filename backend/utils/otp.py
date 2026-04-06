import random
import time

def generate_otp():
    return str(random.randint(100000, 999999))

def otp_expiry():
    return int(time.time()) + 60   # 60 seconds