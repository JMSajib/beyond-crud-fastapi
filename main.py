from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from typing import List
from pydantic import BaseModel

app = FastAPI()


books = [
    {
        "id": 1,
        "title": "Learn Python the Hard Way",
        "author": "Zed Shaw",
        "publisher": "Addison-Wesley",
        "published_date": "2017-08-15",
        "page_count": 320,
        "language": "English"
    },
    {
        "id": 2,
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "publisher": "No Starch Press",
        "published_date": "2019-05-03",
        "page_count": 544,
        "language": "English"
    },
    {
        "id": 3,
        "title": "Automate the Boring Stuff with Python",
        "author": "Al Sweigart",
        "publisher": "No Starch Press",
        "published_date": "2015-04-14",
        "page_count": 504,
        "language": "English"
    },
    {
        "id": 4,
        "title": "Fluent Python",
        "author": "Luciano Ramalho",
        "publisher": "O'Reilly Media",
        "published_date": "2015-07-30",
        "page_count": 792,
        "language": "English"
    },
    {
        "id": 5,
        "title": "Python for Data Analysis",
        "author": "Wes McKinney",
        "publisher": "O'Reilly Media",
        "published_date": "2017-10-20",
        "page_count": 550,
        "language": "English"
    }
]

class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    

class BookUpdateModel(BaseModel):
    title: str
    publisher: str
    page_count: int
    language: str


@app.get('/books', response_model=List[Book])
async def get_all_books():
    return books

@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book_data: Book) -> dict:
    new_book = book_data.model_dump()
    books.append(new_book)
    return new_book

@app.get("/book/{book_id}")
async def get_book(book_id: int) -> dict:
    for book in books:
        if book.get('id') == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    

@app.patch("/book/{book_id}")
async def update_book(book_id: int, book_update_date: BookUpdateModel) -> dict:
    for book in books:
        if book.get('id') == book_id:
            book['title'] = book_update_date.title
            book['publisher'] = book_update_date.publisher
            book['page_count'] = book_update_date.page_count
            book['language'] = book_update_date.language
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@app.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book.get("id") == book_id:
            books.remove(book)
            return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

