# Evaluations for `worldgen`

> **Status: design only.** None of this is built. `truth()`, `eval.py`, `review.md`, `eval.json` and the `Expectations` blocks named below do not exist in the code yet. Paths are relative to the repo root.

End Close reconciles records across a payment processor, a bank, and a company's own ledger, then works the timing, batching, and fee-netting differences. In `worldgen`, **every actor is an agent in `prompts.json`** — customers, merchants/studios, vendors, internal staff, and the institutions themselves (processors, banks, networks, accounting systems, payroll providers) — and **`world.py` is the shared state, contract registry, and ledger toolset** (`next_day()` only advances the calendar date).

For generated worlds to be useful to End Close, an evaluation suite must answer four questions on every run:

1. **Are the books right?** Every balance comes from rows, running balances recompute, grouping rows equal the sum of their parts, and statuses agree with dates.
2. **Do the agents follow real contracts and calendars?** Institutions and customers act according to their contracts and published rail rules (2-day card holds, 1–2 day payouts, no bank postings on weekends/holidays, varied customer and merchant personas).
3. **Is reconciling it hard enough to matter?** A naive amount-and-date matcher leaves a realistic residual of reconciliation items (70–95% recall from batching, cutoff timing, and fee netting), not 100% trivial 1-to-1 matches and not broken noise.
4. **Is every difference explainable?** Every difference between two institutions traces back to an agent's tool call (or Day 1 in-flight history) in the world's answer key (`truth()`). Zero mismatches come from code bugs or phantom balances.

---

## 1. Prerequisite: The `truth()` Answer Key and Record Conventions

Without a ground-truth link across institutions, an evaluator can only guess which processor transactions belong to which bank deposit or why a company invoice differs from a processor net transfer. Every world therefore implements an eighth runner function, `truth()`, alongside strict record conventions in `records()`.

### Runner Interface Addition

```python
def truth() -> dict:
    """Return the hidden answer key for grading and reconciliation:
    {
        "movements": [
            {
                "id": "mv_0001",
                "kind": "member_payment",          # or payout, refund, fee, subscription, bill...
                "date": "2025-01-01",
                "amount": "129.00",
                "records": {
                    "stripe.balance_transactions": ["txn_0001", "txn_0002", "txn_0003"],
                    "stripe.connected_transactions": ["ctxn_0001"],
                    "repflow_db.invoices": ["inv_0001"],
                },
                "cause": {
                    "kind": "agent",               # "agent" | "history"
                    "agent": "member_cohort_renewals",
                    "tool": "pay_membership",
                    "detail": "Jan 1 monthly renewal under studio contract",
                },
            },
            ...
        ],
        "exceptions": [
            {
                "id": "ex_0001",
                "pair": ["stripe", "bank"],        # the two sources that fail naive 1-to-1 matching
                "category": "fee_netting",         # cutoff_timing | bundled_payout | holiday_weekend_delay |
                                                   # fee_netting | partial_refund | instant_payout_fee
                "records": {
                    "stripe.balance_transactions": ["txn_0812"],
                    "stripe.payouts": ["po_0002"],
                    "bank.operating_transactions": ["btx_0004"],
                },
                "amount": "412.50",
                "cause": {
                    "kind": "agent",               # "agent" | "history"
                    "agent": "stripe",
                    "tool": "charge_connect_invoice",
                    "detail": "Stripe netted December Connect invoice ($412.50) from platform balance",
                },
                "explanation": "Stripe deducted its $412.50 December Connect invoice from the platform "
                               "balance on 2025-01-02 before sweeping the daily payout.",
            },
            ...
        ],
    }
    """
```

The runner saves `truth()` to `truth.json` in the run directory at the end of `simulate()` and checks its invariants at the end of `dry_run()`.

### Four Bookkeeping Rules Required in `generate.md`

To let Layer B check the books without hardcoding any particular business:

