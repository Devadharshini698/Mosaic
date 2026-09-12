# Official challenge requirements

Read on 12 September 2026 from https://mosaicfellowship.in/challenge, Marketing tab, problem 7, **Marketing Mix Optimizer**. Submission form inspected read-only at https://mosaicfellowship.in/submit.

## Dataset

One official JSON file: https://mosaicfellowship.in/data/marketing_daily.json. 10,950 rows, 1,095 days × ten channels. Fields: date, weekday, channel, spend, revenue, ROAS, impressions, clicks, conversions, new customers, CTR, CPC, CPA, AOV. Process the complete supplied data programmatically; do not replace it with generated observations.

## Required calculation

Calculate average daily ROAS for each channel over all supplied dates. Allocate ₹5,000,000 monthly, with Email ≤ ₹1,500,000 and SMS ≤ ₹1,200,000. Compute total expected monthly revenue as the sum of allocation × average ROAS. Report the answer in rupees to two decimals. The page recommends proportional allocation as its simplest approach but also asks for an optimal allocation; this ambiguity is documented, not hidden. No mandatory minimum is imposed on other channels. The page does not specify weighted ROAS or a rounding convention for intermediate allocations.

## Product and findings

A working app with channel performance charts and an interactive optimizer; a table covering all ten allocations and expected returns; a brief write-up covering patterns such as diminishing returns, seasonality, and weekday/weekend variation.

## Restrictions and submission

App must be public and accessible without login; public GitHub repository required. Lovable and Emergent are not allowed. Streamlit and Render are forbidden hosting choices. The page gives Vercel, Netlify, and Cloudflare Pages as fast-loading examples. The user's request also permits another managed host only if public no-login access is clearly verified. The write-up is limited to 500 words.

Form fields observed:

1. Full Name
2. Email
3. Phone
4. College
5. Graduation Year
6. Problem Statement
7. Solution Name
8. Deployed App URL
9. Public GitHub Repo URL
10. Numerical Answer (two decimals)
11. Tech Stack
12. Brief Description (**500 characters maximum**)
13. Demo Video URL (optional)
14. Notes (optional)
15. CV upload (PDF, DOC, or DOCX; required; maximum 5 MB)
16. Original-work confirmation

No personal form fields were populated. No CV was collected. No original-work declaration was made on the user's behalf and no application was submitted. No additional word/character limits were displayed for the other fields.

## Scope interpretation

The user selected marketing. Invoice-specific template requirements (GST, billed amounts, overcharge categories) are inapplicable. Corresponding views show channel revenue contributions and daily spend/revenue evidence. Attribution overlap cannot be inferred from aggregated channel-day data; it is a limitation, not a detected billing error.
