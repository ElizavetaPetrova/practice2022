from typing import List, Union
from pydantic import BaseModel
from datetime import datetime


class PriceBase(BaseModel):
    name: str
    price: str
    price_int: int


class PriceCreate(PriceBase):
    pass


class Price(PriceBase):
    id: int
    datetime: datetime

    class Config:
        orm_mode = True
