from pawpal.database import PetCareDatabase
from pawpal.models import Owner, Pet, Task, SchedulePlanner


def test_owner_pet_task_relationships():
    owner = Owner(name="Jordan", availability="Weekdays after 5pm", preferences=["gentle walks", "medication reminders"])
    pet = Pet(name="Mochi", breed="Golden Retriever", weight="30kg", age=3, owner=owner)
    task = Task(
        name="Morning walk",
        description="30 minute walk",
        day_of_week="Monday",
        duration_minutes=30,
        priority="high",
        owner=owner,
        pet=pet,
    )

    pet.add_task(task)
    owner.add_pet(pet)

    assert owner.name == "Jordan"
    assert pet.owner.name == "Jordan"
    assert task.pet.name == "Mochi"
    assert len(pet.task_history) == 1


def test_schedule_planner_sorts_tasks_by_priority():
    owner = Owner(name="Jordan", availability="Weekdays after 5pm", preferences=[])
    pet = Pet(name="Mochi", breed="Golden Retriever", weight="30kg", age=3, owner=owner)

    low_task = Task("Feeding", "Dinner feed", "Monday", 10, "low", owner, pet)
    high_task = Task("Medication", "Daily meds", "Monday", 5, "high", owner, pet)

    planner = SchedulePlanner()
    planned = planner.sort_by_priority([low_task, high_task])

    assert planned[0].priority == "high"
    assert planned[1].priority == "low"


def test_database_can_store_and_load_entities(tmp_path):
    db = PetCareDatabase(db_path=str(tmp_path / "pawpal.db"))

    owner = Owner(name="Jordan", availability="Weekdays after 5pm", preferences=["gentle walks"])
    pet = Pet(name="Mochi", breed="Golden Retriever", weight="30kg", age=3, owner=owner)
    task = Task("Morning walk", "Walk outside", "Monday", 30, "high", owner, pet)

    db.add_owner(owner)
    db.add_pet(pet)
    db.add_task(task)

    loaded_owner = db.get_owner("Jordan")
    loaded_pet = db.get_pet("Mochi")
    loaded_tasks = db.get_tasks_for_pet("Mochi")

    assert loaded_owner["name"] == "Jordan"
    assert loaded_pet["name"] == "Mochi"
    assert len(loaded_tasks) == 1
    assert loaded_tasks[0]["task_name"] == "Morning walk"
