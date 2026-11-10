# Repflow: booking software that moves money for 280 fitness studios

This describes one business, its past and its year. Facts marked † come from published rules on how this money moves: Stripe's documentation for platforms and Nacha's rules for ACH settlement, as summarized by Stripe and by banks that publish them (see `SOURCES.md`). A † vouches for the fact it follows, not for the date or reason the story gives it. No single company stands behind this business. Its size, people and account numbers are invented.

Every member payment in this world is honest, no one disputes a charge or commits fraud, every bank account is open and funded, and every staff member and webhook does its job on time. What drives the accounting work are the real mechanics of moving money through a payment facilitator across the year:

- destination charges split at once between Repflow's platform balance and each studio's connected account†;
- card payments that take 2 business days to become available† and ACH debits that take 3–4 business days;
- daily automatic payouts† that bundle hundreds of settled transactions into a single bank deposit and take 1–2 business days in transit†;
- weekends and federal bank holidays when banks do not post†;
- month-end cutoffs where charges from the last days of a month settle and land in the bank in the following month†;
- Stripe's monthly Connect account fee invoices netted directly from the platform balance;
- clean full and partial refunds where support reverses the studio's proportional transfer†, instant studio payouts before studio payrolls with a 1% fee†, new studios onboarding throughout the year, and a mid-year application fee change for new contracts.

## 1. The business and the time frame

- **Business:** Repflow Inc., a software company in Denver, Colorado. Independent gyms, yoga and pilates studios, climbing gyms and boxing clubs use Repflow to sell memberships, class packs, drop-ins, personal training and retail. Repflow collects every payment through Stripe Connect and pays each studio its share.
- **Most of the money is not Repflow's.** A member pays the studio through Repflow. The payment lands in Repflow's Stripe platform account, and the studio's share moves at once to the studio's connected account, minus Repflow's application fee†. When a payment is refunded, Repflow refunds the member from the platform balance and reverses the studio's transfer proportionally so both balances stay in step†.
- **How Repflow earns:** a software subscription of `$149` to `$399` a month per studio, charged to the studio's card or bank account on the 1st of the month, plus an application fee of 1% on every member payment (rising to 1.25% for new studios signed from July onward), taken from each charge before the studio's share moves on. Studios that joined before 2024 are on an older contract with no application fee and a higher subscription.
- **Size:** about 280 studios at the start of the year and about 330 at the end. Members pay about `$38 million` a year through Repflow across about 420,000 payments, an average of more than 1,100 payments a day, with peaks on the 1st and 15th when monthly memberships renew. About two thirds of member payments are cards. The rest are ACH debits from members' bank accounts, which studios like because they cost less.
- **Staff:** 24 people. Engineering, sales, a support team of five and a finance team of two.
- **Time range:** 2025-01-01 to 2025-12-31, currency USD. Sign-ups spike in January, dip in summer and climb again in September.

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
- **Pikes Peak Commerce Bank:** Repflow's operating account (`Operating ••4471`) receives Stripe's daily payouts and pays payroll, rent, AWS, software and Stripe's invoices. The bank posts only on business days — never on weekends or federal holidays† — and shows each Stripe payout as one deposit with a short description and a payout reference, with nothing that names the charges inside it. Posted transactions and monthly statements. A reserve account (`Reserve ••4488`) holds cash set aside by finance.
- **Repflow's own database:** what Repflow's product records for every member invoice, its status (`paid`, `refunded`, `partially_refunded`), the studio it belongs to, the fee Repflow earned and what Repflow owes each studio. Webhooks are processed cleanly each day so Repflow's database stays in sync with Stripe.
- **Xero:** Repflow's general ledger. The finance team imports the bank feed each business day, posts payout summary journals from Stripe's reports, reconciles each deposit, and closes the books each month.
- **Payroll provider:** semi-monthly payroll for 24 employees, debited from operating two business days before payday.
- **Company card:** software, travel and conference spending, paid monthly from operating.

## 4. The cast

