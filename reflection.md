# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
One of the core actions my system should be able to do is owners should be able to add or remove tasks from the daily schedule, owner should be able to add or remove pet from list and should be able see the explanation as to why the specific tasks were created and why it is listed in that specific order.
- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
1c. I added field(repr=False, compare=False) to Task.pet and to Pet.owner/Pet.task_history. This is because the Task points to the Pet and that Pet has a list of tasks that inclides the same task pointing right to the Pet. This logic causes a Recursive logic when you try to print/compare the tasks or check if they are in a list.
-I removed Task.owner as a separate stored field and replaced it with a computed property that reads self.pet.owner, so a task's owner can never disagree with its pet's owner so theres only one source instead of 2 fields that could go out of sync
- There were no functions that add task to the task history, remove task from the task history and get task from the history for the pet class. Additionally, there were no functions to add pets and remove pets for the Owner class. So I accepted the agents creation of these agents these are important functionalities of this web app.This functio also sets pet.owner= self so adding a pet updates both sides of the relationship at once.
-Another problem I addressed was that the days of the week and the priority variable was hard coded as a string. This will be more difficult to navigate when creating the task recommendation function. So instead the agent implemented a days of the week and priority task class.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**
The scheduler considers the owner's free minutes on each day, each task's scheduled days and start time, task duration, and task priority (High, Medium, Low). Owner preferences are stored but not used in planning yet. I ranked the constraints in this order: availability first, because a task that doesn't fit the owner's time can't happen at all; priority second, so the most important care (feeding, medication, vet visits) is placed before optional tasks; and start time last, which is used to order the final plan and to detect clashes.

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**
The tradeoff of the scheduler is that it warns the user that 2 tasks begin at the same but it doesn't actually resolve the issue.
A second tradeoff is that `generate_daily_plan()` is greedy: it takes tasks in priority order and keeps each one that still fits. It is fast and easy to understand, but it can miss a better combination (for example, a 25-minute High task can block two 15-minute tasks that would have used the time exactly). Conflict detection is also lightweight: it only catches tasks with the same start time, not overlapping durations.
- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
These tradeoffs are reasonable because PawPal+ plans one pet owner's day with only a handful of tasks, so a simple, predictable algorithm is easier to explain to the user and to test than an optimal one. Warning instead of auto-resolving also keeps the owner in control of their own schedule, since only they know which task can actually move.

---

## 3. AI Collaboration

**a. How you used AI**
The most effective features were:
- **Reading my actual files.** When the assistant could see `pawpal_system.py`, `main.py` and `app.py`, its suggestions matched my real class and method names instead of generic ones.
- **Turning the UML into code.** Generating the class skeleton from my diagram gave me a starting point, and it also exposed gaps (no add/remove methods, string-typed days and priorities).
- **Making small, targeted edits and running them.** Adding `sort_by_time`, `filter_by_completion`, `detect_conflicts` and the daily-recurrence logic one at a time, then running `main.py` or pytest right after, kept each change easy to check.
- **Drafting tests and docs.** It wrote pytest cases for sorting, recurrence and conflicts, and docstrings and README sections, which I then reviewed.
- **Explaining tradeoffs.** Asking "what tradeoffs does the scheduler make?" or "what edge cases should I test?" helped me see limits in my own design.

The most helpful prompts were specific ones that named the method and the behavior I wanted (for example, "use `sorted` with a lambda key on `HH:MM` strings" or "use `timedelta` for the next occurrence").

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**
When I asked for a `sort_by_time` method, the first edit the AI proposed also changed `sort_by_priority` to break ties by start time. I rejected that edit. Priority sorting and time sorting are two different jobs, and mixing them would have made `sort_by_priority` behave differently from its name and from the UML. I asked for the change to be limited to a new, separate `sort_by_time` method, and the planner now keeps one method per sorting rule that callers can combine.

I also rejected an edit that wired only a conflict check into `main.py`. I asked for all the new scheduler methods to be wired in, so `main.py` demonstrates sorting, filtering, conflict warnings and recurrence together.

To verify AI output I ran it instead of trusting it: I ran `main.py` to see the real schedule and warning, and I ran pytest. That also caught a setup problem, a duplicate `test_pawpal.py` name and a missing import path, which I fixed with a `pytest.ini`.

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

**c. Separate chat sessions**
Using a separate chat session for each phase kept the work organized. One session focused on the design and UML, another on implementing the scheduling logic in `pawpal_system.py`, and another on testing and the Streamlit UI. Each session started with only the context it needed, so the AI wasn't distracted by old brainstorming or earlier versions of the code, and its answers stayed on the task at hand. It also made my history easier to review: I could find the reasoning behind a design decision in the design session without searching through code changes. The cost is that a new session doesn't remember earlier decisions, so I had to restate key facts, such as the class names and the lightweight conflict-detection choice, or point it at the current files.

---

## 4. Testing and Verification

**a. What you tested**
I wrote 7 pytest tests covering: marking a task complete, adding a task to a pet, sorting tasks by time into chronological order (including midnight and single-digit hours), completing a daily task creating a new task due the next day (including a month rollover), completing a non-daily task creating nothing, and conflict detection flagging same-time tasks across different pets and staying quiet when times or days differ. These matter because sorting, recurrence and conflicts are the three smarter-scheduling features, and each one has date or time details that are easy to get subtly wrong.

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**
I'm about 4 out of 5 confident. All 7 tests pass and they cover the core features, but `generate_daily_plan()`, the availability filter and the completion filter don't have tests yet, and conflict detection ignores overlapping durations. Next I would test: completing the same task twice, un-completing and completing again, a daily task listing several days, tasks that fit the time budget exactly or one minute over, no tasks or no availability, and overlapping tasks (9:00 for 30 minutes and 9:15).

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**
I'm most satisfied with how the pieces connect: the owner-pet-task model, the sorting, filtering, conflict and recurrence methods, and the Streamlit app all use the same `SchedulePlanner` methods, and `main.py` and the tests exercise them from the outside. Making `Task.owner` a computed property and using `timedelta` for recurrence also removed whole classes of bugs.

- What part of this project are you most satisfied with?

**b. What you would improve**
I would detect overlapping durations instead of only identical start times, and let the planner suggest a free slot when it finds a conflict. I would make the Streamlit plan call `generate_daily_plan()` instead of repeating its own greedy loop, so there is one source of truth. I would also use owner preferences in planning, try a knapsack-style selection for better time use, and add tests for the planner and filters.

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**
The AI is a fast collaborator, but I am the architect. It can write a method in seconds, but it also makes changes I didn't ask for, so the design has to stay in my hands: I decide what each class is responsible for, I keep changes small, and I verify every one by running the code and the tests.

- What is one important thing you learned about designing systems or working with AI on this project?
