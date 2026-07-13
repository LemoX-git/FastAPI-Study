from pydantic import BaseModel


class Profile(BaseModel):
    bio: str
    age: int


class User(BaseModel):
    name: str
    profile: Profile


user = User(
    name="Bob",
    profile=Profile(
        bio="blablabla",
        age=30,
    ),
)

result = user.model_dump()