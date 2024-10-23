import pytest

from leveluplife.models.user import Tribe


@pytest.mark.asyncio
def test_tribe_descriptions():
    assert Tribe.NOSFERATI.description == (
        "The Nosferati are a tribe of nocturnal beings who thrive in the shadows. Known for their agility and cunning, they possess a mysterious "
        "allure and a penchant for the dark arts. Their homeland is a gothic realm of eternal night, filled with ancient castles and dark forests."
    )
    assert Tribe.VALHARS.description == (
        "The Valhars are a tribe of mighty warriors and seafarers from the frozen north. They are renowned for their strength, bravery, and indomitable "
        "spirit. Living in a rugged landscape of snow-capped mountains and fjords, they honor their ancestors through epic sagas and battles."
    )
    assert Tribe.SAHARANS.description == (
        "The Saharans hail from a vast desert land of golden sands and ancient cities. They are known for their intelligence, wisdom, and mastery of "
        "mystical arts. Their culture is rich with tales of legendary heroes, enchanted oases, and hidden treasures."
    )
    assert Tribe.GLIMMERKINS.description == (
        "The Glimmerkins are a tribe of ingenious and whimsical beings who inhabit lush, enchanted forests and underground burrows. They are "
        "celebrated for their inventiveness, agility, and cheerful disposition. Their society thrives on creativity, clockwork inventions, "
        "and the magic of nature."
    )
    assert Tribe.NEUTRALS.description == (
        "The Neutrals are those who have chosen not to align themselves with any particular tribe. They are versatile and independent individuals who "
        "prefer to forge their own path. While they do not possess the specific traits of the tribes, they benefit from a balanced set of attributes "
        "and the freedom to adapt to any situation."
    )
