from datetime import time


from pawpal_system import DayOfWeek, Frequency, Owner, Pet, Priority, Task




def test_mark_complete_sets_completed_true():
    owner = Owner(name="Test Owner")
    pet = Pet(name="Fido", breed="Mutt", weight=10.0, age=3, owner=owner)
    task = Task(
    name="Walk",
    description="Quick walk",
    days=[DayOfWeek.MONDAY],
    start_time=time(7, 0),
    duration_minutes=15,
    frequency=Frequency.DAILY,
    priority=Priority.HIGH,
    pet=pet,
    )


    assert task.completed is False


    task.mark_complete()


    assert task.completed is True




def test_add_task_increases_pet_task_count():
    owner = Owner(name="Test Owner")
    pet = Pet(name="Fido", breed="Mutt", weight=10.0, age=3, owner=owner)
    task = Task(
    name="Walk",
    description="Quick walk",
    days=[DayOfWeek.MONDAY],
    start_time=time(7, 0),
    duration_minutes=15,
    frequency=Frequency.DAILY,
    priority=Priority.HIGH,
    pet=pet,
    )


    assert len(pet.tasks) == 0


    pet.add_task(task)


    assert len(pet.tasks) == 1
