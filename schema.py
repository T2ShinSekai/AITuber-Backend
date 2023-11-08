from pydantic import BaseModel

class Message(BaseModel):
    # user_name: str
    message: str
