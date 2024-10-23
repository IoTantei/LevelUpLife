from leveluplife.models.shared import DBModel


class Token(DBModel):
    access_token: str
    token_type: str


class TokenData(DBModel):
    username: str | None = None
