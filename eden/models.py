from pydantic import BaseModel

class Credentials(BaseModel):
    token:str