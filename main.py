from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from jose import jwt, JWTError

from database import db_users
from src.models import user_helper
from src.schemas import UserCreate, UserOut, Token
from src.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM


app = FastAPI(title="User Microservice")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Utility: get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = db_users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)


@app.get("/")
def read_root():
    return {"message": "User Microservice is Running!"}


# Register
@app.post("/register", response_model=UserOut)
def register(user: UserCreate):
    if db_users.find_one({"username": user.username}):
        return JSONResponse(status_code=400, content={"details": "Username already exists"})

    new_user = {
        "username": user.username,
        "full_name": user.full_name,
        "password_hash": hash_password(user.password),
        "join_date": datetime.utcnow(),
        "cash_balance": 100_000.0,   # default starting balance
        "holdings": {},              # empty dict initially
    }
    result = db_users.insert_one(new_user)
    created_user = db_users.find_one({"_id": result.inserted_id})
    return user_helper(created_user)


# Login
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db_users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


# Protected route
@app.get("/me", response_model=UserOut)
def read_me(current_user=Depends(get_current_user)):
    return current_user