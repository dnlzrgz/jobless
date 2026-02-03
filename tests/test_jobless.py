import pytest
from faker import Faker

from jobless.app import JoblessApp

fake = Faker()


@pytest.mark.asyncio
async def test_keys():
    app = JoblessApp()
    app.settings.db_url = "sqlite:///:memory:"

    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("n")

        await pilot.press(*fake.company().split())
        await pilot.press("tab")
