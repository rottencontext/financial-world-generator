# Repflow: booking software that moves money for 280 fitness studios (one clean week)

This describes one business, its past and one clean week. Facts marked † come from published rules on how this money moves: Stripe's documentation for platforms and Nacha's rules for ACH settlement, as summarized by Stripe and by banks that publish them (see `SOURCES.md`). A † vouches for the fact it follows, not for the date or reason the story gives it. No single company stands behind this business. Its size, people and account numbers are invented.

This is the clean week of the order-to-cash world in `PROMPT.md`. Every member payment is honest, no one disputes a charge or commits fraud, every bank account is open and funded, and every staff member and webhook does its job on time. What is left are the mechanics of moving money through a payment facilitator across a federal holiday and a weekend:

- destination charges split at once between Repflow's platform balance and each studio's connected account†;
- card payments that take 2 business days to become available† and ACH debits that take 3–4 business days;
- daily automatic payouts† that bundle hundreds of settled transactions into a single bank deposit and take 1–2 business days in transit†;
- New Year's Day (Wednesday, January 1) and the first weekend (January 4–5), when banks do not post†;
- December 30–31 payments and in-transit payouts that settle and land in the bank in January†;
- Stripe's December Connect account fee invoice netted directly from the platform balance;
- clean full and partial refunds where support reverses the studio's proportional transfer†, and an instant studio payout before payroll with a fee†.

## 1. The business and the time frame

- **Business:** Repflow Inc., a software company in Denver, Colorado. Independent gyms, yoga and pilates studios, climbing gyms and boxing clubs use Repflow to sell memberships, class packs, drop-ins, personal training and retail. Repflow collects every payment through Stripe Connect and pays each studio its share.
- **Most of the money is not Repflow's.** A member pays the studio through Repflow. The payment lands in Repflow's Stripe platform account, and the studio's share moves at once to the studio's connected account, minus Repflow's application fee†. When a payment is refunded, Repflow refunds the member from the platform balance and reverses the studio's transfer proportionally so both balances stay in step†.
- **How Repflow earns:** a software subscription of `$149` to `$399` a month per studio, charged to the studio's card or bank account on the 1st of the month, plus an application fee of 1% on every member payment, taken from each charge before the studio's share moves on. Studios that joined before 2024 are on an older contract with no application fee and a higher subscription.
- **Size:** about 280 studios at the start of the year. Members pay about `$38 million` a year through Repflow across about 420,000 payments, an average of more than 1,100 payments a day, with peaks on the 1st and 15th when monthly memberships renew. About two thirds of member payments are cards. The rest are ACH debits from members' bank accounts, which studios like because they cost less.
- **Staff:** 24 people. Engineering, sales, a support team of five and a finance team of two.
- **Time range:** 2025-01-01 to 2025-01-07, currency USD. This is a seven-day clean run of the first week of the year. Keep the business at full size: about 280 studios and more than 1,100 member payments a day, with the January 1 renewal peak. The week covers New Year's Day (Wednesday, January 1), when banks don't post, and the first weekend (January 4–5). Everyone acts cleanly and every payment, payout, refund, webhook and journal entry follows the rules.

## 2. History before the start

