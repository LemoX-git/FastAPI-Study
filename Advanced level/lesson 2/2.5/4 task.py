from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    password: str


user = User(
    name="Bob",
    email="example@email.com",
    password="secret_pass",
)

result = user.model_dump_json(exclude="password")