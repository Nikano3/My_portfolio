from pydantic import BaseModel, EmailStr, Field


class Registration(BaseModel):
    name: str = Field(min_length=3, description="Имя пользователя")
    email: EmailStr
    password: str = Field(min_length=6, description="Пароль")



class Login(BaseModel):
    email: EmailStr
    password: str
