from pydantic import BaseModel, EmailStr, field_validator

class UserRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def name_length(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Name must be at least 3 characters long")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        return v

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str