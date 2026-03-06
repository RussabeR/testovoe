from typing import Sequence, TypeVar, Generic, Type, Optional
from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import NoResultFound, IntegrityError
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

from src.exceptions.exceptions import (
    ObjectNotFoundException,
    ObjectExistYet,
)

M = TypeVar("M", bound=DeclarativeBase)  # SQLAlchemy Model


class BaseRepository(Generic[M]):
    model: Type[M]

    def __init__(self, session):
        self.session = session

    async def add(self, data: BaseModel) -> M:
        try:
            model_data = data.model_dump()
            model = self.model(**model_data)

            self.session.add(model)

            await self.session.flush()
            return model

        except IntegrityError as e:
            error_str = str(e).lower()
            if "unique" in error_str or "duplicate" in error_str:
                raise ObjectExistYet from e
            raise

    async def get_filtered(self, *filter, skip: int = 0, limit: int = 100, **filter_by):
        query = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def edit(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by
    ) -> Optional[M]:
        values_to_update = data.model_dump(exclude_unset=exclude_unset)

        if not values_to_update:
            raise ValueError("No values to update")

        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**values_to_update)
            .returning(self.model)
        )

        result = await self.session.execute(update_stmt)

        updated_obj = result.scalar_one_or_none()

        return updated_obj

    async def delete(self, **filter_by) -> None:
        stmt = (
            delete(self.model)
            .filter_by(**filter_by)
            .returning(self.model.id)  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        deleted_obj = result.scalar()
        if not deleted_obj:
            raise ObjectNotFoundException

    async def get_one_or_none(self, id: int) -> Optional[M]:

        query = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]

        result = await self.session.execute(query)
        model = result.scalars().first()

        if not model:
            return None

        return model

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException

        return model

    async def add_bulk(self, data: Sequence[BaseModel]):
        add_data_stmt = (
            insert(self.model)
            .values([item.model_dump() for item in data])
            .returning(self.model)
        )
        result = await self.session.execute(add_data_stmt)
        return result.scalars().all()

    async def exists(self, **filters) -> bool:
        stmt = select(self.model).filter_by(**filters).limit(1)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return row is not None
