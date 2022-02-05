from pydantic import BaseModel


class Credentials(BaseModel):
    token: str


class WaitFor(BaseModel):
    seconds: int = 5
