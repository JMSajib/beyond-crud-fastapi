from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from src.auth.schemas import UserCreateModel, UserLoginModel, UserModel
from src.auth.service import UserService
from src.auth.utils import create_access_token, verify_password
from src.db.main import get_session
from src.db.redis import add_jti_to_blacklist

auth_router = APIRouter()

user_service = UserService()
refresh_token = RefreshTokenBearer()

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with email already exist.",
        )
    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None and verify_password(password, user.password_hash):
        access_token = create_access_token(
            user_data={'email': user.email, 'user_uid': str(user.uid)}
        )
        refresh_token = create_access_token(
            user_data={'email': user.email, 'user_uid': str(user.uid)},
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
        )
        return JSONResponse(
            content={
                "message": "Login Successful",
                "access_tooken": access_token,
                "refresh_token": refresh_token,
                "user": {"email": user.email, "user_uid": str(user.uid)},
            }
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or Password"
    )


@auth_router.get("/refresh_token")
async def refresh_token(token_details: dict = Depends(refresh_token)):
    expiry_time = token_details.get('exp')
    if datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_access_token(user_data=token_details.get('user'))
        return JSONResponse(content={"access_token": new_access_token})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    )


@auth_router.get("/me")
async def get_current_user(user = Depends(get_current_user)):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details.get('jti')
    await add_jti_to_blacklist(jti)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {
            "message": "Logout Successful"
        }
    )