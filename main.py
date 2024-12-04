from fastapi import FastAPI, HTTPException, status,Depends
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import UserCreate, UserResponse
from crud import create_user, get_user_by_email
from auth import create_access_token, verify_password

app = FastAPI()

items = []


@app.get("/")
def read_root():
    return {"java": "Hello, World!"}


@app.post("/items")
def create_item(item: str):
    items.append(item)
    return item


@app.get("/items")
def list_items():
    return items


@app.get("/items/{item_id}")
def get_by_id(item_id: int):
    print(f"Requested item ID: {item_id}")
    print(f"Items List: {items}")

    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")

    return {"item": items[item_id-1]}

Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_user(db, user)

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
