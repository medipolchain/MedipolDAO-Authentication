from datetime import datetime
import random
import string

import logging
import os
from datetime import datetime, timedelta, timezone

from send_email import Email
from sendgrid.helpers.mail import Mail

import jwt
from dotenv import find_dotenv, load_dotenv
from eth_account.messages import encode_defunct
from fastapi.exceptions import HTTPException
from pymongo import MongoClient

load_dotenv(find_dotenv())

email_wrapper = Email()


class DbWrapper:
    def __init__(self):
        self.setup()

    def setup(self) -> bool:
        """
        :return: True if connected to the MongoDB, Error otherwise
        """
        try:
            self.connection_string = os.environ.get("MONGODB_PWD")
            self.client = MongoClient(self.connection_string)
            self.university_aliases = ["@std.medipol.edu.tr", "@st.medipol.edu.tr", "@yeklabs.com"]
            self.magic_link = string.ascii_letters + string.digits
            self.website_domain = "https://medipoldao.com"

            logging.info("Connected to MongoDB. Setup has completed.")

            return True

        except Exception as e:
            logging.error(e)
            return HTTPException(status_code=400, detail=e)

    def get_database_names(self):
        """
        :return: a list of all the database names
        """
        try:
            dbs = self.client.list_database_names()

            logging.info("Database names method was called.")

            return dbs

        except Exception as e:
            logging.error(e)
            return HTTPException(status_code=400, detail=e)

    def get_database(self, db_name: str):
        """
        :param db_name: the name of the database to get
        :return: the database object
        """
        try:
            db = self.client[db_name]

            logging.info("Database method was called.")

            return db

        except Exception as e:
            logging.error(e)
            return HTTPException(status_code=400, detail=e)

    def get_collections_names(self, db_name: str):
        """
        :param db_name: the name of the database to get the collections from
        :return: a list of all the collections in the database
        """
        try:
            db = self.get_database(db_name)
            collections = db.list_collection_names()

            logging.info("Collections names method was called.")

            return collections

        except Exception as e:
            logging.error(e)
            return HTTPException(status_code=400, detail=e)

    def get_collection(self, collection_name: str):
        """
        :param db_name: the name of the database to get the collection from
        :param collection_name: the name of the collection to get
        :return: the collection object
        """
        try:
            db = self.get_database("users")
            collection = db[collection_name]

            logging.info("Collection method was called.")

            return collection

        except Exception as e:
            logging.error(e)
            return HTTPException(status_code=400, detail=e)

    def get_otp_magic_link(self, email: str):
        """
        :param email: the email of the user to register
        :return: True if the user was registered, Error otherwise
        """
        try:

            logging.info("Register user method was called.")

            for i in self.university_aliases:
                if i in email:
                    collection = self.get_collection("users-unverified")
                    otp = random.randint(100000, 999999)
                    magic_link = self.generate_magic_link()

                    collection.insert_one({
                        "email": email,
                        "otp": otp,
                        "magic_link": f"{magic_link}",
                        "timestamp": datetime.timestamp(datetime.now())
                    })

                    subject = 'MedipolDAO Authentication Code'
                    html_content = f'''
                    <h1>Auth Code: <b>{otp}</b></h1>
                    <p>Auth Code will expire in 5 minutes.</p>
                    
                    <br>
                    
                    <h1><a href="{self.website_domain}/verify/{magic_link}">Click here</a> to 
                    automatically verify your account</h1>
                    <a href="{self.website_domain}/verify/{magic_link}">{self.website_domain}/verify/{magic_link}</a>
                    '''

                    email_wrapper.send_email(
                        email=email,
                        subject=subject,
                        content=html_content
                    )

                    logging.info("OTP method was called.")
                    logging.info("Email method was called.")

                    return otp

            return HTTPException(
                status_code=400,
                detail="Email is not a valid university email."
            )

        except Exception as e:
            logging.error(e)
            return HTTPException(
                status_code=400,
                detail=e
            )

    def register_user_otp(self, email: str, otp: int):
        """
        :param email: the email of the user to register
        :param otp: the otp of the user to register
        :return: True if the user was registered, Error otherwise
        """
        try:
            unverified_collection = self.get_collection("users-unverified")
            verified_collection = self.get_collection("users-verified")

            user = unverified_collection.find_one({
                "email": email,
                "otp": otp
            })

            if user is not None:
                if datetime.timestamp(datetime.now()) - user["timestamp"] < 300:
                    unverified_collection.delete_one({
                        "email": email,
                        "otp": otp
                    })

                    logging.info("Register user method was called.")

                    unverified_collection.delete_one({
                        "email": email,
                        "otp": otp
                    })

                    logging.info("User was removed from unverified collection.")

                    verified_collection.insert_one({
                        "email": email
                    })

                    logging.info("User was added to verified collection.")

                    return HTTPException(
                        status_code=200,
                        detail="User was registered."
                    )

                return HTTPException(
                    status_code=400,
                    detail="OTP has expired."
                )

            return HTTPException(
                status_code=400,
                detail="OTP is not valid."
            )

        except Exception as e:
            logging.error(e)
            return HTTPException(
                status_code=400,
                detail=e
            )

    def register_user_magic_link(self, magic_link: str):
        """
        :param magic_link: the magic link of the user to register
        :return: True if the user was registered, Error otherwise
        """
        try:
            unverified_collection = self.get_collection("users-unverified")
            verified_collection = self.get_collection("users-verified")

            user = unverified_collection.find_one({
                "magic_link": magic_link
            })

            if user is not None:
                if datetime.timestamp(datetime.now()) - user["timestamp"] < 300:
                    unverified_collection.delete_one({
                        "magic_link": magic_link
                    })

                    logging.info("Register user method was called.")

                    unverified_collection.delete_one({
                        "magic_link": magic_link
                    })

                    logging.info("User was removed from unverified collection.")

                    verified_collection.insert_one({
                        "email": user["email"]
                    })

                    logging.info("User was added to verified collection.")

                    return HTTPException(
                        status_code=200,
                        detail="User was registered."
                    )

                return HTTPException(
                    status_code=400,
                    detail="Magic link has expired."
                )

            return HTTPException(
                status_code=400,
                detail="Magic link is not valid."
            )

        except Exception as e:
            logging.error(e)
            return HTTPException(
                status_code=400,
                detail=e
            )

    def generate_magic_link(self):
        """
        :return: a random string of 256 characters
        """
        try:
            magic_link = ''.join(random.choices(self.magic_link, k=256))

            logging.info("Magic link method was called.")

            return magic_link

        except Exception as e:
            logging.error(e)
            return HTTPException(
                status_code=400,
                detail=e
            )
