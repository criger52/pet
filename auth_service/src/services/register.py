import logging

import bcrypt
from dishka import FromDishka
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.user import UserCreate
from src.broker.producer import KafkaProducer
from src.db.tables import UserTable
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import EntityAlreadyExistsException


logger = logging.getLogger(__name__)


class RegisterService:

    def __init__(self, session: FromDishka[AsyncSession], kafka_producer: FromDishka[KafkaProducer]):
        self.__session = session
        self.kafka_producer = kafka_producer


    @staticmethod
    def hash_password(password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        return hashed_password

    async def create_user(self, user_data: UserCreate):

        hashed_password = self.hash_password(user_data.password)

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

            await self.kafka_producer.send_event(
                topic="user.created",
                key=str(user.id),
                value={
                    "user_id": str(user.id),
                    "email": user.email,
                },
            )

            return user
        except IntegrityError as e:
            raise EntityAlreadyExistsException(message=ErrorMessages.USER_ALREADY_EXISTS) from e
        except Exception as e:
            logger.error(e)
            raise e
