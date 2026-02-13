from mailjet_rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp, first_name):
    api_key = settings.MAILJET_API_KEY
    api_secret = settings.MAILJET_API_SECRET
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    data = {
        'Messages': [
            {
                "From": {
                    "Email": settings.DEFAULT_FROM_EMAIL,
                    "Name": "Ecommerce Admin"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": first_name
                    }
                ],
                "Subject": f"{otp} is your Admin Login Code",
                "TextPart": f"Hi {first_name}, your login code is {otp}. It expires in 5 minutes.",
                "HTMLPart": f"""
                    <h3>Hello {first_name},</h3>
                    <p>You requested a login code for the Ecommerce Admin Dashboard.</p>
                    <h1 style='color: #2e6da4; letter-spacing: 5px;'>{otp}</h1>
                    <p>This code is valid for <b>5 minutes</b>. If you did not request this, please ignore this email.</p>
                """,
                "CustomID": "AdminLoginOTP"
            }
        ]
    }

    try:
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            return True
        else:
            logger.error(f"Mailjet failed: {result.status_code} - {result.json()}")
            return False
    except Exception as e:
        logger.error(f"Mailjet error: {str(e)}")
        return False