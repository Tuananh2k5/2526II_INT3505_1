from fastapi import FastAPI, Query, HTTPException, status, Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI(
    title="Library Management System API",
    description="API cho hệ thống quản lý thư viện, chuẩn REST.",
    version="1.0.0"
)

# --- Data Models ---
class Book(BaseModel):
    id: int
    title: str
    author: str
    category: str
    published_year: int

class User(BaseModel):
    id: int
    name: str
    email: str

class BorrowRecord(BaseModel):
    id: int
    book_id: int
    user_id: int
    borrow_date: date
    return_date: Optional[date] = None

class BorrowRequest(BaseModel):
    book_id: int

# --- Mock Database ---
books_db = [
    Book(id=i, title=f"Sách {i}", author=f"Tác giả {i%5 + 1}", category="Tiểu thuyết" if i%2 == 0 else "Khoa học", published_year=2000 + (i%20))
    for i in range(1, 101)
]

users_db = [
    User(id=i, name=f"Người dùng {i}", email=f"user{i}@example.com")
    for i in range(1, 11)
]

borrows_db = []

# --- Books Endpoints ---

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book: Book):
    if any(b.id == book.id for b in books_db):
        raise HTTPException(status_code=400, detail="Sách đã tồn tại (trùng ID)")
    books_db.append(book)
    return book

@app.get("/books", response_model=dict, tags=["Books"])
def get_books(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm theo tên sách hoặc tên tác giả"),
    page: Optional[int] = Query(None, ge=1, description="Trang hiện tại (Page-based)"),
    size: Optional[int] = Query(10, gt=0, le=100, description="Kích thước trang"),
    offset: Optional[int] = Query(None, ge=0, description="Vị trí bắt đầu (Offset/Limit)"),
    limit: Optional[int] = Query(None, gt=0, le=100, description="Giới hạn số lượng (Offset/Limit)"),
    cursor: Optional[int] = Query(None, description="ID của sách làm điểm bắt đầu (Cursor-based)")
):
    results = books_db

    # 1. Tìm kiếm
    if q:
        results = [b for b in results if q.lower() in b.title.lower() or q.lower() in b.author.lower()]

    # 2. Phân trang (Ưu tiên: Cursor > Page > Offset)
    if cursor is not None:
        start_index = 0
        for i, b in enumerate(results):
            if b.id == cursor:
                # Bắt đầu lấy từ phần tử NGAY SAU cursor
                start_index = i + 1
                break
        
        lim = limit if limit else size
        paginated = results[start_index : start_index + lim]
        next_cursor = paginated[-1].id if paginated else None
        
        return {
            "strategy": "cursor",
            "data": paginated,
            "next_cursor": next_cursor
        }
        
    elif page is not None:
        start = (page - 1) * size
        end = start + size
        total_items = len(results)
        return {
            "strategy": "page",
            "page": page,
            "size": size,
            "total_items": total_items,
            "total_pages": (total_items + size - 1) // size,
            "data": results[start:end]
        }
        
    elif offset is not None or limit is not None:
        off = offset if offset else 0
        lim = limit if limit else size
        return {
            "strategy": "offset",
            "offset": off,
            "limit": lim,
            "data": results[off : off + lim]
        }

    # Nếu không truyền tham số phân trang, trả về toàn bộ danh sách kết quả
    return {
        "strategy": "all",
        "total_items": len(results),
        "data": results
    }

@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
def get_book(book_id: int):
    book = next((b for b in books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    return book

@app.put("/books/{book_id}", response_model=Book, tags=["Books"])
def update_book(book_id: int, updated_book: Book):
    book_index = next((index for index, b in enumerate(books_db) if b.id == book_id), None)
    if book_index is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    
    books_db[book_index] = updated_book
    return updated_book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int):
    book_index = next((index for index, b in enumerate(books_db) if b.id == book_id), None)
    if book_index is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    
    books_db.pop(book_index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Users Endpoints ---

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: User):
    if any(u.id == user.id for u in users_db):
        raise HTTPException(status_code=400, detail="Người dùng đã tồn tại (trùng ID)")
    users_db.append(user)
    return user

@app.get("/users", response_model=List[User], tags=["Users"])
def get_users():
    return users_db

@app.get("/users/{user_id}", response_model=User, tags=["Users"])
def get_user(user_id: int):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user

@app.put("/users/{user_id}", response_model=User, tags=["Users"])
def update_user(user_id: int, updated_user: User):
    user_index = next((index for index, u in enumerate(users_db) if u.id == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    users_db[user_index] = updated_user
    return updated_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: int):
    user_index = next((index for index, u in enumerate(users_db) if u.id == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    users_db.pop(user_index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Nested Resources Endpoints ---

@app.get("/users/{user_id}/borrows", response_model=List[BorrowRecord], tags=["User Borrows"])
def get_user_borrows(user_id: int):
    if not any(u.id == user_id for u in users_db):
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return [b for b in borrows_db if b.user_id == user_id]

@app.post("/users/{user_id}/borrows", response_model=BorrowRecord, status_code=status.HTTP_201_CREATED, tags=["User Borrows"])
def create_user_borrow(user_id: int, request: BorrowRequest):
    if not any(u.id == user_id for u in users_db):
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    if not any(b.id == request.book_id for b in books_db):
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    
    new_id = len(borrows_db) + 1
    record = BorrowRecord(
        id=new_id,
        book_id=request.book_id,
        user_id=user_id,
        borrow_date=date.today()
    )
    borrows_db.append(record)
    return record
