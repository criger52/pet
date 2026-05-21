from typing import Callable

import pytest

from src.api.schemas.user import LoginRequest
from src.exceptions.user import LoginFailedException
from src.services.login import LoginService


async def test__login_service__credentials__invalid(
        login_service: LoginService,
) -> None:
    credentials = LoginRequest(email="unknown@example.com", password="wrong_password")

    with pytest.raises(LoginFailedException):
        await login_service.login(credentials)


async def test__login_service__password__invalid(
        login_service: LoginService,
        create_user_table: Callable,
) -> None:
    user = await create_user_table(email="test@example.com")
    credentials = LoginRequest(email=user.email, password="wrong_password")

    with pytest.raises(LoginFailedException):
        await login_service.login(credentials)
