from fastapi import APIRouter, Depends, status
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker
from src.db.main import get_session

from src.books.schemas import Book
from src.tags.schemas import TagCreateModel, TagModel, TagAddModel
from src.tags.service import TagService

tag_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(['admin', 'user']))


@tag_router.get("/", response_model=List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_tags(session=session)
    return tags


@tag_router.post("/", response_model=TagModel, status_code=status.HTTP_201_CREATED, dependencies=[user_role_checker])
async def add_tag(tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:
    tag_added = await tag_service.add_tag(tag_data=tag_data, session=session)
    return tag_added


@tag_router.post(
    "/book/{book_uid}/tags", response_model=Book, dependencies=[user_role_checker]
)
async def add_tags_to_book(
    book_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_session)
) -> Book:
    print(f"*********{tag_data}*********")
    book_with_tag = await tag_service.add_tags_to_book(
        book_uid=book_uid, tag_data=tag_data, session=session
    )

    return book_with_tag



@tag_router.put("/{tag_uid}", response_model=TagModel, dependencies=[user_role_checker])
async def update_tag(tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:
    updated_tag = await tag_service.update_tag(tag_uid=tag_uid, tag_update_data=tag_update_data, session=session)
    return updated_tag

@tag_router.delete("/{tag_uid}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)) -> None:
    deleted_tag = await tag_service.delete_tag(tag_uid=tag_uid, session=session)
    return {}