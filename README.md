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
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

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

