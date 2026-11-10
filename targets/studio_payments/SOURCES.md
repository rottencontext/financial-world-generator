# Sources: Repflow

Like `vacation_rentals`, this world is not modeled on one small company. It was written as a target for End Close (endclose.com), which reconciles payments for high-volume payments companies across processors, banks and ledgers. A platform that collects for hundreds of small merchants is the kind of company whose records End Close is built for. The mechanics come from Stripe's documentation and from published summaries of Nacha's ACH return rules. The company's size, location, people, prices and events are invented.

## Mechanics checked against published rules

| Document | What it gave |
|---|---|
| [Stripe: handle refunds and disputes (marketplaces)](https://docs.stripe.com/connect/marketplace/tasks/refunds-disputes) | Refunds, disputed amounts and fees are debited from the platform balance for destination charges; a refund without `reverse_transfer` leaves the funds with the connected account; partial refunds reverse a proportional share of the transfer; application fees are not refunded unless asked; refunds wait as pending when the platform balance is short; negative connected balances get a reserve, and US accounts with `debit_negative_balances` have their bank account debited; processing fees are not returned on refunds |
| [Stripe: how disputes work](https://docs.stripe.com/disputes/how-disputes-work) | Disputed amount and fee debited when the dispute opens; 120-day typical dispute window; 7-21 days to respond; 60-75 days for the issuer to decide; 2-3 months overall; received fee not returned (outside Mexico); countered fee returned on a win; partial disputes and disputes after partial refunds; about 40% of Visa/Mastercard early fraud warnings become fraud disputes if not refunded |
| [Stripe: manage connected account payouts](https://docs.stripe.com/connect/payouts-connected-accounts) | Daily rolling payouts by default; payout statuses pending, in transit, paid (1-2 business days after submission), failed, canceled; a failed payout disables the external account until it is updated; instant payouts typically within 30 minutes |
| [Stripe: bank reconciliation](https://docs.stripe.com/reconciliation/bank-reconciliation) | Daily automatic payouts with a 2-business-day payout speed; payouts matched to bank deposits by a matching key; banks don't credit payouts on Sundays; payouts landing in the following month |
| [Increase: ACH returns](https://increase.com/documentation/ach-returns) | Return windows: two business days for most returns, 60 calendar days for consumer debits claimed as unauthorized; R01 insufficient funds; R02, R03, R04 administrative; R05, R07, R10, R29 unauthorized |
| [CU Web Training: RDFI return timeframes](https://cuwebtraining.com/rdfi-returns-2-banking-days-vs-60-calendar-days-understanding-the-difference) | The two Nacha return timeframes: two banking days and 60 calendar days |

## Invented for this world

The company name, Denver, every person, the bank and account numbers, the number of studios, the $38 million volume, the payment count, the card/ACH mix, subscription prices, the 1% and 1.25% application fees, the reserve account, the 2021 migration, and every event in section 6. Stripe's per-transaction fees, dispute fee amounts, Connect account fees and exact ACH settlement timing were not checked and are left to the world.

## Finding a company to anchor it

Vertical software companies that collect payments for small businesses (fitness, salons, clinics, restaurants) sometimes raise through Regulation Crowdfunding. EDGAR full-text search for Form C filings mentioning "Stripe Connect", "payment facilitator" or "payments revenue" is the place to look for a real company's volume, take rate and losses from disputes.
