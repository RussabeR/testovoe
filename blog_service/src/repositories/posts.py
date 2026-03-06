from src.models import PostsOrm
from src.repositories.base import BaseRepository


class PostsRepository(BaseRepository):
    model = PostsOrm
    pass

# При необходимости в новых реализациях конкретных методов под posts


