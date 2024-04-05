from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

CONF = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(
    email: EmailStr, username: str, request_type: str, host: str
) -> None:
    """
    Sends an email with a token and expiration date for a given email address and request type.

    Args:
        email (EmailStr): The email address to send the email to.
        username (str): The username associated with the email address.
        request_type (str): The type of request being made ("registration" or "password reset").
        host (str): The host URL for the application.

    Raises:
        ConnectionErrors: If there is an error connecting to the email server.
    """
    try:
        token_verification, expiration_date = auth_service.create_email_token(
            {"sub": email}
        )
        message = MessageSchema(
            subject=f"FastAPI Contacts App - {request_type}",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
                "expiration": expiration_date,
                "request_type": request_type,
            },
            subtype=MessageType.html,
        )
        fast_mail = FastMail(CONF)
        await fast_mail.send_message(message, template_name="email_template.html")
    except ConnectionErrors as e:
        print(e)
