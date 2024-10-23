import pytest

from leveluplife.models.reaction import ReactionType


@pytest.mark.asyncio
async def test_reaction_type_description():
    assert ReactionType.LIKE.description == "The user likes the task"
    assert ReactionType.DISLIKE.description == "The user dislikes the task"
    assert ReactionType.SAD.description == "The user is sad about the task"
    assert ReactionType.HAPPY.description == "The user is happy about the task"
    assert ReactionType.CRAZY.description == "The user is crazy about the task"
    assert ReactionType.LAUGHING.description == "The user is laughing about the task"
    assert ReactionType.INLOVE.description == "The user is in love with the task"
    assert ReactionType.DISAPPOINTING.description == (
        "The user is disappointed about the task"
    )
