from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenPayload(BaseModel):
    sub: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str