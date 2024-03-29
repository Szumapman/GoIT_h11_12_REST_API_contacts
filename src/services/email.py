import os
from dotenv import load_dotenv
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.auth import auth_service

load_dotenv()
CONF = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=465,
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME="FastAPI Contacts App",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str) -> None:
    try:
        token_verivication = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="FastAPI Contacts App - Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verivication,
            },
            subtype="html",
        )
        fast_mail = FastMail(CONF)
        await fast_mail.send_message(message, template_name="email_template.html")
    except ConnectionErrors as e:
        print(e)
