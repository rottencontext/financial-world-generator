# Repflow: booking software that moves money for 280 fitness studios (first 60 days)

This describes one business, its past and its first 60 days. Facts marked † come from published rules on how this money moves: Stripe's documentation for platforms and Nacha's rules for ACH settlement, as summarized by Stripe and by banks that publish them (see `SOURCES.md`). A † vouches for the fact it follows, not for the date or reason the story gives it. No single company stands behind this business. Its size, people and account numbers are invented.

This is a clean 60-day run of the order-to-cash world in `PROMPT.md`. Every member payment is honest, no one disputes a charge or commits fraud, every bank account is open and funded, and every staff member and webhook does its job on time. What is left are the mechanics of moving money through a payment facilitator across two full month-end closes, four payroll runs, and three federal holidays:

- destination charges split at once between Repflow's platform balance and each studio's connected account†;
- card payments that take 2 business days to become available† and ACH debits that take 3–4 business days;
- daily automatic payouts† that bundle hundreds of settled transactions into a single bank deposit and take 1–2 business days in transit†;
- three federal bank holidays — New Year's Day (Wednesday, January 1), Martin Luther King Jr. Day (Monday, January 20), and Presidents' Day (Monday, February 17) — plus weekends, when banks do not post†;
- three cross-month cutoffs (December 30–31 into January, January 30–31 into February, and February 27–28 into March)†;
- Stripe's monthly Connect account fee invoices (December's paid in January, January's paid in February) netted directly from the platform balance;
- clean full and partial refunds where support reverses the studio's proportional transfer†, instant studio payouts before studio payrolls with a 1% fee†, and new studios onboarding across January and February.

## 1. The business and the time frame

- **Business:** Repflow Inc., a software company in Denver, Colorado. Independent gyms, yoga and pilates studios, climbing gyms and boxing clubs use Repflow to sell memberships, class packs, drop-ins, personal training and retail. Repflow collects every payment through Stripe Connect and pays each studio its share.
- **Most of the money is not Repflow's.** A member pays the studio through Repflow. The payment lands in Repflow's Stripe platform account, and the studio's share moves at once to the studio's connected account, minus Repflow's application fee†. When a payment is refunded, Repflow refunds the member from the platform balance and reverses the studio's transfer proportionally so both balances stay in step†.
- **How Repflow earns:** a software subscription of `$149` to `$399` a month per studio, charged to the studio's card or bank account on the 1st of the month, plus an application fee of 1% on every member payment, taken from each charge before the studio's share moves on. Studios that joined before 2024 are on an older contract with no application fee and a higher subscription.
- **Size:** about 280 studios at the start of the year and about 290 by early March (growing toward 330 by year-end). Members pay about `$38 million` a year through Repflow across about 420,000 payments, an average of more than 1,100 payments a day, with peaks on the 1st and 15th when monthly memberships renew. About two thirds of member payments are cards. The rest are ACH debits from members' bank accounts, which studios like because they cost less.
- **Staff:** 24 people. Engineering, sales, a support team of five and a finance team of two.
- **Time range:** 2025-01-01 to 2025-03-01, currency USD (60 days). Keep the business at full size: about 280 studios at the start and more than 1,100 member payments a day, with renewal peaks on January 1, January 15, February 1, February 15, and March 1. The 60-day window covers three federal bank holidays — New Year's Day (Wednesday 2025-01-01), Martin Luther King Jr. Day (Monday 2025-01-20), and Presidents' Day (Monday 2025-02-17) — plus two full month-end cutoffs (January 31 into February 1, and February 28 into March 1) and four semi-monthly payroll runs (Jan 15, Jan 31, Feb 15, Feb 28). Everyone acts cleanly and every payment, payout, refund, webhook, statement close and journal entry follows the rules.

## 2. History before the start

