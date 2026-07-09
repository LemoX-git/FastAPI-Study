from pydantic import BaseModel


class Profile(BaseModel):
    bio: str = ""
    avatar_url: str | None = None


class User(BaseModel):
    name: str
    profile: 'Profile'
