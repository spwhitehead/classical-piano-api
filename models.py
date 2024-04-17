from sqlmodel import SQLModel, Field
from typing import Optional

metadata = SQLModel.metadata


class Composer(SQLModel, table=True):
    composer_id: int = Field(
        default=None, primary_key=True)
    name: str
    home_country: str


class Piece(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    alt_name: Optional[str] = None
    difficulty: int
    composer_id: int = Field(foreign_key="composer.composer_id")
