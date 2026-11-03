# Stage 1

## Goal

From a main prompt that describes one business, generate a world, simulate its economy with thinking agents, and judge at the end whether it was a real economy. The judge's findings improve the next run.

## Before any world

Only the runner exists. It:

- asks an LLM to generate the world
- runs the world's code in a sandbox
- each day, calls the agents the world says act, with the tools the world gives them
- logs every tool call: who called what, on whom, why, and the result
- calls the judge at the end
- saves the generated code, the call log, each institution's records and the judge's findings

Nothing else is predefined.

## Generate

An LLM writes the world in two parts so code and agent prompts can be updated separately:

- **`world.py` (the rules and automation):**
  - **Entities:** people, businesses, banks, processors, payroll providers, merchants.
  - **Automated work:** routine mechanics that run in code (settling a payment after two days, skipping weekends and holidays, charging monthly interest, pulling autopay).
  - **Tools:** each entity's tools are what others can do with it (check a balance, send a wire, send a message). Who may call which tool follows the world's own rules.
  - **Institutions:** each keeps its own ledger, rules and contracts.
  - **The first day:** balances, contracts in force, money in transit, open bills.
- **`prompts.json` (the agents):**
  - **Actors:** each entity that makes judgment calls acts through an agent (a role, habits, and a starting notepad). Judgment is an agent (holding a suspicious payout, chasing a late invoice, paying rent late, swiping a company card on a weekend trip).

## Simulate (learning inside a run)

Day by day, from the first day to the last:

1. Each entity's automated code runs (`next_day()`).
2. The runner wakes the agents that need to act today.
3. Agents act by calling other entities' tools (`call_tool(...)`).
4. The world's code allows, rejects or delays each call.
5. The runner logs every call.

To help agents adapt from day to day without blowing up the prompt:

- **Clear rejection reasons, not scores:** when a tool call fails or is delayed, the world's code returns a plain reason with the relevant numbers (for example, that checking holds `$14,200`, payroll needs `$25,000`, and `$1,000,000` sits in Treasury with a 1-business-day transfer delay) so the agent can adjust and try again.
- **A short notepad per agent:** instead of seeing the full call log for the whole year, each agent keeps a short notepad of active plans and unresolved items that it updates at the end of its turn, alongside the last few days of its own tool calls and rejections.
- **A daily status header:** each turn shows the agent's current balances, open bills, incoming messages, and how long it has been since key events (such as trips, experiments, or disputes) so agents pace one-off stories naturally across the year instead of firing them all in the first week.

## Judge

At the end, fast Python checks run first to flag any crashes, empty tables, broken `Decimal` formatting, or running-balance math errors. Then an LLM Judge reads the main prompt, `world.py`, `prompts.json`, the Python check summary, the call log and each institution's records.

It decides whether the generated world and the simulation made a real economy for this business. Each finding has four parts:

- **What happened:** what is missing, implausible, or broken.
- **Evidence:** exact quotes from the call log and institution records behind it.
- **Blame (`code` vs. `agent:<id>`):** whether `world.py` caused it (missing tool, instant settlement with no delay, broken ledger rule) or a specific agent's prompt in `prompts.json` caused it (the tool worked, but the agent never used it or acted implausibly).
- **Fix rule:** a general rule to fix the behavior, written as a habit or mechanism rather than hardcoding a single date or amount.

## Improve (learning between runs)

The findings go into the prompts for generating the world and for the agents, and the loop runs again:

- **Targeted updates:** findings blamed on `code` go to the code optimizer to patch `world.py`. Findings blamed on `agent:<id>` go to the prompt optimizer to rewrite only that agent's entry in `prompts.json`.
- **Clean rewrites, not append-only lists:** when updating an agent's prompt, the optimizer rewrites and compresses the prompt cleanly instead of tacking on a growing list of complaints.
- **Keep the best versions:** every run is saved (`run_1`, `run_2`, ...). If a patch in a new run breaks a working ledger or story from an earlier run, the loop rolls back or combines the working `world.py` from one run with the improved `prompts.json` from another.

