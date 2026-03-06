from fastapi import APIRouter, Depends
from pydantic import PositiveInt

from src.services.posts_services import PostsService
from src.api.dependencies import DBDep, CurrentUserId, get_current_user_id, CacheDep
from src.schemas.posts_schemas import PostCreateRequest, PostEdit

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
    dependencies=[Depends(get_current_user_id)],  # эмуляция проверки доступа
)


@router.get("/all", summary="Получение всех постов пользователей с пагинацией")
async def get_all_posts(db: DBDep, skip: PositiveInt = 0, limit: PositiveInt = 20):

    return await PostsService(db).get_all_posts(skip, limit)


@router.post("", summary="Создание нового поста")
async def create_post(
    db: DBDep,
    user_id: CurrentUserId,
    data: PostCreateRequest,
    cache: CacheDep,
):

    return await PostsService(db, cache).add_post(user_id, data)


@router.get("/by_user", summary="Получение постов пользователя с кешированием")
async def get_user_posts(
    db: DBDep,
    user_id: CurrentUserId,
    cache: CacheDep,
):
    return await PostsService(db, cache).get_user_posts(user_id)


@router.get("/{post_id}", summary="Получение поста пользователя по ID с кешированием")
async def get_post(
    db: DBDep,
    post_id: PositiveInt,
    user_id: CurrentUserId,
    cache: CacheDep,
):

    return await PostsService(db, cache).get_user_post_by_id(user_id, post_id)


@router.patch("/{post_id}", summary="Частичное обновление поста пользователя")
async def update_post(
    db: DBDep,
    post_id: PositiveInt,
    post_data: PostEdit,
    current_user_id: CurrentUserId,
    cache: CacheDep,
):

    return await PostsService(db, cache).partially_edit_post(
        post_id=post_id, data=post_data, user_id=current_user_id
    )


@router.delete("/{post_id}", summary="Удаление поста пользователем")
async def delete_post(
    db: DBDep,
    post_id: PositiveInt,
    current_user_id: CurrentUserId,
    cache: CacheDep,
):

    return await PostsService(db, cache).delete_post(
        post_id=post_id, user_id=current_user_id
    )