1. **Every balance comes from rows:** No ledger or account may start with a non-zero balance unless prior-period or opening transaction rows in `records()` sum to that number.
2. **Running balances recompute:** Every row in a sequential account ledger carries `balance_after`, and `balance_after[i] == balance_after[i-1] + signed_amount[i]`.
3. **Grouping rows list their children and equal their sum:** Any row that groups other rows (a processor payout, a batch deposit, a statement, a remittance) must carry `item_ids: [...]` naming the child row IDs in the source table (and/or each child row carries `payout_id`), and the parent's net amount must equal the exact `Decimal` sum of its children.
4. **Statuses agree with dates:** Rows that transition over time (`pending` -> `available` -> `paid` / `posted`) carry both their creation date (`date` or `created`), their settlement/availability date (`available_on`, `arrival`, or `posting_date`), and their current `status`.

---

## 2. The Seven Evaluation Layers

| Layer | What It Checks | Grader | Needs `truth()`? |
|---|---|---|---|
| **A. Harness health** | Passed cleanly vs. kept with warnings; fix rounds used; wall time and USD cost; tool calls that crash vs. rejections that give a reason | Code (`run.json`, `log.jsonl`) | No |
| **B. Books** | Every balance comes from rows; running balances recompute; grouping rows equal the sum of their parts; cross-institution settlement delays $\ge 0$ and within plausible windows; statuses agree with dates; no dangling foreign-key IDs | Code (`records.json`) | No (enhanced by `truth()`) |
| **C. Contract & rail realism** | Institution agents obey rail rules (card 2-day hold, ACH settlement windows, no weekend/holiday bank postings); customer/counterparty agents produce diverse amounts and payment mix matching the target's `Expectations` block | Code (`records.json` vs. target's `Expectations` block) | No |
| **D. Reconciliation** | Naive matcher recall/precision across source pairs (`processor <-> bank`, `processor <-> company_db`, `company_db <-> gl`); exception diversity by root cause; **0 unexplained mismatches** | Code + `truth.json` | **Yes** |
| **E. Pure-agent emergence** | `next_day()` only advances the clock (no hidden RNG loops or hardcoded dates in `world.py`); all institutions, customers, and staff act as agents in `prompts.json`; every post-start movement and exception traces to an agent tool call in `log.jsonl` | Code (`world.py` AST + `prompts.json` + `truth.json` + `log.jsonl`) | **Yes** |
| **F. Coverage** | Every event kind listed in the target prompt's Section 7 ("Kinds of events") appears in `records.json` with concrete row IDs as evidence | LLM judge (calibrated against human verdicts) | No |
| **G. Agents** | Share of tool calls that succeed; **0 Python runtime errors surfaced as tool rejections**; wasted/repeated identical calls; notepad continuity | Code (`log.jsonl`) | No |

---

### Layer A: Harness Health (Code Grader)

Reads `run.json` and `log.jsonl`:

- **`clean_generation` (pass/fail):** `run.json["status"] == "finished"` and `generate_warnings` is empty. Worlds kept via fallback (`generate_kept`) fail this check.
- **`fix_rounds_used` (metric):** Number of fix attempts after Attempt 1 (`0` to `fix_rounds`).
- **`edit_match_rate` (metric):** Share of fix attempts where `<edit>` blocks applied cleanly without `"No edits were applied"`.
- **`simulation_crashes` (pass/fail):** `crashes == 0` and `failed_turns == 0` in `run.json`.
- **`cost_usd` and `wall_seconds` (metrics):** Tracked by stage (`generate`, `fix`, `review`, `simulate`).

---

### Layer B: Books Invariants (Code Grader, Domain-Neutral)

Runs both **inside the `dry_run()` fix loop** (returning exact offending row IDs to the generator on failure) and in the final evaluation over `records.json`:

1. **No phantom opening balances:**
   For every ledger table with a `balance_after` field or an account summary balance, the first row's prior balance must be `0.00` unless preceded by explicit historical rows, and every subsequent row must satisfy:
   $$\text{balance\_after}_i = \text{balance\_after}_{i-1} + \text{signed\_amount}_i$$
