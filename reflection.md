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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**
The tradeoff of the scheduler is that it warns the user that 2 tasks begin at the same but it doesn't actually resolve the issue.
- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redes