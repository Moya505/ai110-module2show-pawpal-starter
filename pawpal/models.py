from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Owner:
    name: str
    availability: str
    preferences: List[str] = field(default_factory=list)
    pets: List["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        if pet not in self.pets:
            self.pets.append(pet)
            pet.owner = self

    def remove_pet(self, pet: "Pet") -> None:
        if pet in self.pets:
            self.pets.remove(pet)
            pet.owner = None

    def update_availability(self, new_schedule: str) -> None:
        self.availability = new_schedule

    def set_preferences(self, preferences: List[str]) -> None:
        self.preferences = preferences


@dataclass
class Task:
    name: str
    description: str
    day_of_week: str
    duration_minutes: int
    priority: str
    owner: Optional[Owner] = None
    pet: Optional["Pet"] = None

    def is_recurring_on(self, day: str) -> bool:
        return self.day_of_week.lower() == day.lower()

    def update_priority(self, new_priority: str) -> None:
        self.priority = new_priority

    def update_duration(self, minutes: int) -> None:
        self.duration_minutes = minutes


@dataclass
class Pet:
    name: str
    breed: str
    weight: str
    age: int
    owner: Optional[Owner] = None
    task_history: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        if task not in self.task_history:
            self.task_history.append(task)
            task.pet = self

    def remove_task(self, task: Task) -> None:
        if task in self.task_history:
            self.task_history.remove(task)
            task.pet = None

    def get_task_history(self) -> List[Task]:
        return list(self.task_history)


class SchedulePlanner:
    """Small scheduler that ranks tasks based on priority and owner constraints."""

    @staticmethod
    def generate_daily_plan(pet: Pet, owner: Owner, available_minutes: int) -> List[Task]:
        tasks = [task for task in pet.task_history if task.owner == owner]
        ranked = SchedulePlanner.sort_by_priority(tasks)

        plan: List[Task] = []
        total = 0
        for task in ranked:
            if total + task.duration_minutes <= available_minutes:
                plan.append(task)
                total += task.duration_minutes
        return plan

    @staticmethod
    def sort_by_priority(tasks: List[Task]) -> List[Task]:
        priority_order = {"high": 3, "medium": 2, "low": 1}
        return sorted(tasks, key=lambda task: priority_order.get(task.priority.lower(), 0), reverse=True)

    @staticmethod
    def filter_by_availability(tasks: List[Task], owner: Owner) -> List[Task]:
        return [task for task in tasks if owner.availability and task.is_recurring_on("Monday")]

    @staticmethod
    def explain_plan(plan: List[Task]) -> str:
        if not plan:
            return "No tasks fit into the available schedule."
        return " | ".join(f"{task.name} ({task.priority}, {task.duration_minutes} min)" for task in plan)