2. **Grouping rows equal the sum of their parts:**
   For every grouping table (e.g., payouts, batch deposits, statements, remittances) linked to a detail table via `payout_id`, `batch_id`, `statement_id`, or `item_ids`:
   - Every settled/paid or in-transit group row must have $\ge 1$ child item (`len(items) > 0`). A payout of `$44,618.22` with 0 items fails immediately.
   - The sum of the child items' net amounts must equal the group row's amount to the cent (`Decimal("0.00")`):
     $$\sum_{c \in \text{children}(g)} \text{amount}(c) = \text{amount}(g)$$
3. **Status agrees with dates:**
   At the end of the run (`end_date`):
   - Any row whose settlement/availability date (`available_on`, `arrival`, `posting_date`) is $\le \text{end\_date}$ on a business day must not remain in `status == "pending"` (or `"in_transit"` past its `arrival` date) once the institution agent has taken its turn.
   - Any row whose settlement/availability date is $> \text{end\_date}$ must still be `"pending"` or `"in_transit"`, never `"paid"` or `"posted"`.
4. **Cross-institution money conservation & non-negative lag:**
   When money moves from institution $A$ to institution $B$ (linked by reference ID or `truth()["movements"]`), the arrival/posting date at $B$ must be $\ge$ the submission/creation date at $A$, within a plausible window ($0 \le \Delta \text{days} \le 10$ for standard rails), and the amounts must match (or differ only by an explicit fee row recorded at $A$ or $B$).
5. **Referential integrity (no dangling IDs):**
   Every foreign key field in any table (`charge`, `invoice`, `studio_id`, `member_id`, `payout_id`, `bank_id`, `ref`) that references a record ID must resolve to an existing row ID in the target table.

---

### Layer C: Contract & Rail Realism vs. Target Expectations (Code Grader)

Compares `records.json` against the structured `Expectations` block at the end of the target prompt:

1. **Role & persona representation:** `prompts.json` defines agents for each institution, internal role, and customer/counterparty archetype described in the prompt, and those agents actively execute tool calls during `simulate()`.
2. **Payment method mix:** Share of each payment rail (e.g., card vs. ACH) falls within the target's stated band.
3. **Settlement & payout delays (Institution agent accuracy):**
   - Card charges: `available_on - created == 2` business days†.
   - Standard ACH debits: `available_on - created` in `3..5` business days.
   - Payouts: `arrival - submitted` in `1..2` business days† (`0` days for instant payouts†).
   - Holiday & weekend cutoffs: bank agents post `0` standard ACH/payout settlements on weekends and federal holidays†.
4. **Behavioral diversity across customer & merchant agents:** Different customer and merchant agents exhibit distinct spending/pricing behavior (big spenders vs. casual buyers, flagship merchants vs. small merchants, 1st/15th renewal surges) rather than every agent calling the exact same tool with the exact same dollar amount.

---

### Layer D: Reconciliation — The End Close Core (Code + `truth()`)

Evaluates each reconciliation pair declared in the target's `Expectations` block:
- **Pair 1 (`processor <-> bank`):** e.g., Stripe platform payouts & balance transactions $\leftrightarrow$ Operating bank deposits & debits.
- **Pair 2 (`processor <-> company_db`):** e.g., Stripe charges, refunds, and connected transfers $\leftrightarrow$ Repflow database invoices and studio payable ledger.
- **Pair 3 (`company_db / bank <-> gl`):** e.g., Bank transactions & Stripe summaries $\leftrightarrow$ Xero bank feed, reconciliations, and journal entries.

#### 1. Naive Baseline Matcher Score
Run a standard heuristic matcher over each pair (exact net amount match within $\pm 3$ business days, or exact reference string match):
- Compute **Precision** and **Recall** against `truth()["movements"]`:
  - **Target recall band: `70%–95%`**.
  - **$> 95\%$ recall:** Too clean — lacks batching, fee netting, or cutoff splits.
  - **$< 50\%$ recall:** Broken — amounts, signs, or dates do not line up at all.

