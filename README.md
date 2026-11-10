# worldgen: a financial world generator

`worldgen` creates realistic synthetic financial data. It simulates a business as a world of LLM agents (founders, employees, customers, vendors, banks) and records what they do the way real institutions would. The output is the records a business would actually have: bank transactions, card transactions, payment processor charges and payouts, and payroll entries.

> **Status:** early build. The runner generates a world from a prompt and simulates it day by day. The evaluation suite is designed in [`docs/EVALS.md`](docs/EVALS.md) but not built yet. See [Where we are](#where-we-are).

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
    the agents with something to do today act by calling other entities' tools
    the world's code checks each call, then allows, rejects or delays it
    the clock moves to the next day
    |
evaluate (not built): are the books right, and is reconciling them hard enough to matter?
```

**The runner holds no business logic.** Everything about a world comes from the LLM that writes it:

- **`world.py`** holds the entities, each institution's own ledger, rules and contracts, the tools each entity offers others, and the state on the first day: balances, contracts in force, money in transit, open bills. It has no daily loop of its own: `next_day()` only moves the clock.
- **`prompts.json`** holds the agents. Every actor is one: customers, vendors, staff, and the institutions themselves (banks, processors, payroll providers). Each has a role, habits, and starting plans and notes. A processor agent settles matured charges and sends the daily payout; a customer agent pays late.

**The world runs in its own process.** `world.py` gets no API keys. On macOS it also runs under `sandbox-exec`, with no network access and write access only to its run folder. On other systems there is no sandbox, and the runner prints a warning.

**Agents learn inside a run.** A rejected or delayed call comes back with a plain reason and the numbers that matter, so the agent can adjust and try again. Each turn shows the agent its status today, its last few days of calls, and its memory: dated plans that stay until marked done, and dated notes. The agent changes both with a built-in `memory` tool.

## Design principles

- **The runner is domain-neutral.** It never names an institution, industry or payment method. A bike shop and a trucking company differ only in their prompt.
- **Agents decide, code keeps the books.** Every money movement starts with an agent's tool call. The world's code checks the rules and the arithmetic and writes each institution's records.
- **Friction emerges, never hardcoded.** Lags, batching and cutoff mismatches come from how the channels work and what agents choose, not from special-case rules.
- **Institutions are good-enough approximations.** A world models what shows up in an institution's records, not every internal step.
- **Coverage, not exact numbers.** A world matches its prompt when it shows the same kinds of events and stories, not the same amounts or dates.
- **Runs are non-deterministic by design.** Two runs of the same prompt can differ, and both must hold up.

## Run it

```
uv sync
uv run pytest -q                                                  # offline tests
cp .env.example .env                                              # then add your OpenRouter key
uv run --env-file .env worldgen run targets/bike_shop/PROMPT.md
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
  memory.json        each agent's plans and notes after the last day
  run.json           status, models, counts and cost
  world_stderr.log   anything the world's code printed
```

## View runs

```
uv run python ui/server.py              # http://127.0.0.1:8765
uv run python ui/server.py --port 8080
```

A dropdown picks any run under `worlds/`, grouped by prompt. Each run has tabs for its days (every agent call with its reason, arguments, result and memory), agents, institution records, dry-run tries, `world.py`, the prompt and the raw files. A run still in progress refreshes itself.

## Prompts

Every prompt lives in [`targets/`](targets/), one folder per business. [`targets/README.md`](targets/README.md) lists them all, and [`targets/GRID.md`](targets/GRID.md) sorts them by finance cycle and difficulty. Three to start with:

| Prompt | What it is |
|---|---|
| [`targets/bike_shop/PROMPT.md`](targets/bike_shop/PROMPT.md) | Spoke & Chain, a one-room bike repair shop in Eugene, Oregon. The smallest world, for quick runs. |
| [`targets/studio_payments/studio_payments_7day.md`](targets/studio_payments/studio_payments_7day.md) | Booking and payments software for 280 fitness studios on Stripe Connect, first week of 2025. |
| [`targets/saas_startup/PROMPT.md`](targets/saas_startup/PROMPT.md) | A small B2B SaaS company, 2021-2022, modeled on the [AccountingBench](https://accounting.penrose.com/) company. |

## Where we are

**Built**
- The runner in [`src/worldgen/`](src/worldgen): generate, the sandboxed dry run, and the day loop.
- The local run viewer in [`ui/`](ui).

- 15 businesses in [`targets/`](targets/), most modeled on public filings.

**Next**, from [`docs/EVALS.md`](docs/EVALS.md)
1. An answer key that links every money movement to the rows it produced in each institution.
2. `worldgen eval`: Python checks on the books, the contracts and calendars, and how hard the records are to reconcile.
3. A baseline suite: each target run three times, with a scorecard per run.

## Tech stack

Python 3.12, `typer` and `httpx2`. A world's code uses only the standard library and keeps money in `Decimal`. Tests use `pytest` with a scripted fake model, so they run offline.