- Founded in 2019 by two former climbing-gym managers. In 2021 they moved payments from "bring your own processor" to Stripe Connect, because collecting payments earned more than software alone.
- Repflow raised a seed round in 2021 and a Series A in 2023. It has about `$6.8 million` in the bank on 2025-01-01 (`Operating ••4471` and `Reserve ••4488`) and burns about `$300,000` a month.
- On 2025-01-01:
  - Card payments from 30 and 31 December are still pending in Stripe and become available in January†.
  - A platform payout (`po_dec31`) and connected-account studio payouts submitted on December 31 are in transit and arrive at the bank on Thursday, January 2 (after the New Year's Day holiday)†.
  - Late-December ACH debits (from December 26–31) are pending in Stripe and settle across January 2–6.
  - January 1 membership renewals and monthly studio subscriptions run on New Year's Day.
  - Stripe's December invoice for Connect account fees is open and scheduled to be deducted from the platform balance in early January.
  - The 2024 books in Xero are reconciled through December 30, waiting on the December 30–31 cutoff payouts landing in January so Dana can close December.

## 3. Institutions (the only sources of data)

- **Stripe, Repflow's platform account.** Every charge, refund, application fee, transfer, transfer reversal, Connect invoice debit and payout, each as a balance transaction. Members pay by destination charge: the charge is made on the platform, and the studio's share is transferred to the studio's connected account at once, minus Repflow's application fee†. Full and partial refunds reverse a proportional share of the studio's transfer†, and the application fee is not refunded unless Repflow asks†. Card payments become available after 2 business days and are paid to Repflow's bank in one daily automatic payout†. ACH debits take 3–4 business days to settle. Card processing fees are kept on a refund†.
- **Stripe, the studios' connected accounts.** Each studio's available balance pays out daily on a rolling schedule† to the studio's bank account. A payout goes from pending to in transit to paid, which takes 1–2 business days after submission†. Studios can request an instant payout for a 1% fee, which arrives within 30 minutes†.
- **Pikes Peak Commerce Bank:** Repflow's operating account (`Operating ••4471`) receives Stripe's daily payouts and pays payroll, rent, AWS, company card statements and Stripe's invoices. The bank posts only on business days — never on weekends or on New Year's Day (Jan 1), MLK Day (Jan 20), or Presidents' Day (Feb 17)† — and shows each Stripe payout as one deposit with a short description and a payout reference, with nothing that names the charges inside it. Posted transactions and monthly statements closing January 31 and February 28. A reserve account (`Reserve ••4488`) holds cash set aside by finance.
- **Repflow's own database:** what Repflow's product records for every member invoice, its status (`paid`, `refunded`, `partially_refunded`), the studio it belongs to, the fee Repflow earned and what Repflow owes each studio. Webhooks are processed cleanly so Repflow's database stays in sync with Stripe.
- **Xero:** Repflow's general ledger. The finance team imports the bank feed each business day, posts payout summary journals from Stripe's reports, reconciles each deposit, and posts the month-end closes for December (in January) and January (in February).
- **Payroll provider:** semi-monthly payroll for 24 employees, debited from operating two business days before payday (paydays Jan 15, Jan 31, Feb 15, Feb 28).
- **Company card:** software, travel and conference spending, billed monthly on the 20th and paid from operating.

## 4. The cast

- **Dana Whitfield, head of finance.** Owns the monthly close, run from Stripe's reports, the bank and Xero. Closes December in January (after the December 30–31 payouts land) and closes January in February (after the January 30–31 charges settle and pay out in February).
- **Marcus Lee, finance associate.** Matches every Stripe payout to a bank deposit each week and books the payout summary journals in Xero, accounting for holiday three-day batches, month-end cutoffs, and Stripe's December and January Connect invoices netted out of the platform balance.
- **Sam, support team.** Processes requested full and partial member refunds cleanly in Repflow's admin tool with `reverse_transfer=True`† so the studio's transfer is always reversed proportionally.
- **Priya Raman, engineer on the payments team.** Runs the webhook sync so Stripe charges, settlements and refunds update Repflow's database cleanly.
- **The founders.** The sales founder signs 8–10 new studios across January and February on the 2024+ contract (1% application fee, `$199`–`$399` monthly subscription).
- **Studio owners (about 280, growing to ~290 by March 1).** Each has a contract: a monthly subscription, the 1% application fee (or 0% on pre-2024 contracts), and a daily payout schedule. Includes flagship climbing gyms with doubled New Year sign-ups, a reconciler pilates studio (`studio_reconciler`) that checks every payout to the cent, and studios (`studios_instant`) that request instant payouts before their own payroll around the 8th and 22nd of each month.
- **Members (tens of thousands).** Pay monthly memberships, class packs, drop-ins, personal training and retail by card (~2/3) or bank account (~1/3). All cards and bank accounts are valid and funded.
- **Stripe:** charges per-transaction processing fees, deducts its monthly Connect account fee invoices (December's in early January; January's in early February) from the platform balance, settles matured card and ACH charges, and sweeps available balances into daily automatic payouts.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Members -> Stripe (card) -> platform balance -> studio's connected account | destination charge; studio's share transferred at once, minus Repflow's application fee; available after 2 business days† |
| Members -> Stripe (ACH debit) -> platform -> studio | same path, settles in 3–4 business days |
| Platform balance -> Operating ••4471 | one automatic payout each business day, net of fees, refunds and Connect invoices in the balance† |
| Studio's connected account -> studio's bank | daily automatic payouts† (1–2 business days in transit†); instant payouts for a 1% fee† |
| Platform balance & studio's connected account -> members | full and partial refunds with proportional transfer reversals† |
| Studios -> Repflow | monthly software subscription by card or ACH (charged on the 1st of Jan, Feb, and Mar) |
| Operating -> payroll, AWS, rent, Stripe, card | semi-monthly payroll (Jan 15, Jan 31, Feb 15, Feb 28); monthly rent (1st), AWS (3rd–5th), company card (20th), and Stripe Connect invoices |

## 6. Stories

- **January and the two month-end cutoffs.** The new-year rush doubles sign-ups at the climbing gyms. Renewals on January 1 and 2 pay out after New Year's Day. Dana closes December once the December 30–31 payouts land in January, and closes January in mid-February once the January 30–31 charges settle and pay out in early February. Late February charges (February 27–28) similarly stay pending or in transit across the February 28 bank statement cutoff into March 1.
- **Three federal holidays and weekly matching (January–March).** Marcus matches every Stripe payout to a bank deposit each Friday, coping with New Year's Day (Jan 1), MLK Day (Jan 20), and Presidents' Day (Feb 17) holiday batches, weekend holds, clean full and partial refunds netted inside daily payouts, and the days when Stripe nets its December and January Connect invoices out of the platform balance.
- **New studio signings (January–February).** The sales founder signs 9 new studios across January and February on the 2024+ contract (`$199`–`$399` subscription, 1% application fee). Each begins collecting member payments and paying monthly subscriptions on the 1st of the following month.
- **Instant payouts before studio payroll (January–February).** A handful of studios take instant payouts before their own payroll around the 8th and 22nd of January and February. Each comes with a 1% fee†, lands the same day, and makes the studio's next daily automatic payout smaller.
- **Cent-exact studio and statement reconciliations (January 31 & February 28).** Pikes Peak Commerce Bank closes the January statement on January 31 and the February statement on February 28. Zenith Pilates (`studio_reconciler`) reconciles its payouts to the cent each Friday, and Dana and Marcus tie out Xero's trial balance against the bank statements and Stripe's clearing balances.

## 7. Kinds of events

Over the 60-day run, its records show these kinds of events:

- **Member payments:** card charges and ACH debits by the hundreds every day, peaks on the 1st and 15th (Jan 1, Jan 15, Feb 1, Feb 15, Mar 1) across memberships, class packs, drop-ins, personal training and retail.
- **Studio subscriptions and new signings:** three monthly software subscription billing runs (Jan 1, Feb 1, Mar 1) and 9 new studios onboarded across January and February.
- **Refunds:** full and partial member refunds processed cleanly with proportional connected-account transfer reversals (`reverse_transfer=True`)† and retained processing/application fees†.
- **Payouts and cutoffs:** daily automatic platform payouts† netting hundreds of transactions into one bank deposit, weekend and federal holiday delays (New Year's Day Jan 1, MLK Day Jan 20, Presidents' Day Feb 17)†, three cross-month cutoffs (Dec 30–31 -> Jan, Jan 30–31 -> Feb, Feb 27–28 -> Mar)†, daily studio payouts†, and instant studio payouts with a 1% fee†.
- **Database and general ledger sync:** webhook processing keeping Repflow's database in step with Stripe, daily Xero bank feed imports and payout summary journals, two monthly bank statements (Jan 31, Feb 28), and two monthly accounting closes (December and January).
- **Repflow's own money:** four semi-monthly payrolls (Jan 15, Jan 31, Feb 15, Feb 28), two monthly rents (Jan 1, Feb 1), two AWS bills, two company card statement payments, and two Stripe Connect monthly invoices (December's netted in January, January's netted in February).

## 8. Expectations

These expectations define how the cast of agents, their contracts, and their tool calls behave across the 60 days, and act as the known-good benchmark for Layer C (Contract & Rail Realism) and Layer D (Reconciliation) evaluations. Figures marked † come from published Stripe and Nacha rules in `SOURCES.md`.

### Agent cast, contracts, and behavior

- **Everything acts as an agent (`prompts.json`):** `next_day()` only advances the clock. Every payment, settlement, payout, bank posting, refund, statement close, and journal entry happens because an agent in `prompts.json` called a tool on its turn:
  - **Institution agents:** `stripe` (settles pending card/ACH items when their hold is up, charges the December and January Connect invoices in Jan and Feb, sweeps available balances into daily platform and studio payouts, and executes instant payouts), `pikes_peak_bank` (posts arriving payouts and scheduled debits on business days only — never on weekends or on Jan 1, Jan 20, or Feb 17† — and closes monthly bank statements on Jan 31 and Feb 28), and `xero` / `payroll_provider` / `company_card`.
  - **Studio agents:** represent the studios (~280 on Jan 1 growing to ~289 by Mar 1) across distinct personas and contracts (about 25–35% on the pre-2024 contract with 0% application fee and `$299`–`$399` subscription, and the rest on the 2024+ contract with 1% application fee and `$149`–`$399` subscription; flagship climbing gyms with New Year rushes, boutique yoga/pilates studios, a reconciler studio `studio_reconciler` that checks every payout to the cent each Friday, and studios `studios_instant` that request instant payouts before payroll around the 8th and 22nd of Jan and Feb).
  - **Member agents:** represent the customer cohorts and individuals with clean, honest spending habits (1st-of-month and 15th-of-month membership renewers across Jan 1, Jan 15, Feb 1, Feb 15, and Mar 1; card and ACH cohorts buying memberships, class packs, drop-ins, personal training, and retail at varied studio-specific prices; and members requesting normal full or partial refunds). No agent attempts fraud or disputes.
  - **Repflow staff agents:** `dana` (head of finance closing December in January and January in mid-February), `marcus` (weekly Friday payout reconciliation and payout summary journals), `sam` / support (issuing full and partial refunds cleanly with `reverse_transfer=True`), `priya` (payments engineer syncing Stripe webhooks to Repflow's database), and `founder_sales` (signing 9 new studios across Jan and Feb).

### Contract rules and delays enforced by institution agents

| Rail or contract rule | Expected behavior |
|---|---|
| Payment method mix | Card and ACH payments both active (~2/3 card, ~1/3 ACH), with varied prices across studio memberships, class packs, drop-ins, PT, and retail |
| Card settlement delay† | `2` business days (`available_on` skips weekends and federal holidays Jan 1, Jan 20, Feb 17†) |
| ACH debit settlement† | `3` to `4` business days to settle (`available_on` skips weekends and federal holidays†); `0` returns or disputes |
| Platform & studio payout speed† | `1` to `2` business days from `submitted` to `paid`/`posted` (`0` days for instant payouts†); no bank posting on weekends or on Jan 1, Jan 20, or Feb 17† |
| Refunds† | Clean full and partial refunds called by support with `reverse_transfer=True`† |
| Fraud & disputes | `0` fraud events and `0` disputes; all member payments are legitimate |

### Reconciliation pairs and expected exceptions

| Pair | Source A | Source B | Naive matcher recall band | Why items fail naive 1-to-1 matching |
|---|---|---|---|---|
| **1. Processor <-> Bank** | `stripe.payouts` & `stripe.balance_transactions` | `bank.operating_transactions` & `bank.statements` | `75%` to `95%` | Three cross-month cutoffs (Dec 30–31 -> Jan, Jan 30–31 -> Feb, Feb 27–28 -> Mar) (`cutoff_timing`); three federal holiday batches (Jan 1, Jan 20, Feb 17) + weekends (`holiday_weekend_delay`); daily payouts bundling hundreds of charges and refunds (`bundled_payout`); two monthly Stripe Connect invoices netted from the platform balance (`fee_netting`) |
| **2. Processor <-> Company DB** | `stripe.balance_transactions` & `stripe.connected_transactions` | `repflow_db.invoices` & `repflow_db.studio_ledger` | `85%` to `100%` | Gross invoice amounts vs. net processor transfers after 1% application fees and processing fees (`fee_netting`); partial refunds adjusting transfers proportionally (`partial_refund`); instant payout fees (`instant_payout_fee`) |
| **3. Bank / Processor <-> GL** | `bank.operating_transactions` & `stripe.payouts` | `xero.bank_feed`, `xero.journals`, & `xero.reconciliations` | `80%` to `95%` | One-line bank deposits matched to multi-line payout summary journals; gross-vs-net fee & Connect invoice netting (`fee_netting`); cross-month close cutoffs (`cutoff_timing`) |

- **Minimum distinct exception/reconciliation root causes in a 60-day clean run:** at least **5** of `{cutoff_timing, bundled_payout, holiday_weekend_delay, fee_netting, partial_refund, instant_payout_fee}`.
- **Unexplained mismatches (`truth()` check):** **0**. Every payout in `stripe.payouts` and `stripe.studio_payouts` must list the exact balance transaction IDs it settles (`item_ids` or `payout_id` on each transaction) and equal their sum to the cent, including any payout in transit on 2025-01-01.