#### 2. Exceptions by Root Cause
Every item that fails the naive matcher (or where two sources differ due to bundling, fees, or cutoffs at `end_date`) is looked up in `truth()["exceptions"]`:
- **Root-cause diversity:** Count distinct reconciliation categories present in the run (`cutoff_timing`, `bundled_payout`, `holiday_weekend_delay`, `fee_netting`, `partial_refund`, `instant_payout_fee`). Must meet the target's minimum distinct causes (e.g., $\ge 4$ in a 7-day run, $\ge 5$ in a 60-day or full-year run).

#### 3. Unexplained Mismatches (The Zero-Bug Gate)
$$\text{unexplained\_mismatches} = \left|\{\text{discrepancies between paired tables}\} \setminus \text{truth()["exceptions"]}\right|$$
- **Hard requirement: `unexplained_mismatches == 0`**.
- Any discrepancy between processor and bank, or between processor and company DB, that is not accounted for by an explicit entry in `truth()["exceptions"]` with a valid cause and matching child rows is a **generator bug** (such as a phantom opening payout, a charge that forgot to write an invoice row, or a sign flip).

---

### Layer E: Pure-Agent Emergence (Code + `truth()`)

Verifies that the simulation is genuinely driven by agents acting on their contracts as the clock advances:

1. **Clock-only `next_day()`:** AST check on `world.py` confirms `next_day()` only advances `DAY` and does not call helper functions that mutate ledger tables or run `random` draws.
2. **Zero hardcoded event dates (`fixed_dates == 0`):** AST check on `world.py` confirms no comparisons of the current day against literal dates (`day == date(2025, 1, 2)`).
3. **100% agent or history attribution:** Every entry in `truth()["movements"]` and `truth()["exceptions"]` has `cause["kind"] in ("agent", "history")`:
   - For every post-start movement or exception (`cause["kind"] == "agent"`), the cited `(date, agent, tool)` call must exist in `log.jsonl`.

---

### Layer F: Coverage (LLM Judge, Calibrated)

An LLM judge reads Section 7 ("Kinds of events") of the target prompt alongside table summaries and query results from `records.json`:
- For each bullet item in Section 7 that is eligible within the run's time window (e.g., 7-day vs. full-year), the judge outputs `PRESENT` or `MISSING` and must cite **at least one exact `(table, row_id)`** from `records.json`.
- **Anti-hallucination check:** A Python post-check verifies that every `(table, row_id)` cited by the LLM judge actually exists in `records.json` and matches the cited fields. Any citation to a non-existent row invalidates the `PRESENT` verdict.

---

### Layer G: Agent Tool-Use Health (Code over `log.jsonl`)

Inspects every `{"type": "call", ...}` entry in `log.jsonl`:

1. **Zero Python runtime errors in tool results (`python_errors_as_rejections == 0`):**
   Scans every tool result for leaked Python exception strings:
   `TypeError`, `ValueError`, `KeyError`, `AttributeError`, `IndexError`, `NameError`, `UnboundLocalError`, `ZeroDivisionError`, `bad operand type`, `slice indices must be`, `object has no attribute`, `is not subscriptable`, `cannot access local variable`.
   **Hard requirement: `0` matches.**
2. **Tool call success rate:** Share of calls that succeed vs. domain rejections (e.g., insufficient balance, unknown query). Target: $\ge 80\%$ valid execution rate.
3. **Wasted / stuck loop calls:** Share of calls where an agent repeats the exact same `(tool, args)` on the same turn or across consecutive turns after an error. Target: $< 5\%$.

---

## 3. Scoring and Suite Aggregation

### Per-Run Scorecard (`eval.json`)

Each evaluated run writes `eval.json` inside its run directory with:
- **`passed` (bool):** `True` only if all hard gates pass:
  - Layer A: `clean_generation == True` and `simulation_crashes == 0`
  - Layer B: `books_errors == 0` (0 phantom balances, 0 grouping sum mismatches, 0 stale statuses, 0 dangling references)
  - Layer D: `unexplained_mismatches == 0` and `naive_recall` in `[0.70, 0.95]`
  - Layer E: `fixed_dates == 0` and `clock_only_next_day == True`
  - Layer G: `python_errors_as_rejections == 0`
- **`layer_scores` (`A`–`G`):** Individual pass/fail flags and continuous metrics for each layer.

