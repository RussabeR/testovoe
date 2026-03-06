from pydantic import BaseModel


class UserOUT(BaseModel):
    user_id: int
    username: str
    email: str
