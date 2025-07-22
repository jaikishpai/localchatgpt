from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.services.mongo_service import create_user, verify_user, get_user
from app.services.jwt_service import create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register")
def register(request: RegisterRequest):
    if not create_user(request.username, request.password):
        raise HTTPException(status_code=400, detail="User already exists")
    return {"status": "User registered"}

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    if not verify_user(request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": request.username})
    return TokenResponse(access_token=token)

bearer_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"username": user["username"]} 