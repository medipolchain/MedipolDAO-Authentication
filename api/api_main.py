import os
import sys
import logging

from send_email import Email
from db_wrapper import DbWrapper

import pydantic
from bson.objectid import ObjectId
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

app = FastAPI()
email_wrapper = Email()
db = DbWrapper()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    :return: a welcoming screen
    :return:
    """
    try:
        return "MedipolDAO API by @yeklabs"

    except Exception as e:
        logging.error(e)
        return HTTPException(status_code=500, detail={
            "message": "Something went wrong.",
            "error": e
        })


@app.post("/send_email")
async def send_email(req: Request):
    """
    :param request: the request object
    :return: True if email was sent, Error otherwise
    """
    try:
        data = await req.json()

        email = data["email"]
        subject = data["subject"]
        content = data["content"]

        return email_wrapper.send_email(email, subject, content)

    except Exception as e:
        logging.error(e)
        return HTTPException(status_code=500, detail={
            "message": "Something went wrong.",
            "error": e
        })


@app.post("/get_otp_magic_link")
async def get_otp(req: Request):
    """
    :param request: the request object
    :return: True if email was sent, Error otherwise
    """
    try:
        data = await req.json()

        email = data["email"]

        return db.get_otp_magic_link(email)

    except Exception as e:
        logging.error(e)
        return HTTPException(status_code=500, detail={
            "message": "Something went wrong.",
            "error": e
        })


@app.post("/register_user_otp")
async def register_user(req: Request):
    """
    :param request: the request object
    :return: True if email was sent, Error otherwise
    """
    try:
        data = await req.json()

        email = data["email"]
        otp = data["otp"]

        return db.register_user_otp(
            email,
            otp
        )

    except Exception as e:
        logging.error(e)
        return HTTPException(status_code=500, detail={
            "message": "Something went wrong.",
            "error": e
        })


@app.post("/verify/{magic_link}")
async def verify_magic_link(magic_link: str):
    """
    :param magic_link: the magic link to verify
    :return: True if email was sent, Error otherwise
    """
    try:
        return db.register_user_magic_link(magic_link)

    except Exception as e:
        logging.error(e)
        return HTTPException(status_code=500, detail={
            "message": "Something went wrong.",
            "error": e
        })
