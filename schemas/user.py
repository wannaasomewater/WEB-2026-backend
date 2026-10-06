from pydantic import BaseModel, ConfigDict


class UserRegisterSchema(BaseModel):
    username: str
    full_name: str
    password: str


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: str
