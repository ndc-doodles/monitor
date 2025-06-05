# from twilio.rest import Client
# import os
# from dotenv import load_dotenv

# load_dotenv()

# account_sid = os.getenv("TWILIO_ACCOUNT_SID")
# auth_token = os.getenv("TWILIO_AUTH_TOKEN")
# twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# client = Client(account_sid, auth_token)

# def send_otp_via_sms(phone, otp):
#     # Safety check: 'to' number should NOT be the same as Twilio 'from' number
#     if phone == twilio_number:
#         raise ValueError("Recipient phone number must be different from the Twilio sender number.")
    
#     message = client.messages.create(
#         body=f"Your OTP is {otp}",
#         from_=twilio_number,
#         to=phone
#     )
#     return message.sid
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def send_otp_via_sms(phone, otp):
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=twilio_number,
        to=phone
    )
    return message.sid