This module allows to follow what happens in a sprint, customer by customer.

It adds a sprint dashboard based on the fortnight sprints of `project_sprint`.
For the selected customer and sprint, it shows the tasks:

- **Done**: tasks of the sprint in the `Done` state;
- **In progress**: open tasks of the sprint with an estimate step;
- **To start**: open tasks of the sprint without estimate step, or in the
  `Waiting` state;
- **Carried over**: tasks of the sprint coming from a previous sprint. They are
  also counted in their status (done, in progress, to start). A task moved to
  a later sprint leaves the previous one.

Canceled tasks are ignored. The estimated time comes from the estimate step
of `project_estimate_step` (in days).

It also shows the **run** work of the sprint: tasks with a run tag of their
project (debug, urgent, out of sprint planning). For run tasks, the time is
the time spent (timesheets) when there is any, else the estimate step. The
dashboard shows how much of the sprint time was taken by run, to see if a
period was spent improving the project or fixing it.

The dashboard also shows the progress per project and the done versus planned
days of the last sprints, split between planned work and run.

To know which tasks were carried over, the module keeps the history of the
fortnight sprints of each task (`Sprint History`) and tracks the changes of
the sprint in the chatter.
