import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def send_otp(receiver_email: str, otp: str) -> bool:
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        # Better email formatting
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "Your Secure E-Voting OTP"

        body = f"Hello,\n\nYour OTP for the E-Voting system is: {otp}\n\nThis code is valid for 60 seconds. Do not share it with anyone."
        msg.attach(MIMEText(body, 'plain'))

        server.send_message(msg)
        server.quit()
        
        print(f"✅ OTP successfully sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email. Error: {e}")
        return False