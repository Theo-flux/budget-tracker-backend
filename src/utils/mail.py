from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import UploadFile
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.config import Config

ROOT_DIR = Path(__file__).resolve().parent.parent

mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(ROOT_DIR, "templates"),
)

mail = FastMail(config=mail_config)


def create_message(
    recipients: List[EmailStr],
    attachments: List[Union[UploadFile, Dict, str]] = [],
    subject: str = "",
    body: Optional[Union[List, str]] = None,
    template_body: Optional[Union[List, str]] = None,
) -> MessageSchema:
    message = MessageSchema(
        recipients=recipients,
        attachments=attachments,
        subject=subject,
        body=body,
        template_body=template_body,
        subtype=MessageType.html,
    )

    return message
