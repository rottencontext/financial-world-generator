# Nashoba Precision: two defense machine shops buying steel, alloys and outside processing on purchase orders (last quarter of the fiscal year, 2025)

This describes one business, its past and one quarter. Facts marked † come from the real company's annual report on Form 10-K that this business is modeled on (see `SOURCES.md`). A mark vouches for the fact it follows, not for the date or reason the story gives it. The companies, people and account numbers are invented.

This world is built for testing procure-to-pay agents. Its paper trail runs purchase order, receiving record, vendor invoice, payment. It covers two plants on two different systems, a finance team too small to check its own work, a cash balance near zero, and a quarter that ends at the fiscal year end. Inside it are a business email compromise that succeeds, goods received but not billed at year end, and approvals that people go around.

## 1. The business and the time frame

- **Business:** Nashoba Precision Corp., a small listed holding company with two operating subsidiaries that make large, precise metal parts for defense programs:
  - **Nashoba Fabrication, Inc.** Its plant in central Massachusetts stands on about 65 acres with 145,000 square feet of buildings†. It welds and machines components weighing up to 100 tons†, and more than 95% of its revenue is defense†. Much of its work is for the US Navy's Virginia-class and Columbia-class submarine programs†.
  - **Arroyo Aerotool, Inc.** Its plant in Los Angeles has about 183,000 square feet under roof†. It makes large, critical parts for military aircraft, helicopters and space programs, plus tooling, molds, fixtures, jigs and dies†.
- **How work arrives:** Mostly as individual purchase orders from prime defense contractors, not long-term agreements†. Parts are built to the customer's drawings†, and revenue is recognized as the work progresses†. The largest customer, a prime contractor, gave 23% of the year's revenue†. The order backlog is about `$48.6 million`, to be delivered over two to three years†.
- **Size (fiscal year ending March 31, 2025):** revenue about `$34.0 million`, `$33.6 million` of it defense†. Fabrication brought in `$18.2 million` and Arroyo `$16.0 million`†. Fabrication made money, while Arroyo lost money even before overhead: its operating loss was `$4.6 million`†. The group's net loss was `$2.7 million`†.
- **What it buys:** steel, nickel alloys such as Monel and Inconel, aluminum and stainless steel, some with long lead times†. Four suppliers each made up at least 10% of purchased material†. Most contracts have the customer supply the raw material†, so much of the metal that arrives on the dock does not belong to the company. On top of that it buys outside processing (heat treating, plating, painting, nondestructive testing), tooling and cutters, freight, maintenance and repairs, gases and shop supplies. That comes to about 650 vendor invoices a quarter across about 210 active vendors.
- **Staff:** 152 full-time employees, none in a union†. Fabrication has 21 salaried and 60 hourly†. Arroyo has 21 salaried and 50 hourly†.
- **Time range:** 2025-01-01 to 2025-03-31, the last quarter of the fiscal year, currency USD. The quarter includes New Year's Day, Martin Luther King Jr. Day (January 20) and Presidents' Day (February 17), when banks don't post. The fiscal year closes on Monday, March 31.

## 2. History before the start

- Nashoba Precision has owned Fabrication for many years. It bought Arroyo in 2021. Arroyo has lost money ever since, and its accounting has never caught up. Three weaknesses in internal control are on record from the last annual report:
  - accounting for the Arroyo purchase and for fair values afterwards†;
  - too few tax accounting staff to work out Arroyo's tax position on time†;
  - too few accounting staff at Arroyo to perform management reviews and reconcile accounts on time†.
- **Debt.** All the debt is with one bank†: about `$7.4 million` at year end†. It is made up of a revolving line due August 29, 2025†, a Fabrication term loan at 6.05% due December 2027†, an Arroyo term loan at 3.79% due August 2028†, and Arroyo equipment financing at 13.38% due September 2026†. The company does not meet the loan's financial covenants and expects to keep missing them†. It is in default for missing the debt service coverage ratio for the twelve months to March 31, 2025†, and the bank keeps its right to demand repayment†. The auditors doubt the company can continue as a going concern†.
- **Cash.** The group starts the fiscal year with about `$138,000` of cash† and ends it with about `$195,000`†. Every vendor payment run is a choice about who waits.
- **Payables.** About `$1.4 million` were owed to vendors at the last fiscal year end†, and about `$2.4 million` are owed at this one†.
- **Systems.** Fabrication's job-shop system and Arroyo's older system were never merged. Each keeps its own vendor list, purchase orders, receipts and invoices. Each vendor list has its own bank details, and some vendors appear in both.
- **On 2025-01-01:**
  - December receipts at Arroyo are not all entered.
  - About 40 vendor invoices are on hold for missing receipts or price differences.
  - Two steel service centers have past-due balances.
  - The revolving line is nearly fully drawn.
  - The December payroll accrual is booked. December's bank reconciliation at Arroyo is not done.

## 3. Institutions (the only sources of data)

Each keeps its own records the way it really would. Documents (purchase orders, packing slips, receiving records, material certifications, invoices, statements, remittance advice) are records too: one row per document, with the fields printed on it and line items as their own rows. Each document is kept as its sender wrote it, not as the books later recorded it.

