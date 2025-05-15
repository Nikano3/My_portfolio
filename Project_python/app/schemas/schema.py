from pydantic import BaseModel ,EmailStr, field_validator, model_validator
from pydantic_core import PydanticCustomError



class Registration(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 6:
            raise PydanticCustomError(
                "password_too_short",  # код ошибки (любой, ты сам выбираешь)
                "Пароль должен быть не менее 6 символов"  # сообщение пользователю
            )
        return v

class Login(BaseModel):
    email: EmailStr
    password: str
