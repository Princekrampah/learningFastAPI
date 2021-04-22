from fastapi import (FastAPI, BackgroundTasks, UploadFile, 
                    File, Form, Depends, HTTPException, status)
from tortoise.contrib.fastapi import register_tortoise
from models import (User, Business, Product, user_pydantic, user_pydanticIn, 
                    product_pydantic,product_pydanticIn, business_pydantic, 
                    business_pydanticIn)
from tortoise.signals import post_delete, post_save, pre_delete, pre_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from passlib.context import CryptContext
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
import os
from dotenv import dotenv_values


from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
import jwt



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

app = FastAPI()



# password helper functions
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# authorization configs
oath2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

async def authenticate_user(username: str, password: str):
    user = await User.get(username = username)

    if user  and verify_password(password, user.password):
        return user

    return False

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials['SECRET'], algorithms = ['HS256'])
        user = await User.get(id = payload.get('id'))
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password"
        )

    return user

async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password"
        )

    token_data = {
        "id" : user.id,
        "username" : user.username
    }

    token = jwt.encode(token_data, config_credentials["SECRET"])
    return token

@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"status" : "ok", "data" : {"token" : token}}



# send email functionality
class EmailSchema(BaseModel):
    email: List[EmailStr]

async def simple_send(email : list, instance: User):

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
        


# process signals here
@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]) -> None:
    
    if created:
        business_obj = await Business.create(
                business_name = instance.username, owner = instance)
        await business_pydantic.from_tortoise_orm(business_obj)
        # send email functionality
        await simple_send([instance.email], instance)


@app.post('/registration')
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset = True)
    user_info['password'] = get_password_hash(user_info['password'])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
 

    return {"status" : "ok", 
            "data" : 
                f"Hello {new_user.username} thanks for choosing our services, you can now login to your account"}




@app.get('/verification')
async def email_verification(token: str):
    user = await verify_token(token)
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return {"username" : user.is_verified}
    raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid or expired token"
        )
# this route is for the swagger UI
@app.post('/verification')
async def email_verification(token: str):
    user = await verify_token(token)
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return {"username" : user.is_verified}
    raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid or expired token"
        )


register_tortoise(
    app,
    db_url='sqlite://database.sqlite3',
    modules={'models': ['models']},
    generate_schemas = True,
    add_exception_handlers = True
)