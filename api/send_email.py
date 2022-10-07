import os
import sys

import logging
from dotenv import find_dotenv, load_dotenv

from fastapi.exceptions import HTTPException

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv(find_dotenv())


class Email:
    def __init__(self):
        self.setup()

    def setup(self) -> bool:
        """
        :return: True if connected to the MongoDB, Error otherwise
        """
        try:
            self.client = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))

            logging.info("Connected to SendGrid. Setup has completed.")

            return True

        except Exception as e:
            logging.error(e)
            return e

    def send_email(self, email: str, subject: str, content: str):
        """
        :param email: the email to send to
        :param subject: the subject of the email
        :param content: the content of the email
        :return: True if email was sent, Error otherwise
        """
        try:
            message = Mail(
                from_email='contact@yeklabs.com',
                to_emails=f'{email}',
                subject=f'{subject}',
                html_content=f'{content}')
            response = self.client.send(message)

            logging.info("Email method was called.")

            return HTTPException(status_code=200, detail="Email sent successfully.")

        except Exception as e:
            logging.error(e.message)

            return HTTPException(status_code=response.status_code, detail={
                "message": "Email was not sent.",
                "error": e.message
            })
