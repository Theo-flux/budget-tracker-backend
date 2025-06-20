from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import UploadFile
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.auth.authentication import Authentication
from src.config import Config
from src.misc.schemas import EmailTypes

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


class Mailer:
    mail = FastMail(config=mail_config)

    @staticmethod
    def _create_message(
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

    @staticmethod
    async def send_email_verification(email: str, first_name: str, base_url: str):
        token_payload = {"email": email}
        email_token = Authentication.create_url_safe_token(token_payload)
        verification_url = f"{base_url}api/v1/auth/verify/{email_token}"

        message = Mailer._create_message(
            recipients=[email],
            subject=EmailTypes.EMAIL_VERIFICATION.subject,
            template_body={"first_name": first_name, "verification_url": verification_url},
        )

        await Mailer.mail.send_message(message=message, template_name=EmailTypes.EMAIL_VERIFICATION.template)

    @staticmethod
    async def send_password_reset(email: str, first_name: str, base_url: str):
        token_payload = {"email": email}
        email_token = Authentication.create_url_safe_token(token_payload)
        reset_url = f"{base_url}api/v1/auth/pwd-reset/{email_token}"

        message = Mailer._create_message(
            recipients=[email],
            subject=EmailTypes.PWD_RESET.subject,
            template_body={"first_name": first_name, "reset_url": reset_url},
        )

        await Mailer.mail.send_message(message=message, template_name=EmailTypes.PWD_RESET.template)