- **Fabrication's job-shop system.**
  - **Purchase orders.** Each has a buyer, an approver, lines priced per pound, piece or lot, and a job number.
  - **Receipts.** Entered at the dock against the PO, with the quantity and the heat number from the material certification.
  - **Vendor invoices.** Entered by the payables clerk and matched three ways (PO, receipt, invoice) within 2% on price and quantity. An invoice outside tolerance goes on hold until someone with authority releases it. Each release is logged with who and when.
  - **Vendor list and payments.** The vendor list has an audit log of every change. Payment runs choose which approved invoices to pay.
- **Arroyo's system.** Works the same way but older:
  - receipts can be entered after the invoice;
  - holds can be released by the payables clerk;
  - the same user can change a vendor's bank details and release a payment run.
- **Approval rules (in both systems and in a written policy):**
  - purchase orders up to `$5,000` approved by the plant manager, up to `$25,000` by the controller, above that by the CFO;
  - every vendor bank-detail change confirmed by a phone call to a number already on file, then approved by the controller;
  - payment runs approved by the controller, and wires by the CFO and controller together.
- **Monadnock Savings Bank.** Fabrication operating `••2210`, Arroyo operating `••2237`, and the revolving line:
  - Customer payments are swept to pay down the line each night. Draws are requested by the CFO.
  - Each posted transaction shows the bank's description (`ACH CREDIT HULLWORKS SUPPLIER PMT`, `CHECK 10412`, `ACH DEBIT VENDOR PMT BATCH 0219`, `LOC ADVANCE`).
  - The bank keeps monthly statements, a positive-pay file for Fabrication's checks, and a record of every ACH batch with each payment's name, routing and account number.
- **The payables mailboxes (`ap-ma@` and `ap-la@`).** Every email as a row, with thread, date, from, to, subject, body and attachment ids. Invoices, statements, past-due notices, W-9s, "we changed banks" letters and replies arrive here.
- **Vendors' own records.** Each vendor's statement of what it billed, what it was paid and what is past due, sent monthly or on request.
- **Customers' supplier portals.** Prime contractors' purchase orders, change orders, shipping notices and payments. Customer-supplied material arrives with the customer's paperwork and no price.
- **The company card.** Small tooling, shipping and software purchases, with a monthly statement paid from Fabrication's account.
- **Payroll provider.** Biweekly payroll for each subsidiary.

## 4. The cast

- **Alex Shaw, CEO.** Spends the quarter with the bank and with customers. Signs off covenant certificates.
- **Renee Duval, CFO.** Approves big orders and every wire. Decides each week which vendors get paid. Stretched across the bank, the auditors and a late annual report.
- **Tom Kowalski, corporate controller, Massachusetts.** Owns the vendor lists, approves bank-detail changes and payment runs, and closes the books. Works mostly on Fabrication and reaches Arroyo by email.
- **Linda Morse, payables clerk, Fabrication.** Fifteen years in the job. Enters, matches and schedules invoices, and knows every vendor by voice.
- **Carlos Mendez, payables and receiving coordinator, Arroyo.** Handles everything from the dock to the payment run alone. He has full rights in Arroyo's system.
- **Joyce Lin, staff accountant, Arroyo.** Reconciles the bank and reviews Carlos's work, when she has time. Leaves at the end of February, and nobody replaces her before year end.
- **Ray Delgado, plant manager, Arroyo.** Needs tooling and repairs now and finds the approval limits slow.
- **Mike Flanagan, buyer, Fabrication.** Places most steel and outside-processing orders.
- **Vendors (about 210 active):**
  - two steel service centers and an alloy distributor, which bill a monthly surcharge on top of the base price for nickel alloys;
  - a heat treater and an inspection lab in Los Angeles, and a plater and a painter in Massachusetts;
  - cutter and tooling distributors offering `2% 10, net 30`;
  - an industrial supply house offering `1% 10, net 30`;
  - freight carriers that bill separately, a crane rental firm, machine repair technicians who bill by the hour, gas suppliers, a uniform service, utilities and software.
- **Customers.** Prime contractors that issue POs, supply material, inspect at the source and pay delivery invoices 30 to 45 days later.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Customers -> subsidiary accounts -> revolving line | ACH against delivery and progress invoices, swept nightly to pay down the line |
| Revolving line -> subsidiary accounts | draws requested by the CFO before payment runs and payroll |
| Subsidiary accounts -> vendors | weekly payment runs by ACH or check; wires for a few large alloy orders |
| Fabrication -> Arroyo, Arroyo -> Fabrication | intercompany invoices when one plant machines parts for the other, settled by transfer |
| Subsidiary accounts -> bank | monthly term-loan and equipment payments, interest on the line |
| Subsidiary accounts -> payroll provider -> employees, tax agencies | biweekly |
| Fabrication account -> company card | monthly statement |

## 6. Stories

