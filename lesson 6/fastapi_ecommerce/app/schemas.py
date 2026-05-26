from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal


class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Category name (3-50 chars)"
    )
    parent_id: int | None = Field(
        None,
        description="Parent ID if exists"
    )


class Category(BaseModel):
    id: int = Field(
        ...,
        description="Uniq category ID"
    )
    name: str = Field(
        ...,
        description="Category name"
    )
    parent_id: int | None = Field(
        None,
        description="Parent ID if exists"
    )
    is_active: bool = Field(
        ...,
        description=""
    )

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Product name (3-100 chars)"
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Description (max 500 chars)"
    )
    price: Decimal = Field(
        ...,
        gt=0,
        description="Product price (> 0)"
    )
    image_url: str | None = Field(
        None,
        max_length=200,
        description="Image URL"
    )
    stock: int = Field(
        ...,
        ge=0,
        description="Count of product (>= 0)"
    )
    category_id: int = Field(
        ...,
        description="Category ID"
    )


class Product(BaseModel):
    id: int = Field(
        ...,
        description="ID"
    )
    name: str = Field(
        ...,
        description="Product name"
    )
    description: str | None = Field(
        None,
        description="Description"
    )
    price: Decimal = Field(
        ...,
        description="Price in rubs",
        gt=0,
        decimal_places=2
    )
    image_url: str | None = Field(
        None,
        description="URL"
    )
    stock: int = Field(
        ...,
        description="Count of product"
    )
    category_id: int = Field(
        ...,
        description="ID"
    )
    is_active: bool = Field(
        ...,
        description=""
    )

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr = Field(description="User email")
    password: str = Field(min_length=8, description="Password (min 8 chars)")
    role: str = Field(default="buyer", pattern="^(buyer|seller)$", description="Role: 'buyer' or 'seller'")