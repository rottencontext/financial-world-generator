# Triangle Shield Software: syncing the bank to the books in one clean week (July 2023)

This describes one business, its past and one week. Facts marked † come from the real company's public filings that this business is modeled on (see `SOURCES.md`). A mark vouches for the fact it follows, not for the date or reason the story gives it. The company, its people and its account numbers are invented.

This is the clean week of the record-to-report world in `PROMPT.md`. Everyone does their job correctly. The work is mechanical, but exact:

- match every bank line to the books;
- book each marketplace and plugin-store payout as a summary entry built from the report behind it (sales, fees, refunds);
- record a payroll and a few bills;
- check that the trial balance after the June close still ties to the bank, the payouts and the schedules.

## 1. The business and the time frame

- **Business:** Triangle Shield Software, Inc., Research Triangle Park, North Carolina†. Data security and privacy software†:
  - **VaultRoom:** secure content sharing.
  - **ArchiveCrate:** archiving.
  - **DataCourier:** data placement.
  - **TagSense:** classification.
  - **RewindGuard:** ransomware recovery.
  - **PrivacyKit:** privacy plugins for WordPress†.
- **How it sells:** Subscriptions, often prepaid for several years, recognized evenly over the term†. It sells directly, through resellers and distributors†, through the Azure and AWS marketplaces†, and through a plugin store. It has more than 10,000 customers†.
- **Size:** revenue `$619,040` in the second quarter of 2023†. Deferred revenue `$1,814,620` and accrued liabilities `$778,611` on June 30, 2023†. 22 employees and 5 contractors†.
- **Time range:** 2023-07-01 (Saturday) to 2023-07-07 (Friday), seven days, currency USD. The week includes a weekend and the Fourth of July (Tuesday), when banks don't post. In this clean version, the June close was finished correctly on June 30, and the June bank reconciliation ties.

## 2. History before the start

- The company is financed by convertible notes, promissory notes and loans from its CEO†, secured by all its assets†. Cash is always thin.
- **On 2023-07-01:**
  - The June trial balance is final.
  - Deferred revenue, prepaid, payroll accrual and note schedules all tie to it.
  - Open items:
    - a reseller invoice due July 5;
    - the June marketplace disbursements from AWS and Microsoft, which arrive this week;
    - the plugin store's June payout;
    - the July 1 rent;
    - one vendor check written on June 28 and not yet cleared.

## 3. Institutions (the only sources of data)

- **Piedmont Ridge Bank:** operating account `••5180`. Posted transactions with the bank's description, running balance and the July statement later. Items dated on a non-banking day post on the next banking day.
- **QuickBooks Online (the books):**
  - the bank feed, imported daily, which suggests matches;
  - invoices, bills, payments, deposits, journal entries and the trial balance.
- **AWS Marketplace and Microsoft's commercial marketplace:** monthly billing reports by buyer and subscription, and disbursements net of the marketplace fee for amounts the marketplace has collected.
- **The plugin store:** a monthly payout, with a sales report listing every license sold, refunded or charged back and the store's revenue share.
- **The payroll provider:** the register for the June 16-30 run, paid June 30, with taxes debited separately.
- **The CRM:** contracts, billing schedules and renewal dates.
- **Resellers:** remittance advice by email.

## 4. The cast

- **Priya Natarajan, CFO (part-time).** Reviews the week's matching on Friday and signs off the trial balance check.
- **Ben Carter, staff accountant.** Matches the bank feed every morning and books the payout summary entries from each report.
- **Jordan Reese, founder and CEO.** Not involved this week.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Reseller -> operating account | ACH against an invoice, with remittance advice |
| AWS / Microsoft -> operating account | June disbursements, net of fees |
| Plugin store -> operating account | June payout, net of revenue share, refunds and chargebacks |
| Operating account -> landlord, hosting, software | ACH on due dates |
| Operating account -> payroll tax agencies | June 30 payroll taxes |

## 6. Stories

- **The holiday.** The reseller's ACH, sent on Monday, July 3, posts that day. A hosting charge dated Tuesday, July 4 posts on Wednesday, July 5. The July 1 rent ACH, dated on a Saturday, posts on Monday, July 3.
- **Three payouts, three summary entries.**
  - **AWS.** Its June disbursement covers four subscriptions, one of them a monthly charge collected late from a May buyer.
  - **Microsoft.** Its payout nets one small refund.
  - **The plugin store.** Its payout covers 312 licenses sold, 9 refunds and 2 chargebacks, less the store's share.

  Ben books each one as a single entry. Gross sales go to the marketplace receivable (already recognized in revenue at the June close). Fees go to expense. Refunds and chargebacks go to the accounts where they were booked. The net goes to the bank.
- **The check that clears.** The vendor check written on June 28 clears on Thursday, July 6, for exactly the amount in the books.
- **Friday's check.** Priya compares the trial balance with the bank balance, the open receivables (including the marketplace receivable) and the schedules. Every difference is explained by an item dated after June 30.

## 7. Kinds of events

Over the week, its records show these kinds of events: bank feed matching, items that post on the next banking day after a weekend or holiday, payout summary entries split into sales, fees, refunds and chargebacks, a reseller payment applied to its invoice, a check clearing, rent and hosting paid, and a trial balance tied to the bank and the schedules.

## 8. What the world must also remember

So that an agent working these records can be graded, the world keeps, in its own state and not in any institution's records, the truth behind every record:

- which invoices and receivables each deposit settles;
- the correct split of each payout;
- the correct bank and book balances each day;
- the trial balance as it should be on July 7.
