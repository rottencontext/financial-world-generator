# Bayview Identity: an ID-scanning software company that files its annual report and then restates it (spring 2022)

This describes one business, its past and ninety days. Facts marked † come from the real company's amended annual report on Form 10-K/A that this business is modeled on (see `SOURCES.md`). A mark vouches for the fact it follows, not for the date or reason the story gives it. The company, its people and its account numbers are invented.

This world is built for testing record-to-report and audit agents on a restatement. The audit is nearly done when the window opens, and the annual report is filed ten days later. Then a payroll reconciliation turns up a problem:

- shares that employees gave up when exercising stock options were never sold;
- the taxes withheld on those exercises were never paid over to the tax authorities;
- the options themselves should have been accounted for as liabilities, remeasured every quarter, not as equity.

The company, its auditors and its payroll provider then have to work out what happened, by how much, in which periods, and file an amended report.

## 1. The business and the time frame

- **Business:** Bayview Identity Systems, Inc., Long Island, New York†. It sells identity verification, mostly as software-as-a-service: customers pay for a cloud service that reads and checks driver's licenses and other IDs at a counter, in an app or at a door†.
- **How it earns:**
  - **Per scan.** A fee for every ID checked.
  - **Fixed monthly fee.** Charged per device or per physical business location†.
  - **Hardware.** Some scanners and devices.

  Customers are retailers, banks and other financial firms, hotels, government agencies and building-access companies†. Two customers give 55% of revenue, and the top ten give 79%†.
- **Size:** revenue `$16,393,000` in 2021 and `$10,735,000` in 2020†, of which software-as-a-service `$12,970,000` and `$9,373,000`†.
- **Staff:** 49 full-time employees†: 5 executives, 22 in IT and development, 13 in sales and marketing, 3 in integration and support, and 6 in administration†. Finance is a CFO, a controller and one accountant.
- **Time range:** 2022-03-14 (Monday) to 2022-06-11 (Saturday), ninety days, currency USD. The window covers:
  - the last days of the 2021 audit;
  - the annual report filed on March 24†;
  - the first-quarter close;
  - the payroll provider's first-quarter tax reconciliation;
  - the restatement work;
  - the amended annual report, filed on June 9†;
  - Memorial Day (May 30).

## 2. History before the start

- **Option awards.** Starting in the third quarter of 2020, the company granted employees option awards that, under its own practices, should have been accounted for as liabilities†. Liability awards are remeasured at fair value each quarter, so the expense moves with the share price. The company accounted for them as equity instead.
- **Exercises.** When employees exercised options, they surrendered shares to cover the exercise and the taxes. The company was supposed to sell those shares and pay the equivalent amount to the tax authorities. It did not†.
- **Nobody noticed for six quarters.** The company did not have enough accounting staff with the knowledge, experience and training to apply the accounting rules for equity compensation†.
- **On 2022-03-14:**
  - The auditors have finished most fieldwork on 2021.
  - Open requests: the stock option rollforward, the year-end payroll tax reconciliation and two customer confirmations.
  - The draft annual report shows the net loss as originally computed.
  - About 60 option exercises since the third quarter of 2020 sit in the equity plan administrator's records.
  - Their tax withholding appears in the payroll registers as withheld, but the tax deposits made by the payroll provider never included it.

## 3. Institutions (the only sources of data)

Each keeps its own records the way it really would. Documents (contracts, invoices, statements, tax forms, notices, confirmations, work papers) are records too: one row per document, with the fields on it.

- **Sound Shore Bank:** operating account `••6602` and a money market account. Posted transactions and statements.
- **NetSuite (the books):** customers, invoices, cash receipts, vendor bills, journal entries with who posted and approved them, the general ledger and the trial balance.
- **The billing system:** monthly per-scan counts and fixed fees per customer, producing the invoices.
- **The equity plan administrator:** every grant, vest, exercise and cancellation, with grant terms, exercise price, shares surrendered and shares issued. It also keeps the "sell to cover" instructions that were never sent.
- **The payroll provider:** semi-monthly payroll registers, which include option exercise income as supplemental wages with tax withheld, tax deposits made on the company's behalf, quarterly federal and state filings, and quarterly reconciliations that compare wages and withholding with deposits.
- **The transfer agent:** the share register, with shares issued on exercise and shares surrendered.
- **Tax authorities:** the record of deposits received, filings, and later notices of underpayment, penalties and interest.
- **Stone & Lasker LLP, the outside audit firm:** its request list, emails, adjustments, and its reports, with their dates.
- **The SEC's EDGAR system:** filings with dates, including any notice of late filing.

