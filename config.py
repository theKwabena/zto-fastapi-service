import secrets
from datetime import timedelta, datetime
from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from functools import lru_cache
from typing import Optional, Any, Dict, Union
from pydantic_settings import BaseSettings
from jose import jwt


ALGORITHM = "HS256"


class Settings(BaseSettings):
    ZIMBRA_SERVER_URL: str = "https://mail.knust.edu.gh"
    DOWNLOAD_FOLDER: str = "/home/data/mailbox-downloads"
    EXTRACTION_FOLDER: str = "/home/data/mailbox-extracts"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 60 * 8  # 8 hrs
    SECRET_KEY: str = secrets.token_urlsafe(32)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    app_settings = Settings()
    return app_settings


settings = get_settings()


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")  # changed to accept access token from httpOnly Cookie
        print("access_token is", authorization)

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "exp": expires_delta
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)
    return encoded_jwt
