# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
---------Output of Main.py------------------
Today's Schedule
Today's plan (85 minutes total):
- [HIGH] Morning Walk at 07:00:00 (30 min)
- [HIGH] Feed Gertrude at 08:00:00 (10 min)
- [HIGH] Vet Checkup at 14:30:00 (45 min)

## 🧪 Testing PawPal+

```bash
python -m pytest
```

`pytest.ini` points pytest at the `tests/` folder and adds `diagrams/` to the import path, so the command works from the project root.

### What the tests cover

The tests are in [tests/test_pawpal.py](tests/test_pawpal.py):

- **Task basics:** `mark_complete()` sets a task's `completed` flag, and `add_task()` adds a task to a pet.
- **Sorting correctness:** `sort_by_time()` returns tasks in chronological order, including midnight and single-digit hours.
- **Recurrence logic:** completing a daily task creates a new incomplete task due the next day (including a month rollover), and completing a non-daily task creates nothing.
- **Conflict detection:** `detect_conflicts()` flags tasks at the same time for different pets, and stays quiet when times or days differ.

### Test output

```
============================= test session starts ==============================
platform darwin -- Python 3.11.5, pytest-7.4.0, pluggy-1.0.0 -- /Users/jamoyamondle/anaconda3/bin/python
cachedir: .pytest_cache
rootdir: /Users/jamoyamondle/Documents/GitHub/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-3.5.0, typeguard-2.13.3
collecting ... collected 7 items

tests/test_pawpal.py::test_mark_complete_sets_completed_true PASSED      [ 14%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 28%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 42%]
tests/test_pawpal.py::test_daily_task_completion_creates_next_day_task PASSED [ 57%]
tests/test_pawpal.py::test_non_daily_task_completion_creates_no_new_task PASSED [ 71%]
tests/test_pawpal.py::test_detect_conflicts_flags_duplicate_times_across_pets PASSED [ 85%]
tests/test_pawpal.py::test_detect_conflicts_returns_empty_when_times_differ PASSED [100%]

============================== 7 passed in 1.66s ===============================
```

### Confidence level: ★★★★☆ (4 / 5)

All 7 tests pass, and they cover the three smarter-scheduling features (sorting, recurrence, conflict detection) and the happy paths for each. Some behavior weren't tested yet. `generate_daily_plan()`, `filter_by_availability()` and `filter_by_completion()` have no tests. Conflict detection only catches exact start-time matches, so overlapping durations aren't flagged. Double completion and multi-day recurring tasks aren't tested either.Therefor I would give it a 3.5/5

## 📐 Smarter Scheduling

All scheduling logic lives in [diagrams/pawpal_system.py](diagrams/pawpal_system.py), and [diagrams/main.py](diagrams/main.py) demonstrates it end to end.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `SchedulePlanner.sort_by_time()`, `SchedulePlanner.sort_by_priority()` | By start time or by priority |
| Filtering | `SchedulePlanner.filter_by_completion()`, `SchedulePlanner.filter_by_availability()`, `Pet.pending_tasks`, `Owner.tasks` | By completion status, owner free time, and pet |
| Conflict handling | `SchedulePlanner.detect_conflicts()` | Warns when tasks share a day and start time |
| Recurring tasks | `Task.mark_complete()` | Completing a daily task creates tomorrow's task |

### Sorting

- **`sort_by_time(tasks)`** orders tasks from earliest to latest. A `sorted()` call with a lambda key converts each `start_time` to a zero-padded `"HH:MM"` string, which sorts chronologically as text. The sort is stable, so ties keep their original order, and the input list is not modified.
- **`sort_by_priority(tasks)`** orders tasks from HIGH to LOW using the `Priority` enum value as the key. `generate_daily_plan()` uses it before filling the available minutes.

### Filtering

- **`filter_by_completion(tasks, completed)`** keeps only finished tasks (`True`) or pending tasks (`False`).
- **`filter_by_availability(tasks, owner)`** keeps only tasks that fit within the owner's free minutes on every day the task occurs.
- **By pet:** each `Pet` keeps its own task list, so `pet.tasks` and `pet.pending_tasks` give one pet's tasks. `owner.tasks` combines the tasks of all of an owner's pets.

### Conflict detection

**`detect_conflicts(tasks)`** is a lightweight check. In a single pass it groups tasks by `(day, start_time)` and reports any group with two or more tasks. This catches two tasks for the same pet and tasks for different pets. It returns a list of warning strings, such as `Warning: 2 tasks on Wednesday at 06:30: 'Vet Checkup' (NichiBear), 'Feed Gertrude' (Gertrude)`, and never raises, so the program keeps running. An empty list means no conflicts.

**Limitation:** only exact start-time matches are caught. Tasks whose durations overlap but start at different times (for example 9:00 for 30 minutes and 9:15) are not flagged.

### Recurring tasks

**`Task.mark_complete()`** marks a task done. If the task's `frequency` is `DAILY`, it also creates a new incomplete copy due the next day. The next date is computed with `timedelta(days=1)` on the task's `due_date`, so month and year rollovers are handled correctly. The copy's `days` is set to the weekday of that date, and the copy is added to the same pet. The method returns the new task, or `None` for non-daily tasks or tasks that were already complete, which prevents duplicate occurrences.

### Tradeoff

`generate_daily_plan()` is greedy. It takes tasks in priority order and keeps each one that still fits in the remaining time. This is fast and easy to follow, but it doesn't always find the combination of tasks that uses the time best.

## 📸 Demo Walkthrough

Start the app with `streamlit run app.py`. It has three tabs.

### Main UI features

