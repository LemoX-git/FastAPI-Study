from pydantic import BaseModel, field_validator


class Item(BaseModel):
    item_name: str
    price: float

    @field_validator('price')
    @classmethod
    def root(cls, price: float) -> float:
        if price <= 0:
            raise ValueError("Price must be positive")
        if price > 1000:
            raise ValueError("Price must not exceed 1000")
        return price