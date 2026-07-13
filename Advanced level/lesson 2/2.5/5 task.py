from pydantic import BaseModel, Field


class Product(BaseModel):
    product_name: str = Field(alias="name")
    product_price: float = Field(alias="price")


product = Product(
    name="not Bob",
    price=300.5,
)

result = product.model_dump(by_alias=True)