from pydantic import BaseModel


class Composer(BaseModel):
    name: str
    composer_id: int
    home_country: str


class Piece(BaseModel):
    name: str
    alt_name: str
    difficulty: int
    composer_id: Composer
