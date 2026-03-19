# app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import List

from app.database import SessionLocal
from app.models import User
from app.schemas import UserCreate, UserResponse

# Configuración JWT y hashing
SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

router = APIRouter(prefix="/users", tags=["Users"])

# ------------------------
# Dependencias
# ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return current_user

# ------------------------
# Endpoints
# ------------------------

# Registro de usuario
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrecta")
    token_data = {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# Ver perfil actual
@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

# Listar todos los usuarios (solo admin)
@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    return db.query(User).all()

# Obtener usuario por id (solo admin)
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Actualizar usuario (solo admin)
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.email = user_data.email
    user.password = pwd_context.hash(user_data.password)
    db.commit()
    db.refresh(user)
    return user

# Eliminar usuario (solo admin)
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"detail": "Usuario eliminado"}
