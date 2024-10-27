from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.schemas import UserCreateModel, UserModel, UserLoginModel
from src.auth.service import UserService
from src.auth.utils import create_access_token, verify_password

auth_router = APIRouter()

user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with email already exist.")
    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None and verify_password(password, user.password_hash):
        access_token = create_access_token(
            user_data={
                'email': user.email,
                'user_uid': str(user.uid)
            }
        )
        refresh_token = create_access_token(
            user_data={
                'email': user.email,
                'user_uid': str(user.uid)
            },
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
        )
        return JSONResponse(
            content={
                "message": "Login Successful",
                "access_tooken": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "email": user.email,
                    "user_uid": str(user.uid)
                }
            }
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or Password")