### Suite Aggregation Across 3 Trials (`pass^3`)

Because `worldgen` is non-deterministic across generation and simulation runs, a change is evaluated on **3 independent trials per target** (`trials = 3`):
- **`pass^3` (all-trials pass rate):** A target passes only if **all 3 trials** (`3/3`) pass the hard gates. End Close cannot use a generator that produces valid books on 2 out of 3 runs and a phantom payout on the 3rd.
- **Suite summary table:** Reports `pass^3` across the suite alongside the 3-trial mean and worst-case (`min`/`max`) for continuous metrics (naive recall, exception root-cause count, realism band pass rate, cost, and wall time).

---

## 4. Target Suite Design (5 Prompts)

To prevent overfitting the harness to Stripe Connect, the suite spans **5 prompts** (3–4 payment-heavy targets with different payment rails, plus 1–2 small regression worlds), with **1 payment target strictly held out**:

| Target | Role | Payment Rails & Institution Agents | Status |
|---|---|---|---|
| [`targets/studio_payments`](targets/studio_payments/) | **Dev / Primary** | Stripe Connect agent, Pikes Peak Bank agent, Xero agent, studio owner agents (climbing, yoga, pilates, boxing), member agents (card & ACH cohorts, 1st/15th renewers, clean refund requesters), Repflow staff agents | **Done** (`Expectations` added) |
| `targets/payroll_fintech` *(to write)* | **Dev / Core End Close** | Outbound ACH credits (payroll/bill pay), settlement cutoffs, wires, FBO customer-funds account at a sponsor bank vs. internal sub-ledger | **Next** (closest to End Close's customers) |
| `targets/property_manager` *(to write)* | **Dev / Multi-Rail** | Resident ACH debits, paper checks deposited in mobile/lockbox batches, security-deposit & rent trust accounts, management fees netted from monthly owner payouts | **Next** |
| `targets/multi_processor_app` *(to write)* | **Held-Out Test** *(never tune on this)* | Consumer subscription app collecting via Stripe + PayPal + Apple/Google app-store monthly net payouts (after 15%/30% commission), FX conversion, cross-processor refunds | **Next (Held Out)** |
| [`targets/bike_shop`](../targets/bike_shop/) & [`targets/brewery_taproom`](../targets/brewery_taproom/) | **Regression check** | Small worlds (POS batches, cash drawers, vendor terms, payroll) to ensure harness changes hold across simple and complex businesses | **Done** (add `Expectations`) |

---

## 5. Implementation Order

1. **Spec & Pure-Agent Prompts (Done):**
   - `EVALS.md` (this document), `src/worldgen/generate.md`, `src/worldgen/review.md`, and `## 8. Expectations` in `targets/studio_payments/`.
2. **Phase 1 Eval Code + Harness Fixes (No `truth()` required yet):**
   - Implement Layers **A**, **B**, **C**, and **G** in `src/worldgen/eval.py`.
   - Wire Layer **B** (book checks: no phantom opening balances, grouping rows sum to parts, status agrees with dates), Layer **E** (`next_day()` clock-only check), and Layer **G** (no Python runtime errors in tool outputs) directly into `dry_run()` in `src/worldgen/generate.py`.
3. **Phase 2 `truth()` + Layers D, E, and F:**
   - Add `truth()` to `src/worldgen/generate.md`, `src/worldgen/host.py`, `src/worldgen/generate.py`, and `src/worldgen/simulate.py` (saving `truth.json`).
   - Implement Layer **D** (naive matcher + root-cause tally + `unexplained_mismatches == 0`), Layer **E** (agent tool-call cause verification), and Layer **F** (calibrated LLM coverage judge).
4. **New Payment Targets:**
   - Author `targets/payroll_fintech`, `targets/property_manager`, and the held-out `targets/multi_processor_app`, each with its `SOURCES.md` and `## 8. Expectations` block.
5. **Baseline Suite & One-Commit Experiments:**
   - Run the baseline suite (`5 prompts × 7 days × 3 trials`).
   - Land each harness or prompt improvement as a single commit with a before-and-after scorecard table.
