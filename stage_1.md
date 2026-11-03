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

An LLM writes the world as code, as close to how real economies work as it can:

- **Entities:** people, businesses, banks, processors, payroll providers, merchants.
- **Actors:** each entity acts through an agent (a role and a prompt), automated code it runs, or both. Routine work is code (settling a payment after two days, charging monthly interest, pulling autopay); judgment is an agent (holding a suspicious payout, chasing a late invoice, paying rent late).
- **Tools:** each entity's tools are what others can do with it (check a balance, send a wire, send a message). Who may call which tool follows the world's own rules.
- **Institutions:** each keeps its own ledger, rules and contracts.
- **The first day:** balances, contracts in force, money in transit, open bills.

## Simulate

Day by day, from the first day to the last:

1. Each entity's automated code runs.
2. Agents act by calling other entities' tools.
3. The world's code allows, rejects or delays each call.
4. The runner logs every call.

## Judge

At the end, an LLM reads the main prompt, the generated code, the call log and each institution's records. It decides whether the generated world and the simulation made a real economy for this business. For each finding it says what is missing or implausible, quotes the calls and records behind it, and says whether the code or the agents caused it.

## Improve

The findings go into the prompts for generating the world and for the agents, and the loop runs again.

## Runner and world

The world's code answers the runner's questions:

- Who are the agents, and what are their prompts?
- What tools does this agent have today?
- Run this tool call.
- Move to the next day.
