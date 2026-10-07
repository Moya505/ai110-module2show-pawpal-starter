import sqlite3
from typing import Any, Dict, List, Optional


class PetCareDatabase:
    """Simple SQLite-backed persistence layer for PawPal+ models."""

    def __init__(self, db_path: str = "pawpal.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS owners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    availability TEXT,
                    preferences TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    breed TEXT,
                    weight TEXT,
                    age INTEGER,
                    owner_name TEXT NOT NULL,
                    FOREIGN KEY (owner_name) REFERENCES owners(name)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT NOT NULL,
                    description TEXT,
                    day_of_week TEXT,
                    duration_minutes INTEGER,
                    priority TEXT,
                    owner_name TEXT NOT NULL,
                    pet_name TEXT NOT NULL,
                    FOREIGN KEY (owner_name) REFERENCES owners(name),
                    FOREIGN KEY (pet_name) REFERENCES pets(name)
                )
                """
            )

    def add_owner(self, owner: Any) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO owners (name, availability, preferences) VALUES (?, ?, ?)",
                (owner.name, owner.availability, ",".join(owner.preferences)),
            )

    def add_pet(self, pet: Any) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO pets (name, breed, weight, age, owner_name) VALUES (?, ?, ?, ?, ?)",
                (pet.name, pet.breed, pet.weight, pet.age, pet.owner.name),
            )

    def add_task(self, task: Any) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks (task_name, description, day_of_week, duration_minutes, priority, owner_name, pet_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    task.name,
                    task.description,
                    task.day_of_week,
                    task.duration_minutes,
                    task.priority,
                    task.owner.name,
                    task.pet.name,
                ),
            )

    def get_owner(self, name: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT name, availability, preferences FROM owners WHERE name = ?",
                (name,),
            ).fetchone()
        if row is None:
            return None
        return {
            "name": row["name"],
            "availability": row["availability"],
            "preferences": row["preferences"].split(",") if row["preferences"] else [],
        }

    def get_pet(self, name: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT name, breed, weight, age, owner_name FROM pets WHERE name = ?",
                (name,),
            ).fetchone()
        if row is None:
            return None
        return {
            "name": row["name"],
            "breed": row["breed"],
            "weight": row["weight"],
            "age": row["age"],
            "owner_name": row["owner_name"],
        }

    def get_tasks_for_pet(self, pet_name: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT task_name, description, day_of_week, duration_minutes, priority, owner_name, pet_name FROM tasks WHERE pet_name = ?",
                (pet_name,),
            ).fetchall()
        return [
            {
                "task_name": row["task_name"],
                "description": row["description"],
                "day_of_week": row["day_of_week"],
                "duration_minutes": row["duration_minutes"],
                "priority": row["priority"],
                "owner_name": row["owner_name"],
                "pet_name": row["pet_name"],
            }
            for row in rows
        ]
