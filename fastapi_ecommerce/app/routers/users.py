from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

import jwt

from app.models.users import User as UserModel
from app.schemas import UserCreate, User as UserSchema, RefreshTokenRequest
from app.db_depends import get_async_db
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token

from app.config import SECRET_KEY, ALGORITHM


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    email_exists = (await db.scalars(select(UserModel)
                                     .where(UserModel.email == new_user.email))
                   ).first()
    
    if email_exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email alredy registred")
    
    db_user = UserModel(
        email=new_user.email,
        hashed_password=hash_password(new_user.password),
        role=new_user.role,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.email == form_data.username)
        .where(UserModel.is_active == True)
    )).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    refrash_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "refresh_token": refrash_token, "token_type": "bearer"}


@router.post("/refresh-token")
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    old_refresh_token = body.refresh_token

    try:
        paylod = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        email: str | None = paylod.get("sub")
        token_type: str | None = paylod.get("token_type")

        if email is None or token_type != "refresh":
            raise credentials_exception
        
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.email == email)
        .where(UserModel.is_active == True)
    )).first()
    if user is None:
        raise credentials_exception
    
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }