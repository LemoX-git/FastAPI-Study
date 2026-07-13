from typing import TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T')

class DataContainer(BaseModel, Generic[T]):
    data: T