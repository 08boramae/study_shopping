from os.path import basename

from pydantic import BaseModel

class AddProductAtCart(BaseModel):
    product_id: int
    count: int

class Login(BaseModel):
    id: str
    password: str

class Signup(BaseModel):
    name: str
    id: str
    password: str