## Runner and world

The world's code answers the runner's questions:

- Who are the agents, and what are their prompts?
- What tools does this agent have today?
- Run this tool call.
- Move to the next day.

## Training loop and experiments

### Three speeds per business

Running a full year of daily agent turns is expensive when `world.py` still has bugs, so each world is trained in three phases. A run always covers exactly the prompt's time range, so a phase sets its horizon by setting the prompt's end date:

| Phase | Horizon | What runs | What updates | Goal before moving on |
| :--- | :--- | :--- | :--- | :--- |
| **1. Smoke test** | **7 days:** the end date is 6 days after the start date (includes a weekend and month start) | Automated code + 1–2 test turns per agent | `world.py` only | Zero crashes; Day 1 in-transit items settle; tools check permissions and return clear rejection reasons. |
| **2. Short window** | **35 days:** the end date is 34 days after the start date (crosses a month-end cutoff) | Full daily loop + Judge + Improve | `world.py` and `prompts.json` | Statements close; payouts and card swipes cross month-end cutoffs; routine bills, payroll, and at least one messy story work. |
| **3. Full run** | **The prompt's full time range** (12–18 months) | Full daily loop + Judge + Improve | Mostly `prompts.json` (and small `world.py` fixes) | Annual scale, cash trajectory, and long-horizon stories match the business prompt. |

### Experiments

1. **Single-world improvement (within one business):**
   Run the loop for 5 iterations on [`TARGET_EXAMPLE.md`](TARGET_EXAMPLE.md) (SaaS) and [`targets/brewery_taproom/PROMPT.md`](targets/brewery_taproom/PROMPT.md) (brewery), comparing:
   - **One-shot baseline:** generate and simulate once with no Judge feedback.
   - **Naive rewrite:** the Judge writes free-form critique and the generator rewrites the whole world from scratch.
   - **Split blame + best-version pool:** the Judge splits blame between `world.py` and `prompts.json`, patches only the broken part, and keeps the best run so far.

2. **Cross-world generalization (improving the generator across businesses):**
   Split the 8 business prompts into a training set and a holdout test set:
   - **Training set (5 businesses):** [`TARGET_EXAMPLE.md`](TARGET_EXAMPLE.md) (SaaS), [`examples/trucking/PROMPT.md`](examples/trucking/PROMPT.md) (trucking), [`targets/brewery_taproom/PROMPT.md`](targets/brewery_taproom/PROMPT.md) (brewery), [`targets/dtc_brand/PROMPT.md`](targets/dtc_brand/PROMPT.md) (DTC brand), and [`targets/food_pantry/PROMPT.md`](targets/food_pantry/PROMPT.md) (food pantry).
   - **Holdout test set (3 unseen businesses):** [`targets/pt_clinic/PROMPT.md`](targets/pt_clinic/PROMPT.md) (PT clinic), [`targets/roofing_contractor/PROMPT.md`](targets/roofing_contractor/PROMPT.md) (roofing contractor), and [`targets/vacation_rentals/PROMPT.md`](targets/vacation_rentals/PROMPT.md) (vacation rentals).
   - Distill recurring Judge findings from the 5 training worlds into general instructions in the base world-generator prompt, then test how well it builds the 3 holdout businesses on their very first run.

### What each run measures

Every run records four checks in `run.json`:

1. **Ledger health:** does the code finish without crashing, conserve money, and export valid tables for each institution?
2. **Story and event coverage:** what share of the target prompt's stories and event types show up in the institution tables with matching call-log events?
3. **Scale and cash trajectory:** are revenue, payroll, debt service, and ending cash in the right ballpark for the business prompt?
4. **Judge defect count:** how many code bugs or implausible agent behaviors does the Judge flag from run 1 to run $N$?
