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
from django.conf import settings

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

def send_whatsapp_message(to_number, message_text):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{to_number}",  # must be in format +91xxxx...
            body=message_text
        )
        return message.sid
    except Exception as e:
        return str(e)
