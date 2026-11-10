# Targets: business stories grounded in public filings

Each folder here is one business: a main prompt that describes the business, its past, its institutions, its people, its money flows, its stories and the kinds of events its data should cover. Most are modeled on a real company's public filings, so their scale, debts and quirks come from real records rather than from imagination.

A folder modeled on filings has two files:

- `PROMPT.md`: the prompt. Facts marked † come from the sources; everything else is invented. Company names, people and account numbers are invented even where the numbers are real.
- `SOURCES.md`: the filings and pages behind the †-marked facts, what was inferred, what was invented, and any disagreements inside the source.

Run one:

```
uv run --env-file .env worldgen run targets/brewery_taproom/PROMPT.md
```

## The businesses

| Folder | Business | Year | Modeled on | What its money adds beyond the SaaS world |
|---|---|---|---|---|
| [`bike_shop`](bike_shop/) | One-room bike repair shop | 2024 | Invented (no `SOURCES.md`) | The smallest world, for quick runs |
| [`trucking`](trucking/) | Six-truck freight carrier in Missouri | 2024 | Invented (no `SOURCES.md`) | Broker invoices sold to a factoring company |
| [`saas_startup`](saas_startup/) | Small B2B SaaS company | 2021-22 | The [AccountingBench](https://accounting.penrose.com/) company (no `SOURCES.md`) | The reference world the others are compared to |
| [`brewery_taproom`](brewery_taproom/) | Taproom brewery that also self-distributes | 2023 | Black Hammer Brewing (Form C) | Point-of-sale payouts, cash drawers, tips through payroll, gift cards, wholesale on terms, keg deposits, excise and container deposits, community bonds, a dumped batch |
| [`dtc_brand`](dtc_brand/) | Online consumer brand with one huge institutional buyer | 2022 | Tampon Tribe (Form C) | Shopify payouts with holdbacks, stacked revenue-based advances, a manufacturer paid by wire, net-60 receivables that swamp the bank balance |
| [`pt_clinic`](pt_clinic/) | Outpatient physical therapy practice | 2023 | DCPT (Form C campaign page) | Insurer payments weeks after each visit, Medicare's payment floor, denials, recoupments, virtual cards, deductible resets, merchant cash advances |
| [`roofing_contractor`](roofing_contractor/) | Union commercial roofer sold to a new owner | 2024 | H.C. Anderson Roofing (Form C) | Pay applications and retainage, lien waivers, public-entity warrants, union fringe remittances, seasonal layoffs, an acquisition loan and a seller note, transfers to a related company |
| [`food_pantry`](food_pantry/) | Nonprofit food pantry building its own building | 2022-23 | Coralville Community Food Pantry (Form 990) | Donations through many channels, December surges, pledges, stock gifts, a bridge loan, construction payments with retainage, food bank invoices |
| [`vacation_rentals`](vacation_rentals/) | Vacation-rental manager for 42 cabins | 2023 | Vacasa's 10-Ks and Airbnb's payout rules (no single small company) | Guest money held in trust until the stay, platform payouts after check-in, monthly owner statements, refunds clawed back from later payouts, lodging taxes |
| [`cookie_wholesale`](cookie_wholesale/) | Bakery brand selling to a distributor, an airline and specialty chains | 2025 | Legally Addictive Foods (Form C) and UNFI's deduction rules | Built for AR/AP agents: invoices, POs, receiving records, remittances and emails as records, distributor deductions and disputes, a procurement portal that rejects invoices, unapplied cash, duplicate and mismatched vendor bills, a fraudulent bank-detail change, services received but not billed, and a ground truth for grading |
| [`studio_payments`](studio_payments/) | Booking and payments software for 280 fitness studios | 2025 | Stripe Connect and Nacha rules (no single company) | Destination charges and application fees, a daily payout netting hundreds of payments, 2-day card holds and 3–4 day ACH settlement across weekends and holidays, full and partial refunds with proportional transfer reversals, instant studio payouts with fees, and monthly Connect fee invoices netted from payouts |

| [`short_drama_app`](short_drama_app/) | Short-drama streaming app run from Singapore for a Cayman parent | Q1 2025 | Mega Matrix / FlexTV (20-F, 10-K/A) and Apple's and Google's payout rules | Apple and Google monthly lump-sum payouts on different calendars, web checkout through Stripe and PayPal in several currencies, carrier billing in rupiah, unspent coins and memberships as unearned revenue, withholding tax on licensing, a customer who paid a fraudster, intercompany funding between three companies |
| [`defense_machining`](defense_machining/) | Two defense machine shops, one parent, one bank | Q4 of fiscal 2025, plus one clean week | TechPrecision (10-K) | Purchase orders, receipts and three-way matching, customer-supplied metal, nickel surcharges, `2% 10` discounts, a successful business email compromise and partial recall, split orders, holds released without receipts, goods received but not invoiced at year end, a covenant default |
| [`data_security_saas`](data_security_saas/) | Tiny listed data-security software company | 2023: one clean week, 60 days, and the year-end audit | Data443 (10-K/A, XBRL balances) | Multi-year prepaid subscriptions, marketplace and plugin-store payouts, prepaid amortization, payroll accruals across month ends, convertible note conversions, CEO loans, weekend and round-dollar journal entries, an audit request list and confirmations, a real cash flow restatement |
| [`id_verification_saas`](id_verification_saas/) | ID-scanning software company | Spring 2022 | Intellicheck (10-K/A) | An annual report filed and then restated: option awards that should have been liabilities, withholding taxes on exercises never paid, corrected payroll filings, penalties |

Several folders hold more than one prompt: a 7-day, 60-day or 90-day window of the same business. [`GRID.md`](GRID.md) places every prompt in a grid of finance cycles (order-to-cash, procure-to-pay, record-to-report) by difficulty, and lists more real companies that fit each cell.


## Finding more real companies

Public filings work, but only some kinds fit small businesses:

- **SEC Form C (Regulation Crowdfunding)** is the best fit. Small businesses raising up to $5 million must file a business description, employee count, a two-year financial summary, a table of every debt with lender, rate and maturity, and usually full financial statements. Restaurants, breweries, clinics, shops, contractors and consumer brands file them through Wefunder, StartEngine, Mainvest, SMBX, PicMii and others. Search with [EDGAR full-text search](https://www.sec.gov/edgar/search/#/q=%22taproom%22&forms=C), filtering to form `C` (the five filings above came from searches like `"taproom"`, `"physical therapy"`, `"roofing contractor"`). For bulk selection, the SEC's quarterly [Crowdfunding Offerings Data Sets](https://www.sec.gov/dera/data/crowdfunding-offerings-data-sets) hold every Form C's structured fields (employees, two years of revenue, assets, debt, net income, state, funding portal). Counted from them through September 2026: about 9,170 businesses have filed a Form C since May 2016, and about 1,750 of them reported at least $250,000 of revenue and at least 5 employees in their latest filing.
- **SEC 10-K and S-1** describe large companies. They are useful for how a platform holds and pays out money (Vacasa above), not for small-business scale.
- **IRS Form 990**, through [ProPublica's Nonprofit Explorer](https://projects.propublica.org/nonprofits/), covers nonprofits: revenue mix, salaries, assets and liabilities by year.
- **Not yet tried here, but promising:** franchise disclosure documents filed with states (royalty and ad-fund payments, unit economics), bankruptcy schedules for small businesses in Subchapter V cases (every bank account, creditor and lease), and the SBA's PPP loan data (a loan was about 2.5 months of payroll, so it gives the payroll size of named small businesses).

Access notes: scripts that fetch from `www.sec.gov` must send a User-Agent with a contact email, while the full-text search endpoint works without one. ProPublica blocks scripted PDF and XML downloads but its JSON API is open.
