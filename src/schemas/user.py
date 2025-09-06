from pydantic import BaseModel, Emailstr

class User(BaseModel):
    id: int
    email: Emailstr
    name: str