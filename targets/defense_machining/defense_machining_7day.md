# Nashoba Precision: two defense machine shops buying on purchase orders (one clean week)

This describes one business, its past and one week. Facts marked † come from the real company's annual report on Form 10-K that this business is modeled on (see `SOURCES.md`). A mark vouches for the fact it follows, not for the date or reason the story gives it. The companies, people and account numbers are invented.

This is the clean week of the procure-to-pay world in `PROMPT.md`. Everyone follows the process, every document is honest, and nothing is lost. What is left are the mechanics:

- purchase orders, receipts and invoices that arrive on different days;
- partial shipments and freight billed apart;
- payment terms counted from the invoice date;
- early-payment discounts with a ten-day deadline;
- a weekend and a bank holiday;
- a weekly payment run that pays many invoices in one bank batch.

## 1. The business and the time frame

- **Business:** Nashoba Precision Corp., a small listed holding company with two subsidiaries that make large, precise metal parts for defense programs:
  - **Nashoba Fabrication, Inc.** Central Massachusetts, about 65 acres and 145,000 square feet†. Welds and machines components of up to 100 tons†, more than 95% of it defense work† and much of it for the US Navy's Virginia-class and Columbia-class submarine programs†.
  - **Arroyo Aerotool, Inc.** Los Angeles, 183,000 square feet†. Makes large parts for military aircraft, helicopters and space programs, plus tooling, molds, fixtures, jigs and dies†.
- **How work arrives:** Mostly individual purchase orders from prime defense contractors†, built to the customer's drawings†. Most contracts have the customer supply the raw material†.
- **Size:** revenue about `$34.0 million` in the fiscal year ending March 31, 2025†. 152 full-time employees, none in a union†.
- **What it buys:** steel, nickel alloys such as Monel and Inconel, aluminum and stainless steel†, plus outside processing (heat treating, plating, painting, inspection), tooling and cutters, freight, repairs, gases and shop supplies. That comes to about 50 vendor invoices a week across both plants.
- **Time range:** 2025-02-12 (Wednesday) to 2025-02-18 (Tuesday), seven days, currency USD. The week includes a weekend and Presidents' Day (Monday, February 17), when banks don't post. Payment runs go out on Thursdays. ACH payments settle the next business day, so Thursday's run settles Friday. Checks mailed on Thursday clear days or weeks later.

## 2. History before the start

- Nashoba Precision has owned Fabrication for many years and bought Arroyo in 2021. Each plant keeps its own system with its own vendor list, purchase orders, receipts and invoices.
- All debt is with one bank: a revolving line, two term loans and equipment financing†, about `$7.4 million` in total†. Cash is tight. The group ends the fiscal year with about `$195,000`†. In this clean week, the CFO draws on the line before the payment run, so every invoice due this week can be paid on time.
- **On 2025-02-12:**
  - About 120 approved invoices are open across both plants, about 30 of them due or with a discount deadline this week.
  - Twelve purchase orders are partly received.
  - Three steel orders and two batches of outside processing are due at the docks this week.
  - Last Thursday's payment run has settled, and two of its checks have not cleared.

## 3. Institutions (the only sources of data)

Each keeps its own records the way it really would. Documents (purchase orders, packing slips, receiving records, material certifications, invoices, statements, remittance advice) are records too: one row per document, with the fields printed on it and line items as their own rows.

- **Fabrication's job-shop system and Arroyo's system.**
  - Purchase orders with lines priced per pound, piece or lot, and job numbers.
  - Receipts entered at the dock with quantity and heat number.
  - Invoices matched three ways (PO, receipt, invoice) within 2% on price and quantity.
  - Vendor lists with terms and bank details, and payment runs.
