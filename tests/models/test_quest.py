import pytest

from leveluplife.models.quest import Type


@pytest.mark.asyncio
async def test_type_duration():
    assert Type.WEEKLY.duration == 7
    assert Type.DAILY.duration == 1
    assert Type.MONTHLY.duration == 30
    assert Type.YEARLY.duration == 365
    assert Type.LOVER.duration == 10
