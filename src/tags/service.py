import logging

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select

from src.books.service import BookService
from src.db.models import Tag
from src.tags.schemas import TagAddModel, TagCreateModel

book_service = BookService()

server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong"
)


class TagService:

    async def get_tags(self, session: AsyncSession):
        try:
            statement = select(Tag).order_by(desc(Tag.created_at))
            result = await session.exec(statement)
            return result.all()
        except Exception as e:
            logging.error(e)
            server_error

    async def get_tag_by_id(self, tag_uid: str, session: AsyncSession):
        try:
            statement = select(Tag).where(Tag.uid == tag_uid)
            result = await session.exec(statement)
            return result.first()
        except Exception as e:
            logging.error(e)
            server_error

    async def add_tags_to_book(
        self, book_uid: str, tag_data: TagAddModel, session: AsyncSession
    ):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
                )

            for tag_item in tag_data.tags:
                result = await session.exec(
                    select(Tag).where(Tag.name == tag_item.name)
                )
                tag = result.one_or_none()
                if not tag:
                    tag = Tag(name=tag_item.name)
                book.tags.append(tag)

            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book
        except Exception as e:
            logging.error(e)
            server_error

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        try:
            statement = select(Tag).where(Tag.name == tag_data.name)
            result = await session.exec(statement)
            tag = result.first()
            if tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exist"
                )
            new_tag = Tag(name=tag_data.name)
            session.add(new_tag)
            await session.commit()
            return new_tag
        except Exception as e:
            logging(e)
            server_error

    async def update_tag(
        self, tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession
    ):
        try:
            tag = await self.get_tag_by_id(tag_uid, session)
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
                )
            update_data_dict = tag_update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(tag, k, v)

                await session.commit()

                await session.refresh(tag)

            return tag
        except Exception as e:
            logging.error(e)
            server_error

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        try:
            tag = await self.get_tag_by_id(tag_uid, session)
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
                )
            await session.delete(tag)
            await session.commit()
        except Exception as e:
            logging.error(e)
            server_error