- **Approval rules:** purchase orders up to `$5,000` approved by the plant manager, up to `$25,000` by the controller, above that by the CFO. Payment runs are approved by the controller.
- **Monadnock Savings Bank.** Fabrication operating `••2210`, Arroyo operating `••2237`, and the revolving line:
  - Posted transactions with the bank's description.
  - One ACH batch per payment run, listing each payment's payee and amount.
  - Checks clearing one by one.
  - A positive-pay file for Fabrication's checks.
  - Line draws and nightly sweeps of customer payments.
- **The payables mailboxes (`ap-ma@` and `ap-la@`).** Invoices, statements and remittance advice, one row per email.
- **Vendors' own records.** Each vendor's statement of what it billed and was paid.

## 4. The cast

- **Renee Duval, CFO.** Approves big orders and draws on the line before the payment run.
- **Tom Kowalski, corporate controller.** Approves the payment runs for both plants.
- **Linda Morse, payables clerk, Fabrication.** Enters and matches invoices, schedules the run, and takes every discount whose deadline falls before the next run.
- **Carlos Mendez, payables and receiving coordinator, Arroyo.** Enters receipts the day goods arrive and invoices the day they come in.
- **Mike Flanagan, buyer, Fabrication.** Places steel and outside-processing orders.
- **Vendors:**
  - two steel service centers on net 30;
  - an alloy distributor that adds a monthly nickel surcharge, written into its PO terms;
  - cutter and tooling distributors on `2% 10, net 30`;
  - an industrial supply house on `1% 10, net 30`;
  - outside processors on net 30, freight carriers that bill each shipment separately, and a repair technician who bills by the hour against a purchase order.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Revolving line -> subsidiary accounts | a draw on Wednesday before Thursday's run |
| Subsidiary accounts -> vendors | Thursday payment run: one ACH batch per plant, settling Friday, plus checks for vendors without ACH details |
| Customers -> subsidiary accounts -> revolving line | ACH payments, swept nightly |

## 6. Stories

- **Steel in pieces.** A steel service center ships an order of plate in two trucks, on Wednesday and Friday. Each delivery has its own packing slip and is received against the same purchase order. The center invoices each shipment separately, and freight comes on a third invoice from the carrier the following week.
- **The surcharge clause.** The alloy distributor's Inconel invoice is 3.1% above the PO base price because of February's nickel surcharge. Mike's PO includes the surcharge clause, and Linda matches the invoice at base price plus the published surcharge.
- **Discount deadlines and the holiday.** Four tooling invoices dated February 6 to 8 carry `2% 10` discounts expiring between February 16 and 18. Linda pays them in Thursday's run, which settles Friday, before the deadlines. One industrial-supply invoice dated February 7, with its discount expiring Monday the 17th, a bank holiday, is paid in the same run.
- **Outside processing comes back.** A batch of parts returns from the heat treater on Tuesday with its certifications. The receipt is entered against the outside-processing PO. The invoice arrives the same day and matches.
- **A partial receipt held.** A cutter order is received short: 40 of 50 inserts. The vendor invoices all 50. The invoice holds on quantity until the backorder arrives on Tuesday. Then it matches and is scheduled for next week's run.
- **The weekly run.** On Thursday, Tom approves two runs: 31 ACH payments and 4 checks at Fabrication, and 22 ACH payments and 2 checks at Arroyo. Each run is one batch debit at the bank. Two checks from last week's run clear on Tuesday.

## 7. Kinds of events

Over the week, its records show these kinds of events:

- purchase orders issued and partly received;
- receipts with packing slips and certifications;
- invoices matched three ways, a surcharge within the PO's terms, freight billed separately, an invoice held for a short shipment;
- discounts taken on time across a weekend and a bank holiday;
- weekly ACH batches and checks, a line draw, nightly sweeps, checks clearing later.

## 8. What the world must also remember

So that an agent working these records can be graded, the world keeps, in its own state and not in any institution's records, the truth behind every record:

- which purchase order and receipt each invoice belongs to;
- each invoice's due date and discount deadline;
- the right amount paid on each, and which invoices in each bank batch it covers;
- the open payables and received-not-invoiced amounts at the end of the week.
