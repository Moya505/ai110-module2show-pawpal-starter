"""PawPal scheduling system skeleton, generated from the UML class diagram."""


from __future__ import annotations


from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta #Added
from enum import Enum, IntEnum
from typing import Dict, List, Optional


class DayOfWeek(str, Enum):
	MONDAY = "Monday"
	TUESDAY = "Tuesday"
	WEDNESDAY = "Wednesday"
	THURSDAY = "Thursday"
	FRIDAY = "Friday"
	SATURDAY = "Saturday"
	SUNDAY = "Sunday"




class Priority(IntEnum):
	HIGH = 1
	MEDIUM = 2
	LOW = 3




class Frequency(str, Enum): #Added
	ONCE = "Once"
	TWICE = "Twice"
	THREE_TIMES = "3 times"
	FOUR_TIMES = "4 times"
	DAILY = "Daily"




Availability = Dict[DayOfWeek, int]
"""Maps a day of the week to how many minutes the owner is free that day."""



@dataclass
class Task:
	name: str
	description: str
	days: List[DayOfWeek]
	start_time: time #Added
	duration_minutes: int
	frequency: Frequency #Added
	priority: Priority
	pet: "Pet" = field(repr=False, compare=False)
	completed: bool = False
	due_date: date = field(default_factory=date.today) #Added


	@property
	def owner(self) -> "Owner":
		"""Returns this task's owner, derived from its pet's owner."""
		return self.pet.owner


	def is_recurring_on(self, day: DayOfWeek) -> bool:
		"""Checks whether this task is scheduled to occur on the given day."""
		return day in self.days


	def update_priority(self, new_priority: Priority) -> None:
		"""Changes this task's priority."""
		self.priority = new_priority


	def update_duration(self, minutes: int) -> None:
		"""Changes this task's duration in minutes."""
		self.duration_minutes = minutes


	def mark_complete(self) -> Optional["Task"]:
		"""Marks this task as completed and, if it is daily, schedules the next occurrence.

		For a DAILY task, a copy is created with due_date advanced by
		timedelta(days=1) and `days` set to that date's weekday, so month and year
		rollovers are handled correctly. The copy is incomplete and is added to the
		same pet's task list.

		Returns:
			The newly created Task for a daily task, or None if the task is not daily
			or was already complete (which also prevents duplicate occurrences).
		"""
		if self.completed:
			return None
		self.completed = True

		if self.frequency != Frequency.DAILY:
			return None

		next_due = self.due_date + timedelta(days=1)
		next_task = replace(
			self,
			days=[DayOfWeek(next_due.strftime("%A"))],
			completed=False,
			due_date=next_due,
		)
		self.pet.add_task(next_task)
		return next_task


	def mark_incomplete(self) -> None:
		"""Marks this task as not completed."""
		self.completed = False




@dataclass
class Pet:
	name: str
	breed: str
	weight: float
	age: int
	owner: "Owner" = field(repr=False, compare=False)
	tasks: List[Task] = field(default_factory=list, repr=False, compare=False)


	def add_task(self, task: Task) -> None:
		"""Adds a task to this pet's task list, if it isn't already there."""
		if not any(existing is task for existing in self.tasks):
			self.tasks.append(task)


	def remove_task(self, task: Task) -> None:
		"""Removes a task from this pet's task list."""
		self.tasks = [existing for existing in self.tasks if existing is not task]


	def get_task_history(self) -> List[Task]:
		"""Returns a copy of this pet's full task list."""
		return list(self.tasks)


	@property
	def pending_tasks(self) -> List[Task]:
		"""Returns this pet's tasks that are not yet completed."""
		return [task for task in self.tasks if not task.completed]


	@property
	def completed_tasks(self) -> List[Task]:
		"""Returns this pet's tasks that are completed."""
		return [task for task in self.tasks if task.completed]






