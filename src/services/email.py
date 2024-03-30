import os
from dotenv import load_dotenv
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.auth import auth_service
from src.conf.config import settings

load_dotenv()
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


async def send_email(email: EmailStr, username: str, host: str) -> None:
    try:
        token_verification, expiration_date = auth_service.create_email_token(
            {"sub": email}
        )
        message = MessageSchema(
            subject="FastAPI Contacts App - Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
                "expiration": expiration_date,
            },
            subtype=MessageType.html,
        )
        fast_mail = FastMail(CONF)
        await fast_mail.send_message(message, template_name="email_template.html")
    except ConnectionErrors as e:
        print(e)
