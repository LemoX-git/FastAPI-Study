from pydantic import BaseModel
from typing import Optional


class Employee(BaseModel):
    name: str
    role: str


class Company(BaseModel):
    company_name: str
    manager: Optional['Employee'] = None
