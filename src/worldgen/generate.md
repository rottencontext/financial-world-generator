You write a simulated economy as two files:

1. `prompts.json`: **every actor in the world is an agent** — customers, merchants/studios, vendors, internal staff, and the institutions themselves (banks, payment processors, card/ACH networks, accounting systems, payroll providers). Each agent knows its role, its contracts and relationships with others, its pricing or spending habits (whether it is a big spender, a regular buyer, or a strict reconciler), and when it acts as the clock passes.
2. `world.py`: **the shared state, contracts, ledgers, and tools** that agents call on their turns. `world.py` has **no daily simulation loop or RNG event generator** — `next_day()` only advances the calendar date by one day. Every charge, settlement, payout, bank posting, refund, message, and journal entry happens because an agent called a tool.

## What `prompts.json` holds

Every entity that acts in the economy is an agent in `prompts.json`:

- **Customers, merchants, and vendors:** each knows who they are, their size and spending/pricing tier (e.g. a flagship climbing gym vs. a small yoga studio; a heavy pack-buying member vs. a regular monthly member), their contract terms (billing day, payment method, subscription rate, application fee), and their habits (when they buy, renew memberships, reconcile payouts, or request a refund or instant payout). Do not ask any customer or member agent to commit fraud, use stolen cards, or file disputes. Cohort or archetype agents may represent groups of similar customers or merchants when a prompt names a large crowd, calling batch or multi-item tools according to their persona.
- **Internal company staff:** finance, support, ops, sales, engineering, and founders. Each knows their workflow and schedule (e.g. daily or weekly payout matching, webhook syncing, refund processing, month-end close) as described in the main prompt.
- **Institutions (processors, banks, networks, ledgers, payroll):** each institution is also an agent (or has an officer/operations agent) that knows its published rules, cutoffs, and contracts:
  - A **processor agent** (e.g. Stripe) sees pending transactions whose holding period is up (2 business days for cards, 3–4 for ACH), marks them available, takes its fees or monthly invoices per contract, and submits daily automatic payouts grouping the available items.
  - A **bank agent** posts arriving deposits, wires, and ACH debits on business days (never on weekends or federal holidays), closes monthly statements, and maintains running balances.
  - A **ledger / payroll / card agent** (e.g. Xero, payroll provider, company card) imports bank feeds, posts summary journals, schedules payroll debits two business days before payday, and issues monthly statements when the calendar calls for them.

```json
{
  "agents": {
    "<agent_id>": {
      "entity": "<entity id in world.py>",
      "prompt": "<who they are, their contracts and relationships, their size/spending/pricing habits, and what calendar/state triggers they watch>",
      "plans": [
        {"due": "YYYY-MM-DD", "task": "<dated plan or scheduled commitment that stays until marked done>"}
      ],
      "notes": [
        "<starting observation or open context on the first day; automatically stamped with the start date>"
      ]
    }
  }
}
```

The runner gives every agent a built-in `memory` tool (`add_plan`, `update_plan`, `done_plan`, `add_note`, `replace_note`, `remove_note`) to manage its `plans` and dated `notes` deliberately during its turn. Do not define a tool named `memory` in `world.py`.

## What `world.py` holds

- **Entities and contracts:** the initial roster of people, businesses, accounts, and contracts in force on the start date (who owes whom, fee rates, subscription amounts, bank account status, opening rows).
- **The first day (`start()`):** sets up the state on the main prompt's start date, with the history it describes already recorded as real rows in each institution's tables (opening transactions that sum to every opening balance, items already in transit, open bills, unread messages).
- **The clock (`next_day()`):** advances `DAY` by one day (`DAY += timedelta(days=1)`) and returns the new date as `"YYYY-MM-DD"`, or `None` after the main prompt's end date. Do not put hidden RNG loops or pre-scripted events in `next_day()`.
- **Who wakes (`agents_today()`):** returns the list of agent IDs that have a turn today. All active institution, staff, customer, and counterparty agents whose calendar or inbox gives them something to check or do today wake up and decide via their tools.
- **Tools (`tools(agent)` and `call_tool(agent, name, args)`):** each entity's tools let agents inspect state and take actions (charge a card/ACH, settle matured items, bundle available items into a payout, post arrived bank items, issue a refund, process webhooks, post a journal, reconcile bank lines, send an email/message).
  - Code checks permissions, contract rules, and arithmetic when a tool is called, and writes the resulting rows into the institution's table.
  - Every tool that looks up records searches them the way a person would: by name, amount, date, status, or words in a description, not only by exact ID.
  - When a call is rejected or delayed, return a plain reason with the numbers that matter (the balance, what was needed, when funds will settle), so the agent can adjust.

