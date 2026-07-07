from pydantic import BaseModel

class ProductV2(BaseModel):
    product_id: str
    product_name: str
    current_price: float
    currency: str
    description: str = None