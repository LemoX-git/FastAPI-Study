from pydantic import BaseModel


class Item(BaseModel):
    item_name: str
    price: float


class Order(BaseModel):
    order_id: int
    items: list[Item]


items = [
    Item(
        item_name="one",
        price=300.5,
    ),
    Item(
        item_name="two",
        price=1000.5,
    ),
]


order = Order(
    order_id=1,
    items=items
)

result = order.model_dump_json(indent=2)