### Four Bookkeeping Rules Every Tool Must Enforce

1. **Every balance comes from rows:** No account or ledger may have an opening number without transaction rows behind it. A balance is always the sum of its posted rows (and available balance is the sum of available rows not yet paid out).
2. **Running balances recompute:** Whenever a bank or ledger row is posted, its `balance_after` equals the previous row's `balance_after` plus the signed `amount`.
3. **Grouping rows list their parts and equal their sum:** Whenever a tool creates a row that groups other rows (a payout, a batch deposit, a statement, a remittance), it must take or select the child rows, record their IDs on the group row (`item_ids: [...]`) and/or stamp the group ID on each child row (`payout_id: "po_..."`), and set the group row's amount to the exact `Decimal` sum of those children. Never create a payout or batch with zero items or an arbitrary amount.
4. **Statuses agree with dates:** When an institution agent settles a pending transaction or marks an in-transit payout as arrived/paid, the tool updates the row's `status` field (`"pending"` -> `"available"` -> `"paid"` / `"posted"`) alongside its date.

### Handling Messy Tool Arguments

Agents write tool arguments, and they are often messy. Reject a bad argument with a plain message; never let a bad argument reach `Decimal(...)`, `int(...)`, `date.fromisoformat(...)` or a list slice unparsed:

- **Money:** parse every amount with one helper that accepts `"1200"`, `"1,200.00"`, `"$1,200.00"` and plain numbers, by stripping `$`, `,` and spaces before `Decimal(...)`. On anything else, return a plain message such as `"Give the amount in dollars, e.g. 620.00."`
- **Integers / limits:** coerce integer arguments like `limit` with one helper (`int(str(v).strip())`) before slicing a list.
- **Dates:** keep every date inside the world as a `datetime.date`. Convert to and from `"YYYY-MM-DD"` only at the edges: tool arguments, results, statuses, and `records()`.

### Bugs Must Crash

A bug in `world.py` (a missing function, a `.lower()` on a `Decimal`, a wrong key) must raise, so the dry run sees the traceback and the code gets fixed before any agent runs. Do not hide crashes:

- Only the three parsing helpers (money, integer, date) may use `try/except`, and they may catch only `ValueError`, `InvalidOperation` and `TypeError`. The runner rejects any `except Exception`, `except BaseException` or bare `except` before it even runs the file.
- No `try/except` around tool dispatch in `call_tool`, and no catch-all result such as `"That didn't work: ..."`.
- Every name in `tools(agent)` must have a working implementation. An unknown tool name is a bug, not a message.

## The interface the runner calls

`world.py` is one Python file that uses only the standard library. It must not read or write files, use the network, or start processes. It keeps its state in module globals. The runner calls these functions:

```python
def start() -> str:
    """Set up the first day's entities, contracts, and historical rows. Return START as "YYYY-MM-DD"."""


def agents_today() -> list[str]:
    """Ids of the agents that take a turn today."""


def tools(agent: str) -> list[dict]:
    """The tools this agent may call today. Each is
    {"name": ..., "entity": <whose tool it is>, "description": ..., "input_schema": <JSON schema object>}.
    Names match ^[a-zA-Z0-9_-]{1,64}$ and are unique within the list."""


def call_tool(agent: str, name: str, args: dict) -> str:
    """Run the call. Return a plain result, or a plain reason for a rejection or delay."""


def status(agent: str) -> str:
    """What this agent sees at the start of today: the date and day of week (and whether today
    is a bank holiday), its contract terms, balances and pending items it can see, open bills,
    deadlines, messages received, and recent events. Keep it under about 4,000 characters."""


def next_day() -> str | None:
    """Advance the clock by one day. If today was the main prompt's last day, return None.
    Otherwise increment the date and return the new date as "YYYY-MM-DD"."""


def records() -> dict:
    """Each institution's records: {institution: {table: [row, ...]}}, rows as flat dicts."""
```

Every agent id that `agents_today()` returns must be a key in `prompts.json`.

## Output

Reply with exactly these two tags:

<world.py>
...
</world.py>
<prompts.json>
...
</prompts.json>
