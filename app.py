from datetime import time

import pandas as pd
import streamlit as st

from diagrams.pawpal_system import (
    DayOfWeek,
    Frequency,
    Owner,
    Pet,
    Priority,
    SchedulePlanner,
    Task,
)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

planner = SchedulePlanner()


def numbered_table(rows):
    """Builds a table with a 1-based row number as its index, for st.table."""
    table = pd.DataFrame(rows)
    table.index = range(1, len(table) + 1)
    return table


if "owner" not in st.session_state:
    st.session_state.owner = None
if "schedule_result" not in st.session_state:
    st.session_state.schedule_result = None

st.title("PawPal+")
st.caption("Pet care planning")

owner = st.session_state.owner
owner_tab, tasks_tab, plan_tab = st.tabs(["Owner & pets", "Care tasks", "Daily plan"])

with owner_tab:
    st.subheader("Owner")
    with st.form("owner_form"):
        owner_name = st.text_input("Owner name", value=owner.name if owner else "")
        available_days = st.multiselect(
            "Days available",
            options=list(DayOfWeek),
            default=list(owner.availability) if owner and owner.availability else list(DayOfWeek),
            format_func=lambda day: day.value,
        )
        available_minutes = st.number_input(
            "Available minutes per selected day",
            min_value=0,
            max_value=720,
            value=max(owner.availability.values(), default=120) if owner else 120,
            step=15,
        )
        preferences_text = st.text_input(
            "Care preferences (comma-separated)",
            value=", ".join(owner.preferences) if owner else "",
        )
        save_owner = st.form_submit_button("Save owner")

    if save_owner:
        clean_name = owner_name.strip()
        if not clean_name:
            st.warning("Enter an owner name.")
        elif not available_days:
            st.warning("Choose at least one day of availability.")
        else:
            availability = {day: int(available_minutes) for day in available_days}
            preferences = [item.strip() for item in preferences_text.split(",") if item.strip()]
            if owner is None:
                owner = Owner(clean_name, availability=availability, preferences=preferences)
                st.session_state.owner = owner
                st.session_state.schedule_result = None
                st.success(f"Created owner: {owner.name}")
            else:
                owner.name = clean_name
                owner.update_availability(availability)
                owner.set_preferences(preferences)
                st.success(f"Updated owner: {owner.name}")

    owner = st.session_state.owner
    if owner is not None:
        st.divider()
        st.subheader("Pets")
        with st.form("pet_form", clear_on_submit=True):
            pet_name = st.text_input("Pet name")
            breed = st.text_input("Breed")
            weight = st.number_input("Weight (kg)", min_value=0.1, max_value=200.0, value=10.0, step=0.1)
            age = st.number_input("Age (years)", min_value=0, max_value=40, value=3, step=1)
            add_pet = st.form_submit_button("Add pet")

        if add_pet:
            clean_pet_name = pet_name.strip()
            existing_pet = next(
                (pet for pet in owner.pets if pet.name.casefold() == clean_pet_name.casefold()),
                None,
            )
            if not clean_pet_name or not breed.strip():
                st.warning("Enter both a pet name and breed.")
            elif existing_pet is not None:
                st.info(f"{existing_pet.name} is already in this owner’s pet list.")
            else:
                pet = Pet(
                    name=clean_pet_name,
                    breed=breed.strip(),
                    weight=float(weight),
                    age=int(age),
                    owner=owner,
                )
                owner.add_pet(pet)
                st.session_state.schedule_result = None
                st.success(f"Added {pet.name}.")

        if owner.pets:
            st.dataframe(
                [
                    {"Pet": pet.name, "Breed": pet.breed, "Weight (kg)": pet.weight, "Age": pet.age}
                    for pet in owner.pets
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("Add a pet to start entering care tasks.")
    else:
        st.info("Save an owner before adding pets.")

with tasks_tab:
    st.subheader("Care tasks")
    owner = st.session_state.owner
    if owner is None or not owner.pets:
        st.info("Save an owner and add a pet before creating tasks.")
    else:
        with st.form("task_form", clear_on_submit=True):
            selected_pet = st.selectbox(
                "Pet",
                options=owner.pets,
                format_func=lambda pet: pet.name,
            )
            task_name = st.text_input("Task name", placeholder="Morning walk")
            description = st.text_input("Description", placeholder="Walk around the neighborhood")
            task_days = st.multiselect(
                "Scheduled days",
                options=list(DayOfWeek),
                default=[DayOfWeek.MONDAY],
                format_func=lambda day: day.value,
            )
            task_time = st.time_input("Start time", value=time(7, 0))
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=720, value=30, step=5)
            frequency = st.selectbox(
                "Frequency",
                options=list(Frequency),
                format_func=lambda item: item.value,
            )
            priority = st.selectbox(
                "Priority",
                options=list(Priority),
                format_func=lambda item: item.name.title(),
            )
            add_task = st.form_submit_button("Add care task")

        if add_task:
            clean_task_name = task_name.strip()
            if not clean_task_name:
                st.warning("Enter a task name.")
            elif not task_days:
                st.warning("Choose at least one scheduled day.")
            else:
                task = Task(
                    name=clean_task_name,
                    description=description.strip(),
                    days=task_days,
                    start_time=task_time,
                    duration_minutes=int(duration),
                    frequency=frequency,
                    priority=priority,
                    pet=selected_pet,
                )
                selected_pet.add_task(task)
                st.session_state.schedule_result = None
                st.success(f"Added {task.name} for {selected_pet.name}.")

        st.divider()
        if not owner.tasks:
            st.info("No care tasks have been added yet.")
        else:
            conflicts = planner.detect_conflicts(owner.pending_tasks)
            if conflicts:
                st.warning(
                    f"{len(conflicts)} scheduling conflict(s) found. "
                    "Move one of the tasks to a different time."
                )
                for message in conflicts:
                    st.warning(message.removeprefix("Warning: "), icon="⚠️")
            else:
                st.success("No scheduling conflicts among pending tasks.")

            pending_options = planner.sort_by_time(planner.filter_by_completion(owner.tasks, completed=False))
            if pending_options:
                task_to_complete = st.selectbox(
                    "Mark a task complete",
                    options=pending_options,
                    format_func=lambda task: (
                        f"{task.name} ({task.pet.name}, {task.start_time:%H:%M}, "
                        f"{', '.join(day.value for day in task.days)})"
                    ),
                )
                if st.button("Mark complete"):
                    next_task = task_to_complete.mark_complete()
                    st.session_state.schedule_result = None
                    if next_task is not None:
                        st.success(
                            f"Completed {task_to_complete.name}. Next occurrence created for "
                            f"{next_task.due_date:%A, %b %d}."
                        )
                    else:
                        st.success(f"Completed {task_to_complete.name}.")

            st.subheader("All tasks")
            filter_cols = st.columns(3)
            with filter_cols[0]:
                pet_filter = st.selectbox(
                    "Pet",
                    options=["All pets"] + [pet.name for pet in owner.pets],
                    key="task_pet_filter",
                )
            with filter_cols[1]:
                status_filter = st.selectbox(
                    "Status",
                    options=["All", "Pending", "Complete"],
                    key="task_status_filter",
                )
            with filter_cols[2]:
                sort_choice = st.selectbox(
                    "Sort by",
                    options=["Start time", "Priority"],
                    key="task_sort",
                )

            visible_tasks = owner.tasks
            if pet_filter != "All pets":
                visible_tasks = [task for task in visible_tasks if task.pet.name == pet_filter]
            if status_filter != "All":
                visible_tasks = planner.filter_by_completion(
                    visible_tasks, completed=(status_filter == "Complete")
                )
            if sort_choice == "Start time":
                visible_tasks = planner.sort_by_time(visible_tasks)
            else:
                visible_tasks = planner.sort_by_priority(visible_tasks)

            if visible_tasks:
                st.caption(f"Showing {len(visible_tasks)} of {len(owner.tasks)} tasks, sorted by {sort_choice.lower()}.")
                st.table(
                    numbered_table(
                        [
                            {
                                "Pet": task.pet.name,
                                "Task": task.name,
                                "Days": ", ".join(day.value for day in task.days),
                                "Time": task.start_time.strftime("%I:%M %p").lstrip("0"),
                                "Duration (min)": task.duration_minutes,
                                "Priority": task.priority.name.title(),
                                "Status": "Complete" if task.completed else "Pending",
                            }
                            for task in visible_tasks
                        ]
                    )
                )
            else:
                st.info("No tasks match these filters.")

with plan_tab:
    st.subheader("Daily plan")
    owner = st.session_state.owner
    if owner is None or not owner.pets:
        st.info("Save an owner and add a pet before building a plan.")
    else:
        day_options = list(DayOfWeek)
        selected_day = st.selectbox(
            "Plan for",
            options=day_options,
            format_func=lambda day: day.value,
        )
        owner_minutes = owner.availability.get(selected_day, 0)
        plan_limit = st.number_input(
            "Minutes to schedule",
            min_value=0,
            max_value=720,
            value=owner_minutes,
            step=15,
            help="The plan will not exceed the owner's availability for this day.",
        )
        selected_plan_pet = st.selectbox(
            "Plan for pet",
            options=owner.pets,
            format_func=lambda pet: pet.name,
            key="plan_pet",
        )

        if st.button("Generate daily plan", type="primary"):
            if owner_minutes <= 0:
                st.session_state.schedule_result = None
                st.warning(f"No owner availability is set for {selected_day.value}.")
            else:
                eligible_tasks = [
                    task
                    for task in selected_plan_pet.pending_tasks
                    if selected_day in task.days and task.duration_minutes <= owner_minutes
                ]
                candidates = planner.sort_by_priority(eligible_tasks)
                budget = min(int(plan_limit), owner_minutes)
                remaining_minutes = budget
                plan = []
                for task in candidates:
                    if task.duration_minutes <= remaining_minutes:
                        plan.append(task)
                        remaining_minutes -= task.duration_minutes
                st.session_state.schedule_result = {
                    "pet_name": selected_plan_pet.name,
                    "day": selected_day,
                    "plan": planner.sort_by_time(plan),
                    "skipped": [task for task in candidates if task not in plan],
                    "budget": budget,
                    "conflicts": planner.detect_conflicts(plan),
                }

        result = st.session_state.schedule_result
        if result is not None:
            st.divider()
            st.markdown(f"**{result['pet_name']} · {result['day'].value}**")
            if result["plan"]:
                used_minutes = sum(task.duration_minutes for task in result["plan"])
                st.success(
                    f"Scheduled {len(result['plan'])} task(s) using {used_minutes} of "
                    f"{result['budget']} available minutes."
                )
                for message in result["conflicts"]:
                    st.warning(message.removeprefix("Warning: "), icon="⚠️")
                st.table(
                    numbered_table(
                        [
                            {
                                "Time": task.start_time.strftime("%I:%M %p").lstrip("0"),
                                "Care task": task.name,
                                "Duration (min)": task.duration_minutes,
                                "Priority": task.priority.name.title(),
                            }
                            for task in result["plan"]
                        ]
                    )
                )
                if result["skipped"]:
                    st.warning(
                        "Not enough time for: "
                        + ", ".join(f"{task.name} ({task.duration_minutes} min)" for task in result["skipped"])
                    )
            else:
                st.info("No pending tasks for this pet fit the selected day and time limit.")
