from datetime import date, time


from pawpal_system import (
DayOfWeek,
Frequency,
Owner,
Pet,
Priority,
SchedulePlanner,
Task,
)




def build_today_schedule() -> None:
    today = DayOfWeek(date.today().strftime("%A"))


    owner = Owner(
    name="Jamoya",
    availability={today: 180},
    preferences=["morning walks", "no tasks after 8pm"],
    )


    NichiBear = Pet(name="NichiBear", breed="Great Dane and Labrador mix", weight=50.5, age=7, owner=owner)
    Gertrude = Pet(name="Gertrude", breed="Tabby Cat", weight=4.2, age=2, owner=owner)
    owner.add_pet(NichiBear)
    owner.add_pet(Gertrude)


    morning_walk = Task(
    name="Morning Walk",
    description="Walk NichiBear around the block",
    days=[today],
    start_time=time(9, 30),
    duration_minutes=30,
    frequency=Frequency.DAILY,
    priority=Priority.HIGH,
    pet=NichiBear,
    )
    feed_Gertrude = Task(
    name="Feed Gertrude",
    description="Morning feeding",
    days=[today],
    start_time=time(6, 30),
    duration_minutes=45,
    frequency=Frequency.DAILY,
    priority=Priority.HIGH,
    pet=Gertrude,
    )
    vet_checkup = Task(
    name="Vet Checkup",
    description="Annual checkup for Rex",
    days=[today],
    start_time=time(6, 30),
    duration_minutes=45,
    frequency=Frequency.ONCE,
    priority=Priority.HIGH,
    pet=NichiBear,
    )


    NichiBear.add_task(morning_walk)
    Gertrude.add_task(feed_Gertrude)
    NichiBear.add_task(vet_checkup)


    planner = SchedulePlanner()


    todays_tasks = [task for task in owner.tasks if task.is_recurring_on(today)]
    pending = planner.sort_by_time(planner.filter_by_completion(todays_tasks, completed=False))


    print("Today's Schedule")
    print(planner.explain_plan(pending))


    for warning in planner.detect_conflicts(pending):
        print(warning)


    # Completing a daily task creates tomorrow's instance automatically.
    next_feeding = feed_Gertrude.mark_complete()
    print(f"\nCompleted: {[t.name for t in planner.filter_by_completion(owner.tasks, completed=True)]}")
    if next_feeding:
        print(f"Next occurrence created: {next_feeding.name} on {next_feeding.due_date} ({next_feeding.days[0].value})")




if __name__ == "__main__":
    build_today_schedule()
