from pydantic import BaseModel, EmailStr, Field

# 🟢 Esquema para crear o actualizar usuario
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

# 🟢 Esquema de respuesta al cliente
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True  # Pydantic V2 (antes era orm_mode=True)
        