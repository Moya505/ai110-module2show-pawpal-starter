from datetime import date, time


from pawpal_system import DayOfWeek, Frequency, Owner, Pet, Priority, SchedulePlanner, Task




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




def make_task(pet, name="Task", start=time(7, 0), frequency=Frequency.ONCE,
              day=DayOfWeek.MONDAY, due_date=None):
    kwargs = {"due_date": due_date} if due_date else {}
    task = Task(
        name=name,
        description=name,
        days=[day],
        start_time=start,
        duration_minutes=15,
        frequency=frequency,
        priority=Priority.HIGH,
        pet=pet,
        **kwargs,
    )
    pet.add_task(task)
    return task




def test_sort_by_time_returns_chronological_order():
    owner = Owner(name="Test Owner")
    pet = Pet(name="Fido", breed="Mutt", weight=10.0, age=3, owner=owner)
    evening = make_task(pet, "Evening", time(18, 30))
    early = make_task(pet, "Early", time(8, 5))
    midnight = make_task(pet, "Midnight", time(0, 0))
    late_morning = make_task(pet, "Late morning", time(10, 0))


    result = SchedulePlanner().sort_by_time(pet.tasks)


    assert result == [midnight, early, late_morning, evening]




def test_daily_task_completion_creates_next_day_task():
    owner = Owner(name="Test Owner")
    pet = Pet(name="Fido", breed="Mutt", weight=10.0, age=3, owner=owner)
    task = make_task(pet, "Walk", frequency=Frequency.DAILY, due_date=date(2026, 10, 31))


    next_task = task.mark_complete()


    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date(2026, 11, 1)
    assert next_task.days == [DayOfWeek.SUNDAY]
    assert next_task in pet.tasks
    assert len(pet.tasks) == 2




def test_non_daily_task_completion_creates_no_new_task():
    owner = Owner(name="Test Owner")
    pet = Pet(name="Fido", breed="Mutt", weight=10.0, age=3, owner=owner)
    task = make_task(pet, "Vet", frequency=Frequency.ONCE)


    assert task.mark_complete() is None
    assert len(pet.tasks) == 1




def test_detect_conflicts_flags_duplicate_times_across_pets():
    owner = Owner(name="Test Owner")
    dog = Pet(name="Fido", breed="Mutt", weight=10.0, age=3, owner=owner)
    cat = Pet(name="Tom", breed="Tabby", weight=4.0, age=2, owner=owner)
    owner.add_pet(dog)
    owner.add_pet(cat)
    make_task(dog, "Walk", time(9, 0))
    make_task(cat, "Feed", time(9, 0))
    make_task(cat, "Play", time(10, 0))


    warnings = SchedulePlanner().detect_conflicts(owner.tasks)


    assert len(warnings) == 1
    assert "09:00" in warnings[0]
    assert "Walk" in warnings[0] and "Feed" in warnings[0]




def test_detect_conflicts_returns_empty_when_times_differ():
    owner = Owner(name="Test Owner")
    pet = Pet(name="Fido", breed="Mutt", weight=10.0, age=3, owner=owner)
    make_task(pet, "Walk", time(9, 0))
    make_task(pet, "Feed", time(9, 30))
    make_task(pet, "Walk Tuesday", time(9, 0), day=DayOfWeek.TUESDAY)


    assert SchedulePlanner().detect_conflicts(pet.tasks) == []
