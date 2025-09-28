from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

def generate_email_verification_token(user):
    """
    Create a short-lived JWT specifically for email verification.
    """
    token = AccessToken.for_user(user)
    token["purpose"] = "email_verification"
    token.set_exp(lifetime=60 * 60 * 24)
    return str(token)

def decode_email_verification_token(token):
    """
    Decode and validate the email verification token.
    Returns the user_id if valid.
    """
    try:
        access_token = AccessToken(token)
        if access_token.get("purpose") != "email_verification":
            raise ValueError("Invalid token purpose")
        return access_token["user_id"]
    except TokenError:
        raise ValueError("Invalid or expired token")