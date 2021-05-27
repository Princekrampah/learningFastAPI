from fastapi import (FastAPI, BackgroundTasks, UploadFile, 
                    File, Form, Depends, HTTPException, status)

from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from typing import List
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
import jwt
from models import User

config_credentials = dict(dotenv_values(".env"))
conf = ConnectionConfig(
    MAIL_USERNAME = config_credentials["EMAIL"],
    MAIL_PASSWORD = config_credentials["PASS"],
    MAIL_FROM = config_credentials["EMAIL"],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)

class EmailSchema(BaseModel):
    email: List[EmailStr]

async def send_email(email : list, instance: User):

    token_data = {
        "id" : instance.id,
        "username" : instance.username
    }

    token = jwt.encode(token_data, config_credentials["SECRET"])

    template = f"""
        <h3> Account Verification </h3>
        <br>
        <p>Thanks for choosing EasyShopas, please 
        click on the link below to verify your account</p> 

        <br>
        http://localhost:8000/verification/?token={token}
        <br>

        <h5>If you did not register for EasyShopas, 
        please kindly ignore this email and nothing will happen. Thanks<h4>
        """
    message = MessageSchema(
        subject="EasyShopas Account Verification Mail",
        recipients=email,  # List of recipients, as many as you can pass 
        body=template,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message) 