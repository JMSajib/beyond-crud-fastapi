from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.reviews.schemas import ReviewCreateModel

user_service = UserService()
book_service = BookService()


class ReviewService:

    async def get_review_for_user(self, book_uid: str, session: AsyncSession):
        statement = select(Review).filter(Review.book_uid == book_uid)
        result = await session.exec(statement)
        review = result.first()
        return review if review else None

    async def create_review(
        self, email: str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession
    ):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            user = await user_service.get_user_by_email(email=email, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='Book not found'
                )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
                )
            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)
            new_review.user = user
            new_review.book = book
            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e
            )
