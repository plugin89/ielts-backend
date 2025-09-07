from pydantic import BaseModel

#pydantic doesn't have Emailstr TODO: find it
class Emailstr(BaseModel):
    email: str

class User(BaseModel):
    id: int
    email: Emailstr
    name: str