class Owner:
	def __init__(self, name: str, availability: Availability | None = None, preferences: List[str] | None = None):
		self.name = name
		self.availability: Availability = availability or {}
		self.preferences: List[str] = preferences or []
		self.pets: List[Pet] = []


	@property
	def tasks(self) -> List[Task]:
		"""Returns every task across all of this owner's pets."""
		return [task for pet in self.pets for task in pet.tasks]


	@property
	def pending_tasks(self) -> List[Task]:
		"""Returns every not-yet-completed task across all of this owner's pets."""
		return [task for task in self.tasks if not task.completed]


	@property
	def completed_tasks(self) -> List[Task]:
		"""Returns every completed task across all of this owner's pets."""
		return [task for task in self.tasks if task.completed]


	def add_pet(self, pet: Pet) -> None:
		"""Adds a pet to this owner and sets the pet's owner reference to match."""
		if not any(existing is pet for existing in self.pets):
			self.pets.append(pet)
			pet.owner = self


	def remove_pet(self, pet: Pet) -> None:
		"""Removes a pet from this owner."""
		self.pets = [existing for existing in self.pets if existing is not pet]


	def update_availability(self, new_schedule: Availability) -> None:
		"""Replaces this owner's availability schedule."""
		self.availability = new_schedule


	def set_preferences(self, preferences: List[str]) -> None:
		"""Replaces this owner's list of preferences."""
		self.preferences = preferences




class SchedulePlanner:
	def generate_daily_plan(self, pet: Pet, owner: Owner, available_minutes: int) -> List[Task]:
		"""Builds a prioritized list of this pet's pending tasks that fit within the available minutes."""
		candidates = self.filter_by_availability(pet.pending_tasks, owner)
		candidates = self.sort_by_priority(candidates)


		plan: List[Task] = []
		remaining_minutes = available_minutes
		for task in candidates:
			if task.duration_minutes <= remaining_minutes:
				plan.append(task)
				remaining_minutes -= task.duration_minutes
		return plan


	def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
		"""Sorts tasks from highest to lowest priority."""
		return sorted(tasks, key=lambda task: task.priority)


	def sort_by_time(self, tasks: List[Task]) -> List[Task]:
		"""Sorts tasks from earliest to latest start time.

		Each task's start_time is converted to a zero-padded "HH:MM" string by a lambda
		key, which sorts in chronological order as plain text. Ties keep their original
		relative order, since sorted() is stable.

		Args:
			tasks: Tasks to order. The list is not modified.

		Returns:
			A new list of the same tasks, earliest start time first.
		"""
		return sorted(tasks, key=lambda task: task.start_time.strftime("%H:%M"))


	def filter_by_availability(self, tasks: List[Task], owner: Owner) -> List[Task]:
		"""Keeps only the tasks that fit within the owner's free time on every day they occur."""
		return [
			task
			for task in tasks
			if all(
				owner.availability.get(day, 0) >= task.duration_minutes
				for day in task.days
			)
		]


	def filter_by_completion(self, tasks: List[Task], completed: bool) -> List[Task]:
		"""Filters tasks by completion status.

		Args:
			tasks: Tasks to filter. The list is not modified.
			completed: True to keep finished tasks, False to keep pending ones.

		Returns:
			A new list of the tasks whose `completed` flag equals `completed`,
			in their original order.
		"""
		return [task for task in tasks if task.completed == completed]


	def detect_conflicts(self, tasks: List[Task]) -> List[str]:
		"""Detects tasks scheduled to start at the same time on the same day.

		Lightweight strategy: tasks are grouped by (day, start_time) in a single O(n)
		pass, and any group with two or more tasks is reported. Tasks conflict whether
		they belong to the same pet or different pets. Only exact start-time matches are
		caught; overlapping durations (e.g. 9:00 for 30 min and 9:15) are not.

		Args:
			tasks: Tasks to check, such as owner.pending_tasks.

		Returns:
			One warning string per clashing day/start time, naming each task and its
			pet. An empty list means no conflicts. It returns warnings and never raises.
		"""
		slots: Dict[tuple, List[Task]] = {}
		for task in tasks:
			for day in task.days:
				slots.setdefault((day, task.start_time), []).append(task)

		warnings: List[str] = []
		for (day, start), clashing in slots.items():
			if len(clashing) > 1:
				details = ", ".join(f"'{t.name}' ({t.pet.name})" for t in clashing)
				warnings.append(f"Warning: {len(clashing)} tasks on {day.value} at {start:%H:%M}: {details}")
		return warnings


	def explain_plan(self, plan: List[Task]) -> str:
		"""Renders a list of tasks as a human-readable schedule summary."""
		if not plan:
			return "No tasks fit in the available time today."


		total_minutes = sum(task.duration_minutes for task in plan)
		lines = [f"Today's plan ({total_minutes} minutes total):"]
		for task in plan:
			lines.append(
				f"- [{task.priority.name}] {task.name} at {task.start_time} "
				f"({task.duration_minutes} min)"
			)
		return "\n".join(lines)


'''
Task

'''
