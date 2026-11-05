# worldgen: a financial world generator

`worldgen` creates realistic synthetic financial data. It simulates a business as a world of LLM agents (founders, employees, customers, vendors, banks) and records what they do the way real institutions would. The output is the records a business would actually have: bank transactions, card transactions, payment processor charges and payouts, and payroll entries.

> **Status:** early build. The runner generates a world from a prompt and simulates it day by day. The judge and the improvement loop are not built yet. [`stage_1.md`](stage_1.md) is the design. See [Where we are](#where-we-are).

## Why

Real financial data is private, and data generated from rules looks too clean. Real exports are messy because of how money moves and how people behave:

- A customer pays on March 30, but the payout arrives on April 1, so the March bank statement leaves it out.
- Forty card charges, fees and refunds show up in the bank as one line: `Deposit - STRIPE`.
- The CEO buys something personal on the company card and leaves the memo blank.
- A customer pays late, short-pays, then sends a corrective wire.
- The same merchant appears as `AMZN Mktp US*2K4L` one month and `Amazon.com` the next.

You can't get this mess by inventing tidy journal entries and working backwards. `worldgen` builds data from the money's side instead. People and businesses make decisions, money moves through channels with real delays, and each institution records only what it would see.

## How it works

```
main prompt  (one business: "a one-room bike repair shop in Eugene, Oregon ...")
    |
generate: an LLM writes the world as code (world.py) and its agents (prompts.json)
    |
dry run: the world's code runs every day, every tool is called with plain and messy
         arguments; a crash goes back to the LLM, which sends edits to fix it
    |
simulate, day by day from the prompt's start date to its end date:
    the world's automated code runs (settlements, autopay, interest, statement closes)
    the agents with something to do today act by calling other entities' tools
    the world's code allows, rejects or delays each call
    |
judge (not built): did this make a real economy for this business?
    |
improve (not built): findings patch world.py or rewrite one agent's prompt, then run again
```

**The runner holds no business logic.** Everything about a world comes from the LLM that writes it:

- **`world.py`** holds the entities, each institution's own ledger, rules and contracts, the routine work that runs in code, the tools each entity offers others, and the state on the first day: balances, contracts in force, money in transit, open bills.
- **`prompts.json`** holds the agents. Each entity whose choices need judgment acts through an agent with a role, habits and a starting notepad: holding a suspicious payout, chasing a late invoice, paying rent late.

**The world runs in a sandbox.** `world.py` runs in its own process with no network access, no API keys and write access only to its run folder (macOS `sandbox-exec`).

**Agents learn inside a run.** A rejected or delayed call comes back with a plain reason and the numbers that matter, so the agent can adjust and try again. Each turn shows the agent its status today, its last few days of calls, and a short notepad it rewrites at the end of every turn.

## Design principles

- **The runner is domain-neutral.** It never names an institution, industry or payment method. A bike shop and a trucking company differ only in their prompt.
- **Agents decide, code keeps the books.** Judgment calls belong to agents. Routine mechanics and each institution's records belong to the world's code.
- **Friction emerges, never hardcoded.** Lags, batching and cutoff mismatches come from how the channels work and what agents choose, not from special-case rules.
- **Institutions are good-enough approximations.** A world models what shows up in an institution's records, not every internal step.
- **Coverage, not exact numbers.** A world matches its prompt when it shows the same kinds of events and stories, not the same amounts or dates.
- **Runs are non-deterministic by design.** Two runs of the same prompt can differ, and both must hold up.

## Run it

```
uv sync
uv run pytest -q                                                  # offline tests
uv run --env-file .env worldgen examples/bike_shop/PROMPT.md
```

A run covers exactly the time range written in the prompt. To run fewer days, shorten the prompt's range.

Models go through [OpenRouter](https://openrouter.ai/) by default, so `.env` needs `OPENROUTER_API_KEY`. `--world-backend claude` or `--agent-backend claude` sends that stage's calls through the [`claude` CLI](https://code.claude.com/docs/en/headless) instead, so whatever `claude` is logged in as pays: a Claude Pro/Max subscription (within its rate limits) or its API key. The cost in `run.json` is then the list-price equivalent, not a bill.

| Option | Default | What it does |
| --- | --- | --- |
| `--world-backend` | `openrouter` | Who answers the world-writing call: `openrouter` or `claude` |
| `--world-model` | `z-ai/glm-5.3`, or `opus` with claude | Writes the world |
| `--agent-backend` | `openrouter` | Who answers the agents' calls: `openrouter` or `claude` |
| `--agent-model` | `z-ai/glm-5.3-flash`, or `sonnet` with claude | Plays the agents |
| `--fix-rounds` | `5` | Times a crashing world goes back to be fixed |
| `--out` | `worlds/<prompt>/<time>_world-<model>_agents-<model>` | Where the run is saved |

## What a run produces

```
worlds/<prompt>/<time>_world-<model>_agents-<model>/      e.g. worlds/studio_payments_7day/20261105-183950_world-fable_agents-opus/
  world.py           the world's code
  prompts.json       the agents
  log.jsonl          every model call, tool call, rejection and crash, in order
  records.json       each institution's records after the last day
  notepads.json      each agent's notepad after the last day
  run.json           status, models, counts and cost
  world_stderr.log   anything the world's code printed
```

## View runs

```
uv run python ui/server.py              # http://127.0.0.1:8765
uv run python ui/server.py --port 8080
```

A dropdown picks any run under `worlds/`, grouped by prompt. Each run has tabs for its days (every agent call with its reason, arguments, result and notepad), agents, institution records, dry-run tries, `world.py`, the prompt and the raw files. A run still in progress refreshes itself.

## Example prompts

| Prompt | What it is |
|---|---|
| [`examples/bike_shop/PROMPT.md`](examples/bike_shop/PROMPT.md) | Spoke & Chain, a one-room bike repair shop in Eugene, Oregon. The smallest world, for quick runs. |
| [`TARGET_EXAMPLE.md`](TARGET_EXAMPLE.md) | A small B2B SaaS company, 2021-2022, modeled on the [AccountingBench](https://accounting.penrose.com/) company. |
| [`examples/trucking/PROMPT.md`](examples/trucking/PROMPT.md) | Ozark Ridge Freight, a six-truck carrier in Missouri, 2024. |

## Where we are

**Built**
- The runner in [`src/worldgen/`](src/worldgen): generate, the sandboxed dry run, and the day loop.
- The local run viewer in [`ui/`](ui).

**Next**, from [`stage_1.md`](stage_1.md)
1. The judge: fast Python checks, then an LLM that reads the run and writes findings blamed on `world.py` or on one agent.
2. Improve: findings patch `world.py` or rewrite one agent's prompt, keeping the best version of each.
3. The training loop: a 7-day smoke test, a 35-day window across a month-end, then the full range.

## Tech stack

Python 3.12, `typer` and `httpx2`. A world's code uses only the standard library and keeps money in `Decimal`. Tests use `pytest` with a scripted fake model, so they run offline.