- **Dana Whitfield, head of finance.** Owns the monthly close, run from Stripe's reports, the bank and Xero. Closes each month once the prior month's cutoff payouts have settled in the bank.
- **Marcus Lee, finance associate.** Matches every Stripe payout to a bank deposit each week and books the payout summary journals in Xero, accounting for holiday and weekend batching, month-end cutoffs, and Stripe's monthly Connect invoices netted from the platform balance.
- **Support team (five).** Issue requested full and partial refunds for studios and members from Repflow's admin tool, reversing the studio's transfer proportionally (`reverse_transfer=True`)†.
- **Priya Raman, engineer on the payments team.** Maintains the Stripe webhook sync so charges, settlements and refunds update Repflow's database cleanly each day.
- **The founders.** One sells to new studios (growing the roster from ~280 to ~330 across the year). The other runs product and introduces a 1.25% application fee tier for new studios starting July 1.
- **Studio owners (about 280, then 330).** Each has a contract: a monthly subscription (`$149`–`$399`), the application fee (0% pre-2024, 1% for 2024 through June 2025, 1.25% for new studios signed from July 2025 onward), and a daily payout schedule. Includes flagship climbing gyms with seasonal rushes, a reconciler pilates studio that checks every payout to the cent, and studios that take instant payouts before their own payroll.
- **Members (tens of thousands).** Pay monthly memberships, class packs, drop-ins, personal training and retail by card (~2/3) or bank account (~1/3). All cards and bank accounts are valid and funded.
- **Stripe:** charges per-transaction processing fees, deducts its monthly invoice for Connect account fees from the platform balance, settles matured card and ACH charges, and sweeps available balances into daily automatic payouts.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Members -> Stripe (card) -> platform balance -> studio's connected account | destination charge; studio's share transferred at once, minus Repflow's application fee; available after 2 business days† |
| Members -> Stripe (ACH debit) -> platform -> studio | same path, settles in 3–4 business days |
| Platform balance -> Operating ••4471 | one automatic payout each business day, net of fees, refunds and Connect invoices in the balance† |
| Studio's connected account -> studio's bank | daily automatic payouts† (1–2 business days in transit†); instant payouts for a 1% fee† |
| Platform balance & studio's connected account -> members | full and partial refunds with proportional transfer reversals† |
| Studios -> Repflow | monthly software subscription by card or ACH on the 1st of each month |
| Operating -> payroll, AWS, rent, Stripe, card | semi-monthly payroll, monthly rent, AWS, company card and Stripe Connect invoices |

## 6. Stories

- **January and month-end cutoffs (all year).** The new-year rush doubles sign-ups at the climbing gyms. Renewals on January 1 and 2 pay out after the New Year's Day holiday. Every month, card and ACH payments from the last two to four days of the month settle and land in the bank in the first week of the next month, so Dana and Marcus reconcile each month's cutoff payouts against the clearing balance.
- **Marcus's weekly matching (all year).** Marcus matches every Stripe payout to a bank deposit each Friday, accounting for payouts that bundle Friday-through-Sunday activity or three-day federal holiday weekends, full and partial refunds netted inside daily payouts, and the day each month when Stripe nets its monthly Connect invoice from the platform balance.
- **New studio signings and the July rate tier.** The sales founder signs about 50 new studios over the year. Starting July 1, newly signed studios join on a 1.25% application fee tier while earlier 2024+ studios remain at 1% and pre-2024 studios remain at 0%.
- **Instant payouts (all year).** A handful of studios take instant payouts before their own payroll twice a month. Each comes with a 1% fee†, lands within 30 minutes, and makes the studio's next daily automatic payout smaller.
- **The year-end close (December).** Dana reconciles all twelve monthly bank statements, clearing accounts and studio ledgers through December 31 so the books tie to the cent for the annual audit.

## 7. Kinds of events

Over the year, its records show these kinds of events:

- **Member payments:** card charges and ACH debits by the hundreds every day, peaks on the 1st and 15th across memberships, class packs, drop-ins, personal training and retail.
- **Studio subscriptions and new signings:** monthly software subscriptions on the 1st of each month and new studios joining throughout the year.
- **Refunds:** full and partial refunds processed cleanly with proportional transfer reversals (`reverse_transfer=True`)† and retained processing/application fees†.
- **Payouts and cutoffs:** a daily platform payout† netting hundreds of transactions into one bank deposit, weekend and holiday payouts landing on the next business day†, cross-month cutoff payouts†, daily studio payouts†, and instant studio payouts with a 1% fee†.
- **Database and general ledger sync:** daily webhook processing keeping Repflow's database in step with Stripe, and Xero bank feed imports, payout summary journals, monthly bank statements and monthly closes.
- **Repflow's own money:** software subscriptions from studios, semi-monthly payroll, AWS, rent, company card statements, and Stripe's monthly Connect invoices.

## 8. Expectations

These expectations define how the cast of agents, their contracts, and their tool calls behave, and act as the known-good benchmark for Layer C (Contract & Rail Realism) and Layer D (Reconciliation) evaluations. Figures marked † come from published Stripe and Nacha rules in `SOURCES.md`.

