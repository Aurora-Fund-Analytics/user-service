from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId

from database import users_collection
from models import user_helper
from schemas import UserCreate, UserOut, Token
from auth import hash_password, verify_password, create_access_token

app = FastAPI(title="User Microservice")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Utility: get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    from auth import SECRET_KEY, ALGORITHM
    from jose import jwt, JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)


# Register
@app.post("/register", response_model=UserOut)
def register(user: UserCreate):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = {
        "username": user.username,
        "full_name": user.full_name,
        "password_hash": hash_password(user.password),
        "join_date": datetime.utcnow(),
    }
    result = users_collection.insert_one(new_user)
    created_user = users_collection.find_one({"_id": result.inserted_id})
    return user_helper(created_user)


# Login
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


# Protected route
@app.get("/me", response_model=UserOut)
def read_me(current_user=Depends(get_current_user)):
    return current_user