import bcrypt
from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schemas.user import UserCreate
from src.db.core import get_async_session
from src.db.tables import UserTable
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import EntityAlreadyExistsException


class RegisterService:

    def __init__(self, session: AsyncSession):
        self.__session = session


    @staticmethod
    def _hash_password(password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        return hashed_password

    async def create_user(self, user_data: UserCreate):

        hashed_password = self._hash_password(user_data.password)

        stmt = (
            insert(UserTable)
            .values(
                email=user_data.email,
                password_hash=hashed_password
            )
            .returning(UserTable)
        )

        try:
            result = await self.__session.execute(stmt)
            await self.__session.commit()
            user = result.scalar_one()
            return user
        except IntegrityError:
            raise EntityAlreadyExistsException(message=ErrorMessages.USER_ALREADY_EXISTS)
        except Exception as e:
            raise e


async def get_register_service(
    session: AsyncSession = Depends(get_async_session)
) -> RegisterService:
    return RegisterService(session=session)