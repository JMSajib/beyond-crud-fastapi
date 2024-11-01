from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user, get_session
from src.db.models import User
from src.reviews.schemas import ReviewCreateModel, ReviewModel
from src.reviews.service import ReviewService
from src.auth.dependencies import RoleChecker


review_router = APIRouter()
review_service = ReviewService()

admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await review_service.get_all_reviews(session=session)
    return reviews


@review_router.get("/{review_uid}", dependencies=[user_role_checker])
async def get_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    review = await review_service.get_review_by_uid(review_uid=review_uid, session=session)
    return review


@review_router.get("/book/{book_uid}", response_model=ReviewModel, status_code=status.HTTP_200_OK)
async def get_review_for_user(book_uid: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    book_review = await review_service.get_review_for_user(book_uid=book_uid, session=session)
    return book_review


@review_router.post("/book/{book_uid}", response_model=ReviewModel)
async def create_review_for_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.create_review(
        email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session
    )
    return new_review


@review_router.delete(
    "/{review_uid}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await review_service.delete_review_to_from_book(
        review_uid=review_uid, user_email=current_user.email, session=session
    )

    return None
