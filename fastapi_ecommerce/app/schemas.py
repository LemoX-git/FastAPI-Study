from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from datetime import datetime


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
    rating: float | None = Field(
        None,
        description="Average rating"
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


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ReviewCreate(BaseModel):
    product_id: int = Field(..., description="")
    comment: str | None = Field(None, description="")
    grade: int = Field(..., ge=0, le=5, description="")


class Review(BaseModel):
    id: int = Field(..., description="ID")
    user_id: int = Field(..., description="")
    product_id: int = Field(..., description="")
    comment: str | None = Field(None)
    comment_date: datetime = Field(...)
    grade: int = Field(..., ge=0, le=5)
    is_active: bool = Field(..., description="")

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    items: list[Product] = Field(description="Products for currnet page")
    total: int = Field(ge=0, description="Total stock")
    page: int = Field(ge=1, description="Number current page")
    page_size: int = Field(ge=1, description="Count of elements on page")

    model_config = ConfigDict(from_attributes=True)


class CartItemBase(BaseModel):
    product_id: int = Field(description="ID товара")
    quantity: int = Field(ge=1, description="Количество товара")


class CartItemCreate(CartItemBase):
    """Модель для добавления нового товара в корзину."""
    pass


class CartItemUpdate(BaseModel):
    """Модель для обновления количества товара в корзине."""
    quantity: int = Field(..., ge=1, description="Новое количество товара")


class CartItem(BaseModel):
    """Товар в корзине с данными продукта."""
    id: int = Field(..., description="ID позиции корзины")
    quantity: int = Field(..., ge=1, description="Количество товара")
    product: Product = Field(..., description="Информация о товаре")

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """Полная информация о корзине пользователя."""
    user_id: int = Field(..., description="ID пользователя")
    items: list[CartItem] = Field(default_factory=list, description="Содержимое корзины")
    total_quantity: int = Field(..., ge=0, description="Общее количество товаров")
    total_price: Decimal = Field(..., ge=0, description="Общая стоимость товаров")

    model_config = ConfigDict(from_attributes=True)


class OrderItem(BaseModel):
    id: int = Field(..., description="ID позиции заказа")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")
    unit_price: Decimal = Field(..., ge=0, description="Цена за единицу на момент покупки")
    total_price: Decimal = Field(..., ge=0, description="Сумма по позиции")
    product: Product | None = Field(None, description="Полная информация о товаре")

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    id: int = Field(..., description="ID заказа")
    user_id: int = Field(..., description="ID пользователя")
    status: str = Field(..., description="Текущий статус заказа")
    total_amount: Decimal = Field(..., ge=0, description="Общая стоимость")
    created_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    items: list[OrderItem] = Field(default_factory=list, description="Список позиций")

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    items: list[Order] = Field(..., description="Заказы на текущей странице")
    total: int = Field(ge=0, description="Общее количество заказов")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")

    model_config = ConfigDict(from_attributes=True)