- Founded in 2019 by two former climbing-gym managers. In 2021 they moved payments from "bring your own processor" to Stripe Connect, because collecting payments earned more than software alone.
- Repflow raised a seed round in 2021 and a Series A in 2023. It has about `$6.8 million` in the bank on 2025-01-01 (`Operating ••4471` and `Reserve ••4488`).
- On 2025-01-01:
  - Card payments from 30 and 31 December are still pending in Stripe and become available in January†.
  - A platform payout (`po_dec31`) and connected-account studio payouts submitted on December 31 are in transit and arrive at the bank on Thursday, January 2 (after the New Year's Day holiday)†.
  - Late-December ACH debits (from December 26–31) are pending in Stripe and settle across January 2–6.
  - January 1 membership renewals and monthly studio subscriptions run on New Year's Day.
  - Stripe's December invoice for Connect account fees (`$412.50`) is open and scheduled to be deducted from the platform balance on the first business day of January (January 2).
  - The 2024 books in Xero are reconciled through December 30, waiting only on the December 30–31 cutoff payouts landing in January to finish the December close.

## 3. Institutions (the only sources of data)

- **Stripe, Repflow's platform account.** Every charge, refund, application fee, transfer, transfer reversal, Connect invoice debit and payout, each as a balance transaction. Members pay by destination charge: the charge is made on the platform, and the studio's share is transferred to the studio's connected account at once, minus Repflow's application fee†. Full and partial refunds reverse a proportional share of the studio's transfer†, and the application fee is not refunded unless Repflow asks†. Card payments become available after 2 business days and are paid to Repflow's bank in one daily automatic payout†. ACH debits take 3–4 business days to settle. Card processing fees are kept on a refund†.
- **Stripe, the studios' connected accounts.** Each studio's available balance pays out daily on a rolling schedule† to the studio's bank account. A payout goes from pending to in transit to paid, which takes 1–2 business days after submission†. Studios can request an instant payout for a 1% fee, which arrives within 30 minutes†.
- **Pikes Peak Commerce Bank:** Repflow's operating account (`Operating ••4471`) receives Stripe's daily payouts and pays payroll, rent, AWS, software and Stripe's invoices. The bank posts only on business days — never on New Year's Day (Jan 1) or weekends (Jan 4–5)† — and shows each Stripe payout as one deposit with a short description and a payout reference, with nothing that names the charges inside it. A reserve account (`Reserve ••4488`) holds cash set aside by finance.
- **Repflow's own database:** what Repflow's product records for every member invoice, its status (`paid`, `refunded`, `partially_refunded`), the studio it belongs to, the fee Repflow earned and what Repflow owes each studio. Webhooks arrive and are processed cleanly each day so Repflow's database stays in sync with Stripe.
- **Xero:** Repflow's general ledger. The finance team imports the bank feed each business day, posts payout summary journals from Stripe's reports, and reconciles each deposit. Xero's bank feed shows the same one-line deposits as the bank.
- **Payroll provider:** semi-monthly payroll for 24 employees, debited from operating two business days before payday (next payday is January 15, debited January 13).

## 4. The cast

- **Dana Whitfield, head of finance.** Oversees the books from Stripe's reports, the bank and Xero. Tracks the December 30–31 cutoff payouts landing in January and reviews the weekly trial balance tie-out on Tuesday, January 7.
- **Marcus Lee, finance associate.** Matches every Stripe payout to its bank deposit, verifies the items bundled inside each payout, and posts the daily payout summary entries in Xero.
- **Sam, support team.** Processes requested full and partial member refunds cleanly in Repflow's admin tool with `reverse_transfer=True`† so the studio's transfer is always reversed proportionally and Repflow's database updates in step.
- **Priya Raman, engineer on the payments team.** Processes Stripe webhook events daily so charges, settlements and refunds in Repflow's database match Stripe without lag or duplicates.
- **Studio owners (about 280).** Each has a contract: a monthly subscription (`$149`–`$399`), the 1% application fee (or 0% on pre-2024 contracts), and a daily payout schedule. Includes flagship climbing gyms (`studio_altitude`) with doubled New Year sign-ups, a reconciler pilates studio (`studio_riverbend`) that checks every payout to the cent, a yoga studio (`studio_lotus`), and a boxing club (`studio_cornerstone`) that takes an instant payout before its January 8 payroll.
- **Members (tens of thousands).** Pay monthly memberships, class packs, drop-ins, personal training and retail by card (~2/3) or bank account (~1/3). All cards and bank accounts are valid and funded.
- **Stripe:** charges per-transaction processing fees, collects its December Connect account fee invoice from the platform balance on January 2, settles matured card and ACH charges, and sweeps available balances into daily automatic payouts.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Members -> Stripe (card) -> platform balance -> studio's connected account | destination charge; studio's share transferred at once, minus Repflow's application fee; available after 2 business days† |
| Members -> Stripe (ACH debit) -> platform -> studio | same path, settles in 3–4 business days |
| Platform balance -> Operating ••4471 | one automatic payout each business day, net of fees, refunds and Connect invoices in the balance† |
| Studio's connected account -> studio's bank | daily automatic payouts† (1–2 business days in transit†); instant payouts for a 1% fee† |
| Platform balance & studio's connected account -> members | full and partial refunds with proportional transfer reversals† |
| Studios -> Repflow | monthly software subscription billed on January 1 by card or ACH |
| Operating -> rent, AWS, payroll | monthly rent (due Jan 1, posted Jan 2) and AWS (due Jan 5, posted Jan 6); semi-monthly payroll (next debit Jan 13) |

## 6. Stories

- **The New Year's rush and holiday cutoff (January 1–2).** New Year sign-ups double volume at the climbing gyms alongside the January 1 monthly membership renewals and the 280 studios' monthly software subscriptions. Because Wednesday, January 1 is a federal holiday, Pikes Peak Commerce Bank is closed: the December 31 in-transit payout (`po_dec31`) and the January 1 office rent (`$18,500.00`) post on Thursday, January 2, and January 1 card charges become available on Monday, January 6 (two business days after Thursday, January 2†).
- **December cutoff payouts landing in January (January 2–6).** Card payments from December 30 and 31 become available on January 2 and 3 and are swept into the first January payouts, while late-December ACH debits settle across January 2–6. Marcus and Dana split those prior-period settlements cleanly in Xero against the December clearing balance.
- **The netted Connect invoice (January 2).** On Thursday, January 2, Stripe deducts its open December invoice for Connect account fees (`$412.50`) from Repflow's platform balance. That day's automatic platform payout is `$412.50` smaller than the day's settled application fees and studio subscriptions; Marcus books the `$412.50` fee line in the payout summary journal so the deposit reconciles to the cent.
- **Clean full and partial refunds (January 3).** On Friday, January 3, a member at Altitude Climbing Gym requests a full refund on a `$180.00` class pack after upgrading to an annual membership, and a member (`member_janet`) at Lotus Yoga Collective requests a `$60.00` partial refund on a `$145.00` class pack. Sam issues both refunds in Stripe with `reverse_transfer=True`†, reversing the studios' transfers proportionally while keeping the original processing and application fees per contract†.
- **The weekend batch and Monday catch-up (January 4–6).** No bank postings occur on Saturday, January 4 or Sunday, January 5†. Payouts submitted on Friday afternoon and bills due over the weekend (including the `$8,400.00` AWS bill due January 5) post at the bank on Monday, January 6.
- **An instant payout before studio payroll (January 6).** Cornerstone Boxing Club requests an instant payout on Monday, January 6 ahead of its January 8 studio payroll. Stripe pays the available connected balance within 30 minutes minus the 1% instant payout fee†, and Cornerstone's next daily automatic payout reflects the smaller remaining balance.
- **Cent-exact studio and GL tie-out (January 6–7).** On Monday, January 6, Riverbend Pilates reconciles its week's payouts against its member invoices to the cent. On Tuesday, January 7, Marcus and Dana finish reconciling every settled bank deposit in Xero and confirm that Stripe, Repflow's database, the bank and the general ledger all tie out.

## 7. Kinds of events

Over the week, its records show these kinds of events:

- **Member payments:** hundreds of valid card charges and ACH debits every day, with the January 1 renewal and New Year sign-up peak across memberships, class packs, drop-ins, personal training and retail.
- **Studio subscriptions:** monthly software subscriptions (`$149`–`$399`) charged to all 280 studios on January 1.
- **Settlements and cutoffs:** 2-business-day card holds† and 3–4 business-day ACH holds skipping New Year's Day (Jan 1) and the weekend (Jan 4–5)†, with December 30–31 charges settling in January.
- **Refunds:** a full refund and a partial refund, both processed cleanly with proportional connected-account transfer reversals (`reverse_transfer=True`)† and retained processing/application fees†.
- **Payouts and fee netting:** daily automatic platform payouts† netting hundreds of balance transactions (and Stripe's `$412.50` December Connect invoice) into single bank deposits, daily studio connected-account payouts†, and an instant studio payout with a 1% fee†.
- **Bank postings and operating bills:** in-transit payouts and scheduled rent (`$18,500.00`) and AWS (`$8,400.00`) debits posting on business days only†.
- **Database and general ledger sync:** daily webhook processing keeping Repflow's database in step with Stripe, and daily Xero bank feed imports, payout summary journals and bank reconciliations.

## 8. Expectations

These expectations define how the cast of agents, their contracts, and their tool calls behave in this clean week, and act as the known-good benchmark for Layer C (Contract & Rail Realism) and Layer D (Reconciliation) evaluations. Figures marked † come from published Stripe and Nacha rules in `SOURCES.md`.

### Agent cast, contracts, and behavior

- **Everything acts as an agent (`prompts.json`):** `next_day()` only advances the clock. Every payment, settlement, payout, bank posting, refund, webhook sync, and journal entry happens because an agent in `prompts.json` called a tool on its turn:
  - **Institution agents:** `stripe` (settles pending card/ACH items when their hold is up, deducts the December Connect invoice on Jan 2, sweeps available balances into daily platform and studio payouts, and executes instant payouts), `pikes_peak_bank` (posts arriving payouts and scheduled rent/AWS debits on business days only — never on Jan 1 or Jan 4–5†), `xero` (imports daily bank feed lines and records journals/reconciliations), and `payroll_provider` (checks the payroll calendar; next debit is Jan 13 for the Jan 15 payday).
  - **Studio agents:** represent the 280 studios across distinct personas and contracts (about 25–35% on the pre-2024 contract with 0% application fee and `$299`–`$399` subscription, and the rest on the 2024+ contract with 1% application fee and `$149`–`$399` subscription; flagship climbing gym `studio_altitude` with New Year sign-up rushes, reconciler studio `studio_riverbend` checking every payout to the cent, yoga studio `studio_lotus`, and boxing club `studio_cornerstone` requesting an instant payout on Jan 6 before its Jan 8 payroll).
  - **Member agents:** represent the customer cohorts and individuals with clean, honest spending habits (1st-of-month membership renewers, card and ACH cohorts buying memberships, class packs, drop-ins, personal training, and retail at varied studio-specific prices, and members requesting normal full or partial refunds on unused class packs). No agent attempts fraud or disputes.
  - **Repflow staff agents:** `dana` (head of finance reviewing cutoff payouts and the Jan 7 trial balance tie-out), `marcus` (matching daily payouts to bank deposits and posting Xero summary journals), `sam` / support (issuing requested full and partial refunds cleanly with `reverse_transfer=True`), and `priya` (processing daily Stripe webhooks so `repflow_db` stays synced with Stripe).

### Contract rules and delays enforced by institution agents

| Rail or contract rule | Expected behavior |
|---|---|
| Payment method mix | Card and ACH payments both active (~2/3 card, ~1/3 ACH), with varied prices across studio memberships, class packs, drop-ins, PT, and retail |
| Card settlement delay† | `2` business days (`available_on` skips weekends and Jan 1 federal holiday†) |
| ACH debit settlement† | `3` to `4` business days to settle (`available_on` skips weekends and Jan 1†); `0` returns or disputes in this clean week |
| Platform & studio payout speed† | `1` to `2` business days from `submitted` to `paid`/`posted` (`0` days for instant payouts†); no bank posting on Jan 1 or Jan 4–5† |
| Refunds† | Clean full and partial refunds called by support with `reverse_transfer=True`† (proportional transfer reversal, application and processing fees kept per contract†) |
| Fraud & disputes | `0` fraud events and `0` disputes; all member payments are legitimate |

### Reconciliation pairs and expected exceptions

| Pair | Source A | Source B | Naive matcher recall band | Why items fail naive 1-to-1 matching |
|---|---|---|---|---|
| **1. Processor <-> Bank** | `stripe.payouts` & `stripe.balance_transactions` | `bank.operating_transactions` | `75%` to `95%` | Dec 30–31 charges and in-transit payouts landing in Jan (`cutoff_timing`); New Year's Day (Jan 1) and weekend (Jan 4–5) payout delays (`holiday_weekend_delay`); hundreds of charges, fees, and refunds bundled into one daily payout (`bundled_payout`); Stripe's `$412.50` Dec Connect invoice netted from the Jan 2 payout (`fee_netting`); Jan 6–7 payouts still in transit at week's end |
| **2. Processor <-> Company DB** | `stripe.balance_transactions` & `stripe.connected_transactions` | `repflow_db.invoices` & `repflow_db.studio_ledger` | `85%` to `100%` | Gross invoice amounts vs. net processor transfers after 1% application fees and processing fees (`fee_netting`); partial refund adjusting invoice and studio transfer proportionally (`partial_refund`); instant payout fee deducted on `studio_cornerstone` (`instant_payout_fee`) |
| **3. Bank / Processor <-> GL** | `bank.operating_transactions` & `stripe.payouts` | `xero.bank_feed`, `xero.journals`, & `xero.reconciliations` | `80%` to `95%` | One-line bank deposits matched to multi-line payout summary journals splitting gross sales, refunds, application fees, and the netted `$412.50` Connect invoice (`fee_netting`, `cutoff_timing`) |

- **Minimum distinct exception/reconciliation root causes in a 7-day clean run:** at least **4** of `{cutoff_timing, bundled_payout, holiday_weekend_delay, fee_netting, partial_refund, instant_payout_fee}`.
- **Unexplained mismatches (`truth()` check):** **0**. Every payout in `stripe.payouts` and `stripe.studio_payouts` must list the exact balance transaction IDs it settles (`item_ids` or `payout_id` on each transaction) and equal their sum to the cent, including any payout in transit on 2025-01-01.