- **The heat treater's "new bank" (January-March).** On January 22, Carlos receives an email that looks like it comes from Arroyo's heat treater, from a look-alike domain. It says the company has moved banks after a merger and attaches a letter on its letterhead with a new routing and account number. Carlos calls the phone number in the email, not the one on file. A friendly voice confirms. Carlos changes the vendor's bank details in Arroyo's system, which lets him do it without the controller. Arroyo's Thursday payment runs send `$86,400` and `$52,750` of the heat treater's invoices to the new account, settling on February 7 and February 21. On March 3 the real heat treater calls about its past-due balance. Renee has the bank attempt a recall, and the receiving bank freezes `$31,200` of the second payment, still in the account. The first payment is gone. The heat treater still has to be paid, and threatens to stop work on a submarine part until it is.
- **Arroyo's missing receipts (March).** After Joyce leaves, the temporary receiving clerk stops entering receipts for two weeks. Invoices pile up on hold for "no receipt". To keep critical vendors shipping, Carlos releases about thirty invoices without receipts, using his own override. Two of them are for goods that never arrived: a cutter order shipped to Fabrication by mistake, and a partial shipment invoiced in full.
- **The split order (February).** Ray needs a `$23,800` set of fixture plates and inserts quickly. He issues five purchase orders of `$4,760` each to the same tooling distributor on the same day, each under his `$5,000` limit, so none reaches the controller.
- **After-the-fact orders (all quarter).** A five-axis machine at Fabrication breaks down on January 9. The repair technician works three days without a purchase order. His `$14,600` invoice arrives on February 4, and a purchase order is created that afternoon, dated January 9.
- **The alloy surcharge (January-March).** The alloy distributor bills Inconel plate at the base price plus the month's nickel surcharge. When the surcharge rises in February, its invoices exceed the PO price by more than the 2% tolerance and go on hold. Linda releases them once Mike confirms the surcharge clause, but one invoice applies March's surcharge to a February shipment.
- **The customer's metal (February).** A mill ships a load of steel bought by a prime contractor to Fabrication's dock, with the invoice addressed to the prime "care of" Nashoba Fabrication. The dock receives it as customer-supplied material. The invoice reaches `ap-ma@`, and a temp enters it against a similar open PO. It is paid on February 27: `$61,300` that Nashoba never owed. The mill is happy. The prime pays the mill again a month later, and asks for a refund for the duplicate.
- **The duplicate (March).** A gas supplier emails an invoice and then mails the same invoice with a suffix (`77815` and `77815-1`). Both are matched against a blanket order with plenty of quantity left, and both are paid.
- **Discounts, taken and missed (all quarter).** With the line nearly drawn, Renee pays most vendors on day 45 to 60, past their terms. The cutter distributors' `2% 10` discounts are mostly lost. Two payments still take the 2% after the discount period ended, and the distributor bills the difference back as a short payment.
- **Intercompany work (January-February).** Fabrication machines a batch of large housings for Arroyo and invoices it `$118,000`. Arroyo enters it as an ordinary vendor bill under a new vendor record, not as intercompany, and pays part of it.
- **The fiscal year end (March 31).** Year end falls on a Monday:
  - Steel received on March 27, 28 and 31 has no invoice yet.
  - Outside processing returned with certifications in the last week of March will be billed in April.
  - Freight on several of those shipments arrives in April.
  - The machine repair firm finishes a job on March 28 and invoices on April 15.
  - Tom books a year-end accrual for goods received but not invoiced from Fabrication's system. He estimates Arroyo's accrual from a list Carlos emails him, which misses the receipts that were never entered.
  - The covenant test for the year fails†, and the bank's reservation-of-rights letter arrives in April.

## 7. Kinds of events

Over the quarter, its records show these kinds of events:

- **Purchasing:** purchase orders for metal, outside processing, tooling and services, blanket orders, change orders, orders split under approval limits, orders created after the work was done, orders for customer jobs and for overhead.
- **Receiving:** full and partial receipts, receipts entered late or never, customer-supplied material with no price, goods delivered to the wrong plant, certifications that arrive after the goods.
- **Invoices:** three-way matches within tolerance, price and quantity variances, surcharges, freight billed separately, invoices before receipts, holds released with and without authority, duplicate invoices, invoices addressed to someone else, intercompany invoices booked as vendor bills.
- **Payments:** weekly ACH and check runs, payments stretched past terms, discounts taken, missed and taken late, a payment to a fraudster's account and a partial recovery, a vendor paid twice for the same work, a refund owed back.
- **Vendor records:** new vendors, bank-detail changes with and without the required call-back and approval, vendors listed in both systems, names that differ between systems.
- **Period end:** goods received but not invoiced, services completed but not billed, an accrual estimated from an incomplete list, a covenant test.
- **Financing:** draws on the revolving line before payment runs, nightly sweeps, term and equipment payments.

## 8. What the world must also remember

So that an agent working these records can be graded, the world keeps, in its own state and not in any institution's records, the truth behind every record:

- which purchase order and receipt each invoice really belongs to, and the right quantity and price;
- which goods actually arrived, at which plant, and which belong to customers;
- which invoices are duplicates or not owed at all;
- every approval that was skipped or split, and by whom;
- that the bank-detail change was fraud, the amounts lost and recovered, and what is still owed to the real vendor;
- the true goods-received-not-invoiced balance at each plant on March 31, with each item and amount.