- **Owner & pets:** save the owner's name, the days they are available, the minutes free on those days, and care preferences. Add pets with a name, breed, weight and age. A table lists the pets.
- **Care tasks:** add a task for a pet with a name, description, scheduled days, start time, duration, frequency and priority. The tab also lets you:
  - see a conflict alert (`st.warning`) or an all-clear message (`st.success`) for pending tasks;
  - mark a pending task complete;
  - filter the task table by pet and by status (All, Pending, Complete);
  - sort the table by start time or priority.
- **Daily plan:** choose a day, a time limit and a pet, then click **Generate daily plan**. The plan appears as a numbered table in time order, with a summary of the minutes used, conflict warnings, and a warning that names any tasks that didn't fit.

### Example workflow

1. **Owner & pets:** enter an owner name, keep the available days, set 180 minutes, and click **Save owner**. Then add a pet, such as NichiBear, a Great Dane and Labrador mix.
2. **Care tasks:** add "Morning Walk" for NichiBear on today's weekday at 7:00 AM for 30 minutes, with Daily frequency and High priority. Add a second task for the same time, for example "Vet Checkup".
3. **Care tasks:** a warning appears saying two tasks start at the same time, naming both tasks and their pets. Change one task's time to clear it.
4. **Care tasks:** use the filters to show only pending tasks, sorted by start time. Select "Morning Walk" under **Mark a task complete** and click **Mark complete**. A success message says the next daily occurrence was created for tomorrow.
5. **Daily plan:** pick today's weekday and a pet, then click **Generate daily plan**. The time-ordered schedule appears with the total minutes used, and any task that didn't fit is listed in a warning.

### Scheduler behaviors shown

- **Sorting:** the task table and the daily plan are ordered by start time (`sort_by_time()`), with priority sorting available in the task table (`sort_by_priority()`).
- **Filtering:** tasks are filtered by completion status (`filter_by_completion()`) and by pet. The plan keeps only tasks that fit the selected day and available minutes.
- **Conflict warnings:** `detect_conflicts()` flags tasks that share a day and start time, without crashing the app.
- **Daily recurrence:** `Task.mark_complete()` creates the next day's task for daily tasks.
- **Time budget:** the plan fills the available minutes by priority and reports which tasks were left out.

### Sample CLI output

Running `python main.py` from the `diagrams/` folder schedules three tasks for today, prints the schedule, flags the 6:30 clash between two pets' tasks, then completes a daily task:

```
Today's Schedule
Today's plan (120 minutes total):
- [HIGH] Vet Checkup at 06:30:00 (45 min)
- [HIGH] Feed Gertrude at 06:30:00 (45 min)
- [HIGH] Morning Walk at 09:30:00 (30 min)
Warning: 2 tasks on Wednesday at 06:30: 'Vet Checkup' (NichiBear), 'Feed Gertrude' (Gertrude)

Completed: ['Feed Gertrude']
Next occurrence created: Feed Gertrude on 2026-10-08 (Thursday)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

#Generate mermaid.js code for uml diagram using this instructions
Classes:
/Pet Class:
    This includes name of the dog, weight, breed, age, pet care task history, name of owner.

/Owner Class:
    Name , name of dog owned, availability, and task preferences

/Task Class:
    Name of owner, name of dog, name of task, day(s) of the week this task is done, duration of task, priority of task.

The relationship between each task: owner owns pet, pet owns owner class, and pet owner owns task class

Core behavior of pawpal_system.py
Ownership model: an Owner has Pets, and each Pet has Tasks, so every task can reach its pet and its owner.
Daily plan generation: generate_daily_plan() drops tasks that don't fit the owner's availability, sorts the rest by priority, and greedily fills the available minutes.
Sorting and filtering: the planner can sort tasks by start time or priority, and filter them by completion status or owner availability.
Conflict detection: detect_conflicts() returns warnings, without raising errors, when tasks share the same day and start time, for the same pet or different pets.
Recurring tasks: completing a daily task with mark_complete() creates the next day's task, using timedelta to calculate the date.

## ✨ Features

- **Sorting by time:** `sort_by_time()` orders tasks from earliest to latest start time. It uses `sorted()` with a lambda key that converts each start time to a zero-padded `"HH:MM"` string, so "08:05" correctly comes before "10:00". Tasks with the same time keep their original order.
- **Sorting by priority:** `sort_by_priority()` orders tasks HIGH → MEDIUM → LOW using the `Priority` enum value as the sort key.
- **Greedy daily planning:** `generate_daily_plan()` filters out tasks that don't fit the owner's availability, sorts the rest by priority, then walks the list once. It adds each task that still fits in the remaining minutes. It is fast and always favors high-priority tasks, but it doesn't always find the best possible mix of tasks.
- **Availability filtering:** `filter_by_availability()` keeps only tasks whose duration fits within the owner's free minutes on every day the task occurs.
- **Completion filtering:** `filter_by_completion()` returns only pending or only completed tasks. Pets and owners also expose `pending_tasks` and `completed_tasks`, and `owner.tasks` combines the tasks of all pets.
- **Conflict warnings:** `detect_conflicts()` groups tasks by `(day, start_time)` in one pass and returns a warning message for each group with two or more tasks. It works for the same pet or different pets and never raises an error. It only catches exact start-time matches, not overlapping durations.
- **Daily recurrence:** `Task.mark_complete()` marks a task done. For a `DAILY` task, it also creates a new incomplete task due the next day, calculated with `timedelta(days=1)` so month and year rollovers are correct. Completing the same task twice does not create a duplicate.
- **Plan explanation:** `explain_plan()` turns a plan into a readable summary with the total minutes and each task's priority, name, time and duration.
- **Streamlit display:** `app.py` shows these results with `st.table`, `st.success` and `st.warning`. It includes pet and status filters, a sort selector, conflict alerts, a "Mark complete" action, and a warning for tasks that didn't fit in the available time.
