from .base import BaseConfig
from typing import ClassVar, List
import os
from dotenv import load_dotenv
from pydantic import Field

load_dotenv(override=True)

class DevConfig(BaseConfig):
    DATABASE_URL: str = os.getenv("DB_DEV_URI")
    # DATABASE_URL: str = Field(..., alias="DB_URI_DEV")
    # JWT_SECRET: str = os.getenv("JWT_SECRET")
    # Use ClassVar to indicate these are not Pydantic model fields
    # ALGORITHM: ClassVar[str] = "HS512"
    # ACCESS_TOKEN_EXPIRE_MINUTES: ClassVar[int] = 30
    # SECRET_KEY: str = os.getenv("KEY_SECRET")
    # SECRET_KEY: str = Field(..., alias="KEY_SECRET")

    # Define allowed origins
    origins: ClassVar[List[str]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
