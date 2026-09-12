# Demo shot list

1. The allocation problem (13.3s) — 01-overview.png

Mosaic Mix Lab turns the official Marketing Mix Optimizer dataset into a transparent budget decision. The question is simple: how should fifty lakh rupees per month be allocated across ten marketing channels? Email is capped at fifteen lakh, and SMS at twelve lakh.

2. Complete official data (13.0s) — 05-channels.png

The engine processes all ten thousand, nine hundred and fifty observations, with one thousand and ninety five rows per channel. It checks dates, weekdays, missing values, monetary precision, duplicates, and complete coverage. All official records pass.

3. The proportional baseline (14.9s) — 01-overview.png

The brief suggests allocating proportionally to average daily return on ad spend. With allocations rounded to whole paise, expected monthly revenue is two crore, sixty five lakh, sixty eight thousand, eight hundred and two rupees, and forty two paise. Email makes the largest contribution.

4. The mathematical maximum (16.8s) — 02-linear.png

But proportional is not mathematically optimal. Under the stated constant return formula, the maximum allocates fifteen lakh to Email, twelve lakh to SMS, and twenty three lakh to Affiliate. Expected revenue is three crore, thirty eight lakh, fifty three thousand, five hundred and sixty one rupees, and sixty four paise.

5. Patterns and model limits (12.3s) — 06-patterns.png

The performance charts expose limits of constant returns. Meta Ads averages three point two four times return in the lowest spend quartile, falling to one point two four in the highest. These are descriptive associations, not proof of causality.

6. Trace every observation (10.0s) — 03-search.png

The evidence explorer supports combined date search and channel filters, sorting, and pagination. Here, searching Email on January first, twenty twenty three, isolates source row six.

7. An auditable record (11.9s) — 04-evidence.png

Opening that row reveals the recorded spend, revenue, and their reconciliation. Multiplying spend by the rounded reported return creates a difference of two hundred and fifteen rupees and seventy paise. This is rounding, not an overcharge.

8. Reproducible and explicit (15.7s) — 07-methodology.png

Python rational arithmetic and an independent JavaScript decimal implementation agree. The methodology separates both allocation conventions and explains the one paise adjustment in the linear breakdown. Downloadable reports preserve the evidence. No private answer key agreement is claimed, and no fellowship application has been submitted.
