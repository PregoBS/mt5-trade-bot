from database import Database
import os
import pytest


@pytest.fixture
def db() -> Database:
    return Database(f"{os.path.dirname(__file__)}/database.db")


def test_create_table(db: Database):
    db.create_table("Teste", """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INT NOT NULL
    """)
    table = db.get_table("Teste")
    db.drop_table("Teste")
    assert len(table) == 0


def test_insert_into_table(db: Database):
    db.create_table("Teste", """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INT NOT NULL
    """)
    db.insert_into_table("Teste", "name, age", "'Rodrigo', 25")
    db.insert_into_table("Teste", "name, age", "'Pedro', 24")
    db.insert_into_table("Teste", "name, age", "'Joao', 44")
    db.insert_into_table("Teste", "name, age", "'Brenda', 21")
    table = db.get_table("Teste")
    db.drop_table("Teste")
    assert len(table) == 4
    assert table["name"].iloc[0] == "Rodrigo"
    assert table["age"].iloc[0] == 25
    assert table["name"].iloc[1] == "Pedro"
    assert table["age"].iloc[1] == 24
    assert table["name"].iloc[2] == "Joao"
    assert table["age"].iloc[2] == 44
    assert table["name"].iloc[3] == "Brenda"
    assert table["age"].iloc[3] == 21
