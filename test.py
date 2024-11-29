from fastapi import FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

app = FastAPI()


# Configuration for FastAPI-Mail
class EmailConfig:
    MAIL_USERNAME = "termyar.15@gmail.com"
    MAIL_PASSWORD = "zfvkmavwoqdlfdzz"  # Use App Password if 2FA is enabled
    MAIL_FROM = "termyar.15@gmail.com"
    MAIL_PORT = 465
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_TLS = True
    MAIL_SSL = True
    MAIL_FROM_NAME = "Your Name"


conf = ConnectionConfig(
    MAIL_USERNAME=EmailConfig.MAIL_USERNAME,
    MAIL_PASSWORD=EmailConfig.MAIL_PASSWORD,
    MAIL_FROM=EmailConfig.MAIL_FROM,
    MAIL_PORT=EmailConfig.MAIL_PORT,
    MAIL_SERVER=EmailConfig.MAIL_SERVER,
    MAIL_FROM_NAME=EmailConfig.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)


# Define the email schema
class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str


message = MessageSchema(
    subject="hi",
    recipients=["mostafa1382ma@gmail.com"],  # List of recipients
    body="gooooooooh",
    subtype=MessageType.plain,
)

fm = FastMail(conf)
import asyncio

asyncio.get_event_loop().run_until_complete(fm.send_message(message))
