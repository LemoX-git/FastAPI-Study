from pydantic import BaseModel, EmailStr, HttpUrl, PositiveInt

class Message(BaseModel):
    id: int
    content: str


message = Message(id=1, content="Hello, World!")
print(message.model_dump_json(indent=2))
print(message.model_dump())


class User(BaseModel):
    email: EmailStr
    website: HttpUrl
    age: PositiveInt


class Author(BaseModel):
    name: str
    email: EmailStr


class Message(BaseModel):
    id: int
    content: str
    author: Author  # Вложенная модель