## 4. The cast

- **Karen Albright, CEO.** Wants the annual report out on time, and then wants the restatement over quickly.
- **David Osei, CFO.** Signs the filings. Signs off option grant terms, and is the first to see the payroll provider's reconciliation.
- **Nina Feld, controller.** Owns the close, the stock compensation schedule and the payroll entries. Has never handled liability awards.
- **Sam Ortiz, accountant.** Books cash, billing and payroll journals.
- **The payroll provider's tax analyst.** Flags the mismatch in the first-quarter reconciliation and asks how the company wants it fixed.
- **Stone & Lasker's team.** The partner signs the original report and, later, the reissued one. The manager reopens the 2021 work. A specialist values the options as liabilities.
- **Employees who exercised.** About twenty people, several of whom have left, whose W-2s now need correcting.
- **Customers.** Two large customers dominate. One disputes a per-scan invoice in April, which delays its payment.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Customers -> operating account | ACH and wires against monthly per-scan and fixed-fee invoices, net 30 |
| Operating account -> payroll provider -> employees, tax authorities | semi-monthly, with tax deposits made by the provider |
| Operating account -> tax authorities | catch-up deposits of the unremitted withholding, then penalties and interest |
| Operating account -> vendors, hosting, rent | ACH and card |
| Operating account <-> money market | sweeps |
| Employees -> company | none in cash: shares surrendered on exercise |

## 6. Stories

- **The last audit requests (March 14-23).** Nina sends the option rollforward and the year-end payroll tax reconciliation. Neither looks at whether withholding on exercises was ever deposited. The two outstanding customer confirmations come back clean. The auditors sign, and the annual report is filed on March 24†.
- **The first-quarter close (April).** Nina books stock compensation for the quarter on the old basis. One large customer disputes an April per-scan invoice for double-counted scans from a store system's retries. It pays the undisputed part and the rest later.
- **The reconciliation (late April).** The payroll provider's first-quarter reconciliation shows supplemental wages from option exercises with tax withheld but not deposited. Its analyst emails David. David and Nina trace the exercises back to the third quarter of 2020. Every one has the same gap: shares surrendered, no sale, no deposit.
- **The accounting question (May).** The company and the auditors conclude:
  - the award terms and practice make the options liabilities†;
  - the unpaid withholding is a liability too;
  - 2020 and 2021, and the quarters in between, are misstated†.

  The option specialist values the awards at each quarter end. The restatement adds `$3,042,000` to 2020 expense and `$3,331,000` to 2021†. The net loss becomes `$2,484,000` for 2020 and `$7,478,000` for 2021†.
- **Paying the taxes (May-June).** The company deposits the unpaid withholding, files corrected quarterly returns and issues corrected W-2s. Tax authorities send notices with penalties and interest. Some former employees can't be reached at their old addresses.
- **The amended report (June 9).** The amended annual report restates 2021 and 2020 and the quarters in between†. It reports a material weakness in accounting for equity compensation†. The auditors reissue their report.

## 7. Kinds of events

Over the ninety days, its records show these kinds of events:

- **Audit and filing:** final audit requests, confirmations, an annual report filed, an amended report filed with restated years and quarters, a reissued audit report.
- **Equity:** option grants, exercises, shares surrendered, shares never sold, awards remeasured as liabilities each quarter.
- **Payroll tax:** supplemental wages with withholding that was never deposited, a provider's reconciliation that flags it, catch-up deposits, corrected returns and W-2s, penalty and interest notices.
- **Revenue:** monthly per-scan and fixed-fee invoices, a disputed invoice paid in two parts, concentration in two customers.
- **Close:** a quarterly close on the old basis that must be redone, prior-period adjustments, journal entries that cross years.

## 8. What the world must also remember

So that an agent working these records can be graded, the world keeps, in its own state and not in any institution's records, the truth behind every record:

- each option exercise, the shares surrendered, the tax that should have been deposited and when;
- the fair value of the liability awards at each quarter end;
- the correct expense and liability in each restated period;
- the penalties and interest owed;
- which W-2s and returns need correcting;
- which audit procedures could have caught the gap before March 24.
