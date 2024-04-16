import json

from fastapi import FastAPI, HTTPException
from models import Composer, Piece


with open("composers.json", "r") as f:
    composers_list: list[dict] = json.load(f)

with open("pieces.json", "r") as f:
    piece_list: list[dict] = json.load(f)


app = FastAPI()

composers: list[Composer] = []
pieces: list[Piece] = []

for person in composers_list:
    composers.append(Composer(**person))

for music in piece_list:
    pieces.append(Piece(**music))


@app.get("/composers")
async def list_composers() -> list[Composer]:
    return composers


@app.get("/pieses")
async def list_pieces() -> list[Piece]:
    return pieces


@app.post("/composers")
async def create_composer(person: Composer) -> None:
    if any(exisiting_composer.name == person.name for exisiting_composer in composers):
        raise HTTPException(
            status_code=400, detail="Composer ID already exists")
    composers.append(person)
    return "Composer added successfully"


@app.post("/pieces")
async def create_piece(music: Piece) -> None:
    if any(existing_piece.name == music.name for existing_piece in pieces):
        raise HTTPException(
            status_code=400, detail="Piece name already exists")
    pieces.append(music)


@app.put("/composers/{composer_id}")
async def update_composer(composer_id: int, updated_composer: Composer) -> None:
    if any(existing_composer.composer_id == updated_composer.composer_id for existing_composer in composers):
        for i, composer in enumerate(composers):
            if composer.composer_id == composer_id:
                composers[i] = updated_composer
                return "Composer updated successfully"
    return "No composer exists with that ID"


@app.put("/pieces/{piece_name}")
async def update_piece(piece_name: str, updated_piece: Piece) -> None:
    if any(existing_piece.name == updated_piece.name for existing_piece in pieces):
        for i, piece in enumerate(pieces):
            if piece.name == piece_name:
                pieces[i] = updated_piece
                return "Piece updated successfully"
    return "No piece exists with that name"


@app.delete("/composers/{composer_id}")
async def delete_composer(composer_id: int) -> None:
    for i, person in enumerate(composers):
        if person.composer_id == composer_id:
            composers.pop(i)
            return "Composer deleted successfully"
    return "No composer exists with that ID"


@app.delete("/piece/{piece_name}")
async def delete_piece(piece_name: str) -> None:
    for i, piece in enumerate(pieces):
        if piece.name == piece_name:
            pieces.pop(i)
            return "Piece deleted successfully"
    return "No piece exists with that name"
