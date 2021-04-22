from django.conf import settings
import requests
from src.apis.notification import BaseNotification


class BaseOtpNotification(BaseNotification):
    service_name = "AUTHY"

    def send_verfication_code(self, user):
        data = {
            "api_key": settings.AUTH_KEY,
            "via": "sms",
            "country_code": settings.COUNTRY_CODE,
            "phone_number": user.mobile_number,
        }
        otp_send_url = settings.OTP_SEND_URL
        response = requests.post(otp_send_url, data=data)
        return response

    def verify_sent_code(self, otp, user):
        data = {
            "api_key": settings.AUTH_KEY,
            "country_code": settings.COUNTRY_CODE,
            "phone_number": user.mobile_number,
            "verification_code": otp,
        }
        otp_verify_url = settings.OTP_VERIFY_URL
        response = requests.get(otp_verify_url, data=data)
        return response