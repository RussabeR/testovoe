from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator, PositiveInt


class PostBase(BaseModel):
    id: int
    user_id: int
    title: str
    content: str


class PostCreateRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Заголовок поста (от 3 до 100 символов)",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=250,
        description="Содержание поста (до 250 символов)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Мой первый пост", "content": "Это пример содержания поста"},
                {"title": "Еще один пост", "content": "Другой пример содержания"},
            ]
        }
    )


class PostAdd(PostCreateRequest):
    user_id: int


class PostOUT(PostBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class PostEdit(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=250)

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "PostEdit":
        if self.title is None and self.content is None:
            raise ValueError("At least one field (title or content) must be provided")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Обновленный заголовок",
                "content": "Обновленное содержание поста",
            }
        }
    }



class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0, description="Количество пропущенных записей")
    limit: PositiveInt = Field(default=20, le=100, description="Размер страницы (макс. 100)")

    class Config:
        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 20
            }
        }


