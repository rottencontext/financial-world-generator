# Hollow Oak Cookie Co.: a bakery brand whose books live in invoices, purchase orders and email (first 60 days)

This describes one business, its past and its year. Facts marked † come from the real company's public Regulation Crowdfunding filing that this business is modeled on (see `SOURCES.md`). Facts marked ‡ come from published rules on how a natural-foods distributor deducts from and pays its suppliers. A mark vouches for the fact it follows, not for the date or reason the story gives it. The company, its people and its account numbers are invented.

This world is built for testing accounts-receivable and accounts-payable agents. Its money moves through the same channels as every other world, but most of the work sits in the paper around the money: invoices, purchase orders, receiving records, remittance advice, portal statuses and email. Each of those is a record kept by the institution that holds it (section 3).

## 1. The business and the time frame

- **Business:** Hollow Oak Cookie Co., a maker of premium sweet-and-salty cookies in six flavors, in a 4.7 oz bag and a 1.34 oz snack pack†. It bakes in-house in a leased facility near Asheville, North Carolina†. It sells online, to grocery and specialty retail, foodservice, hospitality and travel†, and is in about 2,000 points of distribution†.
- **Size:** 23 employees†: bakers, packers, a warehouse and shipping lead, a part-time bookkeeper, an operations manager and the two founders. Most bakers and packers are hourly.
- **Time range:** 2025-01-01 to 2025-03-01, currency USD (60 days). Keep the business at full size: about 90 wholesale invoices a month, weekly distributor payments, daily Shopify payouts. The window covers New Year's Day (Wednesday), Martin Luther King Jr. Day (Monday, January 20) and Presidents' Day (Monday, February 17), when banks don't post. It also covers two month-end cutoffs (January 31 and February 28) and biweekly paydays on January 3, January 17, January 31, February 14 and February 28. Only what can happen in these 60 days happens. Later in the year, a second cash advance, a revolving line and a holiday rush come, but none of them happen in this run.
- **Revenue†:** `$1,246,138` in 2024 and `$1,366,989` in 2025. Cost of goods `$525,125` in 2025† (a 61.6% gross margin†). Net loss `$207,403` in 2025†.
- **2025 by channel (invented, summing to the real total):** wholesale and distributor sales about `$1,130,000`, the online store about `$235,000`. Wholesale is where the work is: about 90 invoices a month across about 160 active accounts.
- **The shape of the year:** sales grow, but cash falls from about `$68,000` to about `$37,000`† while receivables rise from about `$52,000` to about `$72,000`† and debt stacks up (section 2). Every dollar stuck in a deduction, a rejected portal invoice or an unapplied payment matters.

## 2. History before the start

- Founded in 2015 by Nora Brandt (now CMO) and Owen Ellery (now CEO), first as an LLC†. In this world it is still an LLC through 2025.
- Debt on the books during 2025, from the filing's year-end table†: an SBA loan at 3.75% maturing in 2050 (about `$438,000` left at year end), two smaller SBA loans at Prime + 2.75% and Prime + 4.50% maturing in 2034 (about `$42,000` and `$140,000`), equipment financing for the ovens and packaging line paid in fixed monthly installments (about `$123,000`), two merchant cash advances repaid as a share of card and online collections (about `$209,000` and `$81,000`), a small merchant loan with a fixed monthly fee, a revolving line of credit at 59.5% APR, and a 2% demand note from a founder (about `$68,000`). In this world the second cash advance and the revolving line are taken during 2025; the rest already exist on 2025-01-01.
- On 2025-01-01: about `$68,000` in checking†; about `$52,000` of open receivables†, including December invoices to the distributor that have not been paid and two invoices stuck in the airline's portal; about `$59,000` of inventory†; December bills from the flour mill, the butter supplier and the packaging printer unpaid on net-30; the December card statement awaiting payment; the December 31 payroll not yet in the bank.
- The bookkeeper works two days a week. There is no AR clerk; the operations manager chases payments when she remembers. About 40 deductions from the distributor in 2024 were never disputed.

## 3. Institutions (the only sources of data)

Each keeps its own records the way it really would. Documents (invoices, purchase orders, receiving records, remittance advice, statements) are records too: one row per document with the fields printed on it, line items as their own rows, and the document as its sender wrote it, not as the books later recorded it.