### Agent cast, contracts, and behavior

- **Everything acts as an agent (`prompts.json`):** `next_day()` only advances the clock. Every payment, settlement, payout, bank posting, refund, statement close, and journal entry happens because an agent in `prompts.json` called a tool on its turn:
  - **Institution agents:** `stripe` (settles pending card/ACH items when their hold is up, charges the monthly Connect invoice, sweeps available balances into daily platform and studio payouts, and executes instant payouts), `pikes_peak_bank` (posts arriving payouts and scheduled debits on business days only — never on weekends or federal holidays† — and closes monthly bank statements), and `xero` / `payroll_provider` / `company_card`.
  - **Studio agents:** represent the studios (~280 at start growing to ~330) across distinct personas and contracts (about 25–35% on the pre-2024 contract with 0% application fee and `$299`–`$399` subscription; 2024+ studios at 1% application fee; July+ new studios at 1.25% application fee; flagship climbing gyms with seasonal rushes, boutique yoga/pilates studios, a reconciler studio that checks every payout to the cent, and studios that request instant payouts before payroll).
  - **Member agents:** represent the customer cohorts and individuals with clean, honest spending habits (1st-of-month and 15th-of-month membership renewers, card and ACH cohorts buying memberships, class packs, drop-ins, personal training, and retail at varied studio-specific prices, and members requesting normal full or partial refunds). No agent attempts fraud or disputes.
  - **Repflow staff agents:** `dana` (head of finance running the monthly close), `marcus` (weekly payout reconciliation and summary journals), `sam` / support (issuing full and partial refunds cleanly with `reverse_transfer=True`), `priya` (payments engineer syncing Stripe webhooks), and the founders (signing new studios and introducing the July 1.25% rate tier for new signings).

### Contract rules and delays enforced by institution agents

| Rail or contract rule | Expected behavior |
|---|---|
| Payment method mix | Card and ACH payments both active (~2/3 card, ~1/3 ACH), with varied prices across studio memberships, class packs, drop-ins, PT, and retail |
| Card settlement delay† | `2` business days (`available_on` skips weekends and federal holidays†) |
| ACH debit settlement† | `3` to `4` business days to settle (`available_on` skips weekends and federal holidays†); `0` returns or disputes |
| Platform & studio payout speed† | `1` to `2` business days from `submitted` to `paid`/`posted` (`0` days for instant payouts†); no bank posting on weekends or federal holidays† |
| Refunds† | Clean full and partial refunds called by support with `reverse_transfer=True`† |
| Fraud & disputes | `0` fraud events and `0` disputes; all member payments are legitimate |

### Reconciliation pairs and expected exceptions

| Pair | Source A | Source B | Naive matcher recall band | Why items fail naive 1-to-1 matching |
|---|---|---|---|---|
| **1. Processor <-> Bank** | `stripe.payouts` & `stripe.balance_transactions` | `bank.operating_transactions` | `75%` to `95%` | Month-end cutoff payouts landing in the next month (`cutoff_timing`); holiday and weekend batching (`holiday_weekend_delay`); daily payouts bundling hundreds of charges and refunds (`bundled_payout`); Stripe's monthly Connect invoice netted from the platform balance (`fee_netting`) |
| **2. Processor <-> Company DB** | `stripe.balance_transactions` & `stripe.connected_transactions` | `repflow_db.invoices` & `repflow_db.studio_ledger` | `85%` to `100%` | Gross invoice amounts vs. net processor transfers after application fees and processing fees (`fee_netting`); partial refunds adjusting transfers proportionally (`partial_refund`); instant payout fees (`instant_payout_fee`) |
| **3. Bank / Processor <-> GL** | `bank.operating_transactions` & `stripe.payouts` | `xero.bank_feed`, `xero.journals`, & `xero.reconciliations` | `80%` to `95%` | One-line bank deposits matched to multi-line payout summary journals; gross-vs-net fee & Connect invoice netting (`fee_netting`); cross-month close cutoffs (`cutoff_timing`) |

- **Minimum distinct exception/reconciliation root causes:** at least **4** in a 7-day run and **5** in a 60-day or full-year run across `{cutoff_timing, bundled_payout, holiday_weekend_delay, fee_netting, partial_refund, instant_payout_fee}`.
- **Unexplained mismatches (`truth()` check):** **0**. Every payout in `stripe.payouts` and `stripe.studio_payouts` must list the exact balance transaction IDs it settles (`item_ids` or `payout_id` on each transaction) and equal their sum to the cent, including any payout in transit on 2025-01-01.
