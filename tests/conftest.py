from unittest.mock import AsyncMock, patch

import aiohttp
import pytest


@pytest.fixture(scope="function")
def mock_aiohttp_session():
    async_mock_session = AsyncMock(aiohttp.ClientSession)
    with patch("aiohttp.ClientSession", return_value=async_mock_session):
        yield async_mock_session