- **Laurel Fork Community Bank:** operating checking `••4471`. Each posted transaction with the description the bank shows (`ACH CREDIT UNFI EFT 000082214`, `DEPOSIT MOBILE CHECK`, `WIRE IN JETBLUE AIRWAYS`), a running balance, and monthly statements. A lockbox is not used: checks arrive by mail and are deposited by phone, often in batches a week late.
- **QuickBooks Online (the books):** the chart of accounts, customer and vendor lists (with the names as first typed, duplicates and all), sales invoices, credit memos, bills, bill payments, received payments and how each was applied, deposits, journal entries, and the accounts-receivable and accounts-payable aging. What is in QuickBooks is what the bookkeeper entered, when she entered it, including mistakes.
- **The AR and AP mailboxes (`ar@`, `ap@`, and the founders' own inboxes):** every email as a row: thread, date, from, to, subject, body and the ids of attached documents. Vendors send invoices and statements here; customers send purchase orders, remittance advice, disputes and "please resend" requests; the company sends invoices, reminders and replies. Some emails go to the wrong inbox and are forwarded days later; some are never answered.
- **The distributor's supplier portal (UNFI-style, for Whole Foods and natural grocers):** purchase orders, invoices received, payments with a remittance listing every invoice and deduction in the payment, and deductions as their own lines. Deductions carry the distributor's codes: a quantity or pricing chargeback on an invoice is `[Invoice#]-111`‡, a promotion billback is `MCB(yyyymmdd)`‡, concealed damage is `[DC#]CNDM(mmmyy)`‡, and compliance fines are `LCBOL(PO#)` for an incomplete bill of lading or packing slip‡ and `AVL(PO#)` for a delivery more than 30 minutes late for its appointment‡. Disputes are filed in the portal within 12 months of the deduction‡ and take 30 to 45 days to resolve‡.
- **The airline's procurement portal (Coupa-style):** the airline buys snack packs for its cabins. Every order is a purchase order in the portal; invoices must be submitted in the portal against the PO, with matching PO number, line prices and quantities, and the airline's receiving record must exist before an invoice can be approved. Each invoice moves through statuses (submitted, rejected with a reason, pending receipt, approved, scheduled, paid) and payment comes by ACH 45 days after approval.
- **Shopify and Shopify Payments:** online orders, refunds and daily payouts to checking net of fees, less the share held back for the first cash advance.
- **Bill.com:** the company pays most vendor bills here. Each payment has a scheduled date, a funding debit from checking, and a delivery method (ACH, or a mailed check that clears days or weeks later). Vendor bank details are stored here, and changing them leaves a record of who changed them and when.
- **The company card (Amex):** ingredients bought in a pinch, shipping supplies, software, trade-show travel; a monthly statement paid from checking.
- **Gusto:** payroll every two weeks, with a journal of wages, taxes and withholdings for each run.
- **Lenders:** SBA loan servicers (monthly ACH), the equipment lessor (monthly ACH), the cash-advance providers (one takes a share of Shopify payouts, the other debits checking every business day), the revolving line (draws and weekly debits), the founder (the note is repaid only when cash allows).

## 4. The cast

- **Owen Ellery, co-founder and CEO.** Runs daily operations, manufacturing and financial planning†. Approves every bill over `$2,500` from his phone, sometimes days late. Takes the second cash advance in July without telling the bookkeeper.
- **Nora Brandt, co-founder and CMO.** Runs marketing and the brand† and, in this world, the online store and the big accounts. Agrees to promotions with buyers by phone and forwards the paperwork late or not at all.
- **Denise Hall, operations manager.** Schedules production, books freight, receives deliveries from suppliers. Signs receiving slips but does not always enter them.
- **Priya Raman, part-time bookkeeper (Tuesdays and Thursdays).** Enters bills and invoices, applies payments, reconciles the bank monthly, a few weeks behind. Careful, but works from what reaches her inbox.
- **Bakers, packers and the shipping lead.** Hourly, paid every two weeks; overtime in November and December.
- **Customers:**
  - **The distributor (for Whole Foods† and natural grocers).** Places weekly POs for several distribution centers. Pays weekly by ACH, one payment covering many invoices less many deductions, with the detail only in the portal remittance. Deducts for promotions, damage, shortages and compliance, some valid and some not.
  - **JetBlue†, through its procurement portal.** Large POs every few weeks; strict about PO numbers and receiving; rejects invoices with any mismatch.
  - **The Fresh Market†, World Market† and Total Wine & More†.** Buy direct on net-30 or net-45 through their own vendor setups; send remittance advice by email, sometimes after the money, sometimes never; one pays by check, one by ACH, one by wire.
  - **About 150 independent shops, cafés, hotels and gift stores.** Net-30, paying by check, ACH or card; a few always late; some pay several invoices with one check and no stub; one pays from an owner's personal account under a different name.
  - **Online customers.** Orders spike in November and December; a few refunds and chargebacks.
- **Vendors (about 45 active):** a flour mill and a butter-and-dairy supplier (weekly deliveries on POs, invoices by email, net-30), a chocolate supplier (shipments with freight billed separately), a pretzel and snack-ingredient supplier, a packaging printer (bags printed to order, quantities over or under the PO by up to 10%), a corrugated box supplier, two freight carriers and a freight broker, the facility landlord (rent by ACH on the 1st), utilities, an equipment repair technician (bills by the hour, sometimes without a PO), a food-safety auditor, a sales broker paid a commission on distributor sales, a trade-show organizer, software subscriptions, an insurance broker.

## 5. Money flows

| Flow | How it moves |
|---|---|
| Distributor -> checking | weekly ACH, one payment for many invoices less deductions; detail only in the portal remittance |
| Airline -> checking | ACH 45 days after a portal invoice is approved, one payment per invoice or a few batched |
| Retail chains -> checking | ACH, wire or check on net-30/45; remittance by email, if at all |
| Independent accounts -> checking | checks deposited in batches by phone, ACH, card payments through an invoice link |
| Online customers -> Shopify -> checking | daily payouts net of fees and the advance holdback |
| Checking -> Bill.com -> vendors | bill payments by ACH or mailed check, funded by a debit from checking |
| Checking -> Amex | monthly statement |
| Checking -> Gusto -> employees, tax agencies | every two weeks |
| Checking -> lenders | SBA and equipment monthly; one advance daily; the line weekly |
| Lenders -> checking | the second advance and the line's draws |

## 6. Stories

- **The deduction pile (all window).** Every weekly distributor payment is short. Most of the January deductions are December promotions Nora agreed to by phone. Two promotions ended in November but are still being deducted. A run of `-111` shortage chargebacks hits three December invoices whose proof of delivery shows full quantity. A concealed-damage deduction from October repeats in January for the same shipment. Priya applies payments to the right invoices only when she downloads the portal remittance, so for weeks the deposits sit as unapplied cash in QuickBooks.
- **The airline's stuck invoices (January-February).** The two December invoices stuck in the airline's portal move in different ways. One was rejected for a typo in the PO number. It is resubmitted on January 14 with a second typo and rejected again, then approved on February 3. The other waits in "pending receipt" because the airline's warehouse never recorded the delivery. Denise sends the signed proof of delivery twice before it is approved on February 20. A new February PO changes the snack-pack item number. The first invoice against it is rejected for a price mismatch, because it was billed at the old price. Each rejection arrives as a portal status and an automated email.
- **The packaging printer (January).** A bag reprint arrives on January 13, 8% over the PO quantity. The printer bills the overrun at a price `$0.02` a bag higher than the PO. Denise's receiving slip shows the right count but is entered a week late. Priya catches the price but pays the quantity.
- **A specialty chain short-pays and pays twice (February).** The chain pays a January invoice short by a promotional allowance nobody wrote down. Then it pays a different invoice twice, and sends one wire covering three invoices with a remittance that lists the wrong invoice numbers.
- **The duplicate invoice (February).** The butter supplier emails an invoice, then sends its monthly statement with the same invoice under a slightly different number (`INV-20417` and `20417`). Both are entered and both are scheduled in Bill.com. One is caught the day before it pays. The other is not, and the supplier issues a credit on the March statement.
- **Names that do not match (all window).** The chocolate supplier bills as `Piedmont Cocoa Co`, `PIEDMONT COCOA COMPANY LLC` and `Piedmont Cocoa (Freight)`. The distributor's payments show under three different bank descriptions. QuickBooks has two vendor records for the same freight carrier.
- **Work done but not billed (each month end).** The December oven repair (done December 18) is invoiced on January 9, and the trade-show organizer's December balance in mid-January. At January 31, the freight broker's January loads are not yet billed. At February 28, a repair done on February 25 is not invoiced until March 10.
- **Dunning, or not (all window).** Overdue independent accounts get a reminder only when the operations manager has time. Replies include "paid on the 3rd" (it was, to the wrong invoice), "please resend with our PO number" and "we never received the order". Two accounts cross 90 days in February.
- **Debt service (all window).** The first cash advance takes its share of every Shopify payout. The SBA and equipment payments debit monthly. Checking dips near zero in the slow weeks after the holidays, and Owen delays the packaging printer's January bill by three weeks.

## 7. Kinds of events

Over the year, its records show these kinds of events:

- **Receivables:** invoices on net-30/45 and through portals, partial payments, one payment for many invoices, overpayments and duplicate payments, payments with no remittance or a wrong one, payers whose names differ from the customer record, unapplied cash, credit memos, write-offs, accounts past 120 days, reminders and replies.
- **Distributor deductions:** promotion billbacks, shortage and pricing chargebacks, concealed damage, compliance fines, valid and invalid ones, duplicates, disputes filed and won or denied, deductions never disputed.
- **Portals:** POs received, invoices submitted, rejected for price, quantity or PO-number mismatches, held for receipt, approved, scheduled and paid, resubmissions.
- **Payables:** POs to suppliers, receiving records, invoices by email and on statements, quantity and price variances, freight billed separately, duplicate invoices, bills without POs, approvals delayed, payments by ACH and check, checks clearing late, a vendor credit, vendor names that vary.
- **Period end:** services received but not invoiced at each month end, card charges not yet coded, a bank reconciliation weeks behind.
- **Financing:** monthly SBA and equipment payments, daily advance debits and payout holdbacks, a founder loan.
- **People:** biweekly payroll.

## 8. What the world must also remember

So that an agent working these records can be graded, the world keeps, in its own state and not in any institution's records, the truth behind every record: which invoices each payment really settles and by how much; whether each deduction is valid under what was agreed; which PO and receipt each vendor bill belongs to and the right quantity and price; which account each expense belongs in; which bills are duplicates; and the services received but not billed at each month end, with their amounts.
