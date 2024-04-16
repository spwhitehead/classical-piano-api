import json

from fastapi import FastAPI
from models import Composer, Piece


with open("composers.json", "r") as f:
    composers_list: list[dict] = json.load(f)

with open("pieces.json", "r") as f:
    piece_list: list[dict] = json.load(f)


app = FastAPI()


@app.get("/composers")
async def list_composers() -> list[Composer]:
    pass


@app.get("/pieses")
async def list_pieces() -> list[Piece]:
    pass


@app.post("/composers")
async def create_composer() -> Composer:
    pass


@app.post("/pieces")
async def create_piece() -> Piece:
    pass


@app.put("/composers/{composer_id}")
async def update_composer() -> Composer:
    pass


@app.put("/pieces/{piece_name}")
async def update_piece() -> Piece:
    pass


@app.delete("/composers/{composer_id}")
async def delete_composer() -> None:
    pass


@app.delete("/piece/{piece_name}")
async def delete_piece() -> None:
    pass
