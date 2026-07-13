from pydantic import BaseModel, field_validator


class User(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def root(cls, name: str) -> str:
        if name and all(char.isalpha() or char == " " for char in name):
            return name
        else:
            raise ValueError("Name must contain only letters and spaces")