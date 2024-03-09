from typing import Optional

from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str


class User(BaseModel):
    username : str
    auth_token : Optional[str] = None

class LoginUser(BaseModel):
    username : str

class Token(BaseModel):
    access_token: str
    token_type: str