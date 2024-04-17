import json
import logging
import os

from contextlib import asynccontextmanager
from decouple import Config, RepositoryEnv
from fastapi import FastAPI, HTTPException
from models import Composer, Piece
from sqlmodel import SQLModel, select, Session, create_engine

logging.basicConfig(level=logging.INFO)

base_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(base_dir, 'migrations', '.env')
config = Config(RepositoryEnv(env_file))

DATABASE_URL = config("DATABASE_URL")

engine = create_engine(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    await check_and_load_initial_data()
    yield
    await shutdown_logic()


async def check_and_load_initial_data():
    with Session(engine) as session:
        exisiting_composer = session.exec(select(Composer)).first()
        if not exisiting_composer:
            await load_initial_data_from_json()


async def load_initial_data_from_json():
    with open("composers.json", "r") as f:
        composers_list: list[dict] = json.load(f)

    with open("pieces.json", "r") as f:
        piece_list: list[dict] = json.load(f)

    with Session(engine) as session:
        for composer_data in composers_list:
            composer = Composer(**composer_data)
            session.add(composer)
        for piece_data in piece_list:
            piece = Piece(**piece_data)
            session.add(piece)
        session.commit()


@asynccontextmanager
async def shutdown_logic():
    engine.dispose()
    logging.info("Database connections closed.")
    logging.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/composers")
async def list_composers():
    with Session(engine) as session:
        result = session.exec(select(Composer)).all()
        return result


@app.get("/pieces")
async def list_pieces():
    with Session(engine) as session:
        result = session.exec(select(Piece)).all()
        return result
"""
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
    elif any(existing_composer.composer_id == music.composer_id for existing_composer in composers):
        pieces.append(music)
    raise HTTPException(
        status_code=400, detail="No composer with that ID exists.")


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
    if not any(existing_composer.composer_id == updated_piece.composer_id for existing_composer in composers):
        raise HTTPException(
            status_code=400, detail="Composer ID does not exist")
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
"""
