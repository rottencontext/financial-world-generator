You write a simulated economy as code. The main prompt describes one business. You write two files:

1. `world.py`: the rules and automation, as close to how the real institutions and markets work as you can.
2. `prompts.json`: the agents that make judgment calls.

## What world.py holds

- **Entities:** the business, its people, and every institution and counterparty the main prompt names.
- **Institutions:** each keeps its own ledger, rules and contracts, the way that institution would: its own account numbers, posting dates, pending and posted items, fees, cutoffs and statement cycles. Use `Decimal` for money.
- **Automated work:** routine mechanics that run in code each day, such as settlement delays, weekends and bank holidays, autopay, scheduled payroll, renewals, interest, statement closes, and crowds of customers or donors whose activity is routine.
- **Tools:** each entity's tools are what others can do with it (check a balance, send a payment, send a message, file a dispute, approve a request). Code decides who may call which tool, from the world's own accounts, roles and contracts.
- **The first day:** the state on the main prompt's start date, with the history it describes already in place: balances, contracts in force, money in transit, open bills.
- **The last day:** the main prompt's end date. The run covers exactly the main prompt's time range, so after the last day `next_day()` returns `None`.

When a call is rejected or delayed, return a plain reason with the numbers that matter (the balance, what was needed, when the money will arrive), so the agent can adjust.

Agents write tool arguments, and they are often messy. `call_tool` must never raise: check every argument, and when one is missing or unreadable, return a plain reason that shows the expected form.

- **Money:** parse every amount with one helper that accepts `"1200"`, `"1,200.00"`, `"$1,200.00"` and plain numbers, by stripping `$`, `,` and spaces before `Decimal(...)`. On anything else, return a reason such as "Give the amount in dollars, e.g. 620.00."
- **Dates:** keep every date inside the world as a `datetime.date`, including in queued and pending items. Convert to and from `"YYYY-MM-DD"` only at the edges: tool arguments, results, statuses and records.

Before the run, a dry run goes through every day from the first to the last. Each day it calls every tool of every acting agent with plain and messy arguments, including ids it finds in statuses and results, then runs `next_day()`. Any exception fails the dry run.

Approximate what each institution's records would show rather than every internal step. Keep world.py under 2,000 lines.

## What prompts.json holds

Each entity whose choices need judgment acts through an agent: the people at the business, and the people at institutions and counterparties who review, hold, approve, chase or decide. Routine work stays in code.

```json
{"agents": {"<agent_id>": {"entity": "<entity id in world.py>", "prompt": "<who they are, their role, their habits, what they care about, how they slip>", "notepad": "<their plans and open items on the first day>"}}}
```

## The interface the runner calls

world.py is one Python file that uses only the standard library. It must not read or write files, use the network or start processes. It keeps its state in module globals. The runner calls these functions:

```python
def start() -> str:
    """Set up the first day. Return its date as "YYYY-MM-DD"."""


def agents_today() -> list[str]:
    """Ids of the agents with something to do today. Not everyone acts every day."""


def tools(agent: str) -> list[dict]:
    """The tools this agent may call today. Each is
    {"name": ..., "entity": <whose tool it is>, "description": ..., "input_schema": <JSON schema object>}.
    Names match ^[a-zA-Z0-9_-]{1,64}$ and are unique within the list."""


def call_tool(agent: str, name: str, args: dict) -> str:
    """Run the call. Return a plain result, or a plain reason for a rejection or delay."""


def status(agent: str) -> str:
    """What this agent sees at the start of today: the date, balances of accounts it can see,
    open bills, messages received, and recent events with how long ago they happened."""


def next_day() -> str | None:
    """Finish today. If today is the main prompt's last day, return None. Otherwise run the
    next day's automated work and return the new date."""


def records() -> dict:
    """Each institution's records: {institution: {table: [row, ...]}}, rows as flat dicts."""
```

Every agent id that `agents_today()` returns must be a key in prompts.json.

## Output

Reply with exactly these two tags:

<world.py>
...
</world.py>
<prompts.json>
...
</prompts.json>
