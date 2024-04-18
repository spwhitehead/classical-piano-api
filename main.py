import json
import logging
import os

from contextlib import asynccontextmanager
from decouple import Config, RepositoryEnv
from fastapi import FastAPI, HTTPException, Depends
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
    try:
        yield
    finally:
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


def get_session():
    with Session(engine) as session:
        yield session


async def shutdown_logic():
    engine.dispose()
    logging.info("Database connections closed.")


app = FastAPI(lifespan=lifespan)


@app.get("/composers")
async def list_composers():
    with Session(engine) as session:
        result = session.exec(
            select(Composer).order_by(Composer.composer_id)).all()
        return result


@app.get("/pieces")
async def list_pieces():
    with Session(engine) as session:
        result = session.exec(select(Piece).order_by(Piece.composer_id)).all()
        return result


@app.post("/composers")
async def create_composer(person: Composer, session: Session = Depends(get_session)) -> str:
    # Check if a composer with the same name already exists
    existing_composer = session.exec(
        select(Composer).where(Composer.composer_id == person.composer_id)).first()
    if existing_composer:
        raise HTTPException(
            status_code=400, detail="Composer with this name already exists")

    # Add the new composer to the database if they don't already exist
    session.add(person)
    session.commit()
    session.refresh(person)
    return f"Composer {person.name} added successfully with ID {person.composer_id}"


@app.post("/pieces")
async def create_piece(music: Piece, session: Session = Depends(get_session)) -> str:
    existing_piece = session.exec(
        select(Piece).where(Piece.name == music.name)).first()
    if existing_piece:
        raise HTTPException(
            status_code=400, detail="Piece with this name already exists")

    session.add(music)
    session.commit()
    session.refresh(music)
    return f"Piece {music.name} added successfully. Composer's ID is {music.composer_id}"


@app.put("/composers/{composer_id}")
async def update_composer(composer_id: int, updated_composer: Composer, session: Session = Depends(get_session)) -> str:
    existing_composer = session.exec(select(Composer).where(
        Composer.composer_id == composer_id)).first()
    if existing_composer:
        session.delete(existing_composer)
        session.add(updated_composer)
        session.commit()
        session.refresh(updated_composer)
        return f"Composer {updated_composer.name} updated successfully"

    session.add(updated_composer)
    session.commit()
    return f"No Composer with ID {composer_id} currently in database. Added {updated_composer.name} with ID {updated_composer.composer_id} successfully"


@app.put("/pieces/{piece_name}")
async def update_piece(piece_name: str, updated_piece: Piece, session: Session = Depends(get_session)) -> str:
    existing_piece = session.exec(
        select(Piece).where(Piece.name == piece_name)).first()
    if existing_piece:
        session.delete(existing_piece)
        session.add(updated_piece)
        session.commit()
        session.refresh(updated_piece)
        return f"Piece {updated_piece.name} updated successfully"

    session.add(updated_piece)
    session.commit()
    return f"No Piece with name {piece_name} currently in database. Added {updated_piece.name} successfully"


@app.delete("/composers/{composer_id}")
async def delete_composer(composer_id: int, session: Session = Depends(get_session)) -> str:
    existing_composer = session.exec(select(Composer).where(
        Composer.composer_id == composer_id)).first()
    if existing_composer:
        session.delete(existing_composer)
        session.commit()
        return f"Composer {existing_composer.name} deleted successfully"

    raise HTTPException(
        status_code=400, detail=f"No composer existis with ID {composer_id}")


@app.delete("/piece/{piece_name}")
async def delete_piece(piece_name: str, session: Session = Depends(get_session)) -> str:
    existing_piece = session.exec(
        select(Piece).where(Piece.name == piece_name)).first()
    if existing_piece:
        session.delete(existing_piece)
        session.commit()
        return f"Piece {existing_piece.name} deleted successfully"

    raise HTTPException(
        status_code=400, detail=f"No piece exists with name {piece_name}")
