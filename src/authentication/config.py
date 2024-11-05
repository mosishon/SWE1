from src.config import config
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

mail_conf = ConnectionConfig(
    MAIL_USERNAME =config.MAIL_USERNAME,
    MAIL_PASSWORD = config.MAIL_PASSWORD,
    MAIL_FROM = config.MAIL_FROM,
    MAIL_PORT = config.MAIL_PORT,
    MAIL_SERVER = config.MAIL_SERVER,
    MAIL_STARTTLS = config.MAIL_STARTTLS,
    MAIL_SSL_TLS = config.MAIL_SSL_TLS,
    USE_CREDENTIALS = config.USE_CREDENTIALS,
    VALIDATE_CERTS = config.VALIDATE_CERTS
)