from pydantic import BaseModel

class AddProductAtCart(BaseModel):
    id: int
    count: int