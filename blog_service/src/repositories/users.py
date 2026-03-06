from src.models import UsersOrm
from src.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    model = UsersOrm
    pass
