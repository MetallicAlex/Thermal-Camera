import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from typing import List

from .models import EmailMessage, SMTPConfig, get_session


def send_email(subject: str,
               text: str,
               to_recipients: List[str],
               images: List[str] = None,
               files: List[str] = None,
               sender: str = None,
               raise_exceptions: bool = False,
               config: SMTPConfig = None):
    with get_session() as session:
        message = EmailMessage(
            to_recipients=', '.join(to_recipients),
            subject=subject,
            text=text,
            files=', '.join(files) if files is not None else None
        )
        session.add(message)
        session.commit()

        # Config getting
        try:
            config: SMTPConfig = session.query(SMTPConfig).order_by(SMTPConfig.id.desc()).first() if config is None else config

            if config.default_sender is None and sender is None:
                raise RuntimeError('Sender not specified (in function args and config)')

            if sender is None:
                sender = config.default_sender
        except Exception as e:
            message.payload = {
                'failure': {
                    'step': 'config getting',
                    'message': str(e)
                },
            }
            message.status = EmailMessage.Status.FAILURE
            session.add(message)
            session.commit()
            if raise_exceptions:
                raise
            else:
                return message

        # Server initialization
        try:
            if config.use_ssl:
                server = smtplib.SMTP_SSL(config.host, config.port)
            else:
                server = smtplib.SMTP(config.host, config.port)

            if config.use_ehlo:
                server.ehlo()

            if config.use_tls:
                server.starttls()
        except Exception as e:
            message.payload = {
                'failure': {
                    'step': 'server initialization',
                    'message': str(e)
                },
            }
            message.status = EmailMessage.Status.FAILURE
            session.add(message)
            session.commit()
            if raise_exceptions:
                raise
            else:
                return message

        # Login
        try:
            server.login(config.user, config.password)
        except Exception as e:
            message.payload = {
                'failure': {
                    'step': 'login',
                    'message': str(e)
                },
            }
            message.status = EmailMessage.Status.FAILURE
            session.add(message)
            session.commit()
            if raise_exceptions:
                raise
            else:
                return message

        # Message composing
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ", ".join(to_recipients)

            # Attach text
            text_msg = MIMEText(text)
            msg.attach(text_msg)

            # Attach images
            if images is not None:
                for image in images:
                    with open(image, 'rb') as image_obj:
                        image_part = MIMEImage(
                            image_obj.read()
                        )
                        msg.attach(image_part)

            # Attach files
            if files is not None:
                for file in files:
                    with open(file, 'rb') as file_obj:
                        file_part = MIMEApplication(
                            file_obj.read()
                        )
                        file_part.add_header('Content-Disposition', f'attachment; filename="{os.path.split(file)[-1]}"')
                        msg.attach(file_part)
        except Exception as e:
            message.payload = {
                'failure': {
                    'step': 'message composing',
                    'message': str(e)
                },
            }
            message.status = EmailMessage.Status.FAILURE
            session.add(message)
            session.commit()
            if raise_exceptions:
                raise
            else:
                return message

        # Message sending
        try:
            server.sendmail(sender, to_recipients, msg.as_string())
        except Exception as e:
            message.payload = {
                'failure': {
                    'step': 'message sending',
                    'message': str(e)
                },
            }
            message.status = EmailMessage.Status.FAILURE
            session.add(message)
            session.commit()
            if raise_exceptions:
                raise
            else:
                return message

        message.status = EmailMessage.Status.SUCCESS
        session.add(message)
        session.commit()
        return message
