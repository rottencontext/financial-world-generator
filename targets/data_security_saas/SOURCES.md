# Sources: Triangle Shield Software

Modeled on **Data443 Risk Mitigation, Inc.** (OTC: ATDS, CIK 1068689), a data security software company in Research Triangle Park, North Carolina. The facts come from its amended 10-K for 2022 and from the balances it tagged in its 10-K and 10-Q filings (SEC XBRL company facts). The world keeps the real company's location, product types, selling model, revenue by period, deferred revenue and accrued liabilities by quarter, cash, debt pattern, related-party loans, the ransomware product purchase, headcount, its four material weaknesses, the dates of its 2022 10-K, 10-K/A and Q2 2023 10-Q, and the cash flow restatement. The names, people, bank, systems, audit firm, lenders' behavior and every dated event inside the windows are invented.

Grid cells:

- **record-to-report, tier 1:** `data_security_saas_7day.md`, a clean week of bank-to-books matching, payout summary entries and a trial balance check (July 1-7, 2023).
- **record-to-report, tier 2:** `PROMPT.md`, 60 days of month-end closes: unearned revenue rollforward, prepaid amortization, payroll accruals across month ends, note conversions, and the cash flow restatement (July 1-August 29, 2023).
- **record-to-report, tier 3:** `data_security_saas_audit_90day.md`, the 2022 year-end close and audit, with weekend entries, round-dollar adjustments, one person posting and approving, request lists and confirmations (January 1-March 31, 2023).

## Filings used

| Document | What it gave |
|---|---|
| [10-K/A for 2022, filed 2023-08-24](https://www.sec.gov/Archives/edgar/data/1068689/000149315223030030/form10-ka.htm) | Products (ARALOC, ArcMail, DataExpress, ClassiDocs/FileFacets, Ransomware Recovery Manager, WordPress GDPR/CCPA/LGPD plugins, some freemium); "paid in-advance, multiyear term that is auto-renewing" subscriptions; revenue recognized ratably; the move away from perpetual licenses with annual maintenance; channel partners, distributors, resellers; Azure and AWS marketplaces; "over 10,000 customers"; the January 2022 purchase of the Centurion SmartShield product ($250,000 cash, $2.9 million note, $250,000 contingent); 22 employees and 5 contractors at January 31, 2023; revenue $2,627,123 (2022) and $3,609,494 (2021); net loss $9,713,467; cash $1,712; trade receivables $31,978; current liabilities $8,604,066; working capital deficit $5,752,984; 2022 debt issued and repaid; CEO loans ($299,281 received, $602,237 repaid, $167,653 of expenses paid) and $112,064 due to related parties; all-asset security interest; Data443 NC's five-year lease from July 2022; office at 4000 Sancar Drive, Research Triangle Park; the four material weaknesses (quoted in the tier 2 prompt); new convertible notes dated January 4 and January 24, 2023 (exhibit index); the restatement of the 2022 statement of cash flows (convertible-note balances shown as financing instead of operating, found while preparing Q2 2023; operating cash used $2,886,337 -> $1,252,650; financing $2,244,244 -> $610,557); original 10-K filed February 24, 2023 |
| [SEC XBRL company facts, DeferredRevenueCurrent / ContractWithCustomerLiabilityCurrent](https://data.sec.gov/api/xbrl/companyconcept/CIK0001068689/us-gaap/DeferredRevenueCurrent.json) | Deferred revenue: $1,035,185 (Dec 31, 2021), $1,704,249 (Dec 31, 2022), $1,584,809 (Mar 31, 2023), $1,814,620 (Jun 30, 2023), $1,619,711 (Sep 30, 2023) |
| [SEC XBRL company facts, revenue](https://data.sec.gov/api/xbrl/companyconcept/CIK0001068689/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax.json) | Quarterly revenue: Q1 2023 $1,379,806; Q2 2023 $619,040; Q3 2023 $693,835; FY2023 $5,578,942; Q2 2023 10-Q filed August 14, 2023 |
| SEC XBRL company facts, AccruedLiabilitiesCurrent | Accrued liabilities: $554,076 (Dec 31, 2022), $553,367 (Mar 31, 2023), $778,611 (Jun 30, 2023) |

## Inferred

- That the deferred revenue for multi-year deals sits in one account and is split by spreadsheet. The filings tag only a current deferred revenue balance. Whether multi-year amounts were split is not known, so the world makes the split a schedule task.
- **The first quarter of 2023.** Revenue jumped to $1.38 million while deferred revenue fell. The term-license explanation is invented to fit the two numbers.

## Invented for this world

The names (Triangle Shield Software, its product names, Piedmont Ridge Bank, Hartwell & Coe LLP), every person, the finance team's makeup, QuickBooks Online, the CRM, the plugin store, the premium finance arrangement, payroll calendar, number of noteholders, conversion counts and every event in section 6 of the three prompts (the weekend entries, the round-dollar adjustments, the confirmation differences, the unrecorded liabilities and the prepaid errors). Real lenders named in the filing (several small-cap convertible note funds) are not named in the prompts.

## Known differences and oddities in the source

- **Two operating cash figures.** The 10-K/A's liquidity discussion still quotes $2,886,337 of operating cash used, while its restated cash flow table shows $1,252,650. The world treats the restated figure as the truth.
- **Two accumulated deficits.** The filing gives the accumulated deficit as $51,412,128 in one place and $51,412,413 in another.
- **The promissory note.** It is printed as "$2,900,00".
- **Proceeds from related parties.** The revised line shows $299,280 after a $1 adjustment that should give $229,280.
- **Cash in XBRL.** The XBRL cash tag reports 0 at both year ends, while the filing text gives $1,712. The prompt uses $1,712.
