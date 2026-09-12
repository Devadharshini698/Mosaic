# Mosaic Mix Lab

A public marketing budget optimizer for the Mosaic Fellowship **Marketing Mix Optimizer** challenge. It processes the official 10,950-row dataset, makes both interpretations of the allocation problem explicit, and preserves every daily record for inspection.

**Requested GitHub repository:** https://github.com/Devadharshini698/Mosaic

**App origin:** https://mosaic-mix-lab-ajay.ochre-deer-1487.chatgpt.site

The app origin is allocated by OpenAI Sites. Consult `docs/deployment.md` for verified publication status. A configured origin alone does not mean deployment succeeded.

## Results

| Convention | Expected monthly revenue (INR) |
|---|---:|
| Suggested ROAS-proportional baseline, executable whole-paise allocation | **26,568,802.42** |
| Mathematical maximum under the stated constant-ROAS formula | **33,853,561.64** |
| Alternate proportional convention, fractional paise retained until final total | **26,568,802.44** |

The brief recommends proportional allocation but asks for an optimal allocation. These are not equivalent. The UI defaults to the suggested proportional baseline and offers the actual linear maximum alongside it. No private answer key was accessed, and no agreement with it is claimed. The alternate ₹0.02 difference is solely an allocation rounding convention, not a different ROAS definition.

The linear maximum allocates ₹1,500,000 to Email, ₹1,200,000 to SMS, and ₹2,300,000 to Affiliate. All other channels receive zero. Its individually rounded channel returns sum to ₹33,853,561.65; a **−₹0.01 rounding adjustment** reconciles them to the rounded exact total. The baseline has no rounding adjustment. Complete tables are in `docs/results.md` and `public/results/allocation.csv`.

## Run locally

Requirements: Node.js 22+, npm, Python 3.11+. The analysis has no third-party Python dependencies.

```sh
npm ci
python engine/download.py  # optional: original dataset is included and hash pinned
npm run verify
npm run dev
```

Open the URL printed by Vite. `npm run verify` runs the complete analysis, 16 unit tests, independent Node.js decimal reconciliation, lint, TypeScript checks, and a production build. `npm run build` outputs a static site in `dist/`.

## Architecture

- **Engine:** Python `Decimal` parses original numeric lexemes; `Fraction` carries exact ROAS and revenue calculations. Allocations use integer paise and largest remainders. `ROUND_HALF_UP` is applied at presentation boundaries.
- **Independent verification:** Node.js and decimal.js at 80-digit precision independently read the raw JSON, recompute channel means, both allocations, and both totals.
- **App:** React 19, TypeScript, Vite, custom responsive CSS, Lucide icons, decimal.js for editable scenarios. No backend or login is required.
- **Evidence:** The read-only explorer loads the entire official dataset as generated record evidence. It provides date/channel/row search, channel filters, sorting, pagination, accessible record dialogs, and JSON/CSV downloads.
- **Charts:** Mean versus spend-weighted ROAS, monthly seasonality, equal-count spend quartiles, and weekday/weekend comparisons. These are descriptive associations, not causal forecasts.

The generic invoice-audit language in the task template is not applicable to this marketing dataset. There are no invoices, GST rates, billed line items, or overcharges to invent. Record details instead show spend, reported revenue, spend × rounded ROAS, the difference, and an explanation.

## Data integrity

Only `https://mosaicfellowship.in/data/marketing_daily.json` supplies production observations. Original bytes are retained under `data/`. Their SHA-256 is `0c2e4314f496fcd830fe8688cdbe3716ab24aa53c1de052566a9cef150975e50`.

Every channel has 1,095 rows. The actual date range is 2023-01-01 through 2025-12-30, including leap day. It is not three complete calendar years. All 10,950 official records pass validation with zero exclusions and zero missing pairs. Checks include schema, finite nonnegative numeric values, integral counts, monetary precision, valid dates, weekdays, known channels, duplicates, zero spend, and full coverage. Exact duplicates are excluded once; conflicting duplicates are all quarantined; overlapping issues never multiply records. Incomplete date/channel coverage fails the run rather than silently computing a partial answer. Test-only mutations of official records exercise failure paths; they are never used as production data.

Daily reported ROAS is rounded to two decimals. Thus `spend × ROAS` need not equal recorded revenue. All official ratios are within the half-cent ROAS rounding tolerance. This is not overcharge evidence or a reason to rewrite the provided ROAS.

## Files and artifacts

- `docs/challenge-requirements.md`: official requirements and form fields
- `docs/write-up.md`: at most 500 words
- `docs/form-description.txt`: at most 500 characters
- `docs/results.md`: exact answers and per-channel breakdown
- `docs/tech-stack.md`, `docs/deployment.md`, `docs/validation.md`
- `artifacts/independent-reconciliation.json`
- `artifacts/demo/mosaic-mix-lab-demo.mp4`: narrated 107.84-second demo
- `artifacts/demo/demo.srt`, `transcript.md`, `demo-script.md`, `validation.json`
- `public/demo/`: published video, subtitles, and transcript

To regenerate the video on Windows: install `imageio-ffmpeg==0.6.0`, capture the specified authentic app screenshots, run `powershell -NoProfile -File engine/narrate.ps1`, then `python engine/make_demo.py`. It uses the installed Microsoft Zira Desktop synthetic voice, H.264/AAC, readable burned-in captions, and a separate SRT. Screenshot capture is a browser QA operation; no synthetic replacement screens are generated.

## Deployment and assumptions

The selected platform is **OpenAI Sites**, not Vercel, Netlify, or Cloudflare Pages. Public no-login access must be verified over unauthenticated HTTP after deployment. Static `dist/` can also be deployed to Vercel, Netlify, or Cloudflare Pages using build command `npm run build` and output directory `dist`. No prohibited builder or host is used.

Historical averages are held constant for the challenge's formula. Saturation, cross-channel attribution overlap, incremental lift, and future demand are not modeled. Channel caps and a full ₹50 lakh budget are checked for every preset; custom drafts visibly indicate invalid inputs, cap violations, or incomplete budgets. Source data licensing remains with its provider; no broader license is asserted for the dataset.

**No fellowship application has been submitted. No CV, private contact details, credentials, or personal files are included.**
