from enum import Enum

from pydantic import EmailStr
from sqlmodel import AutoString, Field

from leveluplife.models.shared import DBModel


class Tribe(str, Enum):
    NOSFERATI: str = "Nosferati"
    VALHARS: str = "Valhars"
    SAHARANS: str = "Saharans"
    GLIMMERKINS: str = "Glimmerkins"
    NEUTRALS: str = "Neutrals"

    @property
    def description(self) -> str:
        descriptions = {
            "Nosferati": "The Nosferati are a tribe of nocturnal beings who thrive in the shadows. Known for their agility and cunning, they possess a mysterious "
            "allure and a penchant for the dark arts. Their homeland is a gothic realm of eternal night, filled with ancient castles and dark forests.",
            "Valhars": "The Valhars are a tribe of mighty warriors and seafarers from the frozen north. They are renowned for their strength, bravery, and indomitable "
            "spirit. Living in a rugged landscape of snow-capped mountains and fjords, they honor their ancestors through epic sagas and battles.",
            "Saharans": "The Saharans hail from a vast desert land of golden sands and ancient cities. They are known for their intelligence, wisdom, and mastery of "
            "mystical arts. Their culture is rich with tales of legendary heroes, enchanted oases, and hidden treasures.",
            "Glimmerkins": "The Glimmerkins are a tribe of ingenious and whimsical beings who inhabit lush, enchanted forests and underground burrows. They are "
            "celebrated for their inventiveness, agility, and cheerful disposition. Their society thrives on creativity, clockwork inventions, "
            "and the magic of nature.",
            "Neutrals": "The Neutrals are those who have chosen not to align themselves with any particular tribe. They are versatile and independent individuals who "
            "prefer to forge their own path. While they do not possess the specific traits of the tribes, they benefit from a balanced set of attributes "
            "and the freedom to adapt to any situation.",
        }
        return descriptions[self.value]


class UserBase(DBModel):
    username: str = Field(
        default=None, index=True, min_length=3, max_length=18, unique=True
    )
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
    tribe: Tribe
    biography: str | None = Field(default=None, max_length=500)
    profile_picture: str | None = Field(default=None, max_length=500)
    background_image: str | None = Field(default=None, max_length=500)


class UserCreate(UserBase):
    password: str


class UserUpdate(DBModel):
    username: str | None = None
    email: EmailStr | None = None
    strength: int | None = None
    intelligence: int | None = None
    agility: int | None = None
    wise: int | None = None
    psycho: int | None = None
    experience: int | None = None
    tribe: Tribe | None = None
    biography: str | None = None
    profile_picture: str | None = None
    background_image: str | None = None


class UserUpdatePassword(DBModel):
    password: str
