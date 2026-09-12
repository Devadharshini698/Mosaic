# Validation record

## Programmatic checks completed

- All 10,950 official records processed, with 1,095 unique dates for each of ten channels.
- Zero malformed/excluded rows, duplicate date/channel pairs, missing expected pairs, or discrepancies beyond rounded-ROAS tolerance.
- Both presets allocate exactly ₹5,000,000 and satisfy Email/SMS caps.
- Arithmetic-mean ROAS calculated from every supplied daily ROAS; no intermediate ROAS rounding.
- Baseline revenue ₹26,568,802.42; linear maximum ₹33,853,561.64. Baseline channel rows reconcile without adjustment; linear rows reconcile after −₹0.01.
- Independent Node.js decimal.js implementation agrees on both totals and each allocation. It also calculates ₹26,568,802.44 for the alternate fractional-paise proportional convention.
- 16 Python unit tests pass, covering schema failures, missing values, nonfinite/negative numbers, fractional counts, monetary precision, date range, weekdays, zero spend, exact and conflicting duplicates, overlapping errors, missing coverage, half-up rounding, cap redistribution, remainder ties, zero weights, capacity errors, and linear exchange optimality.
- TypeScript, ESLint, and Vite production build passed, including the final documentation/demo integration build.
- `npm install` audit reported zero dependency vulnerabilities.

## Browser checks completed

Desktop browser showed correct baseline and linear totals. Switching to linear produced Email ₹15L, SMS ₹12L, Affiliate ₹23L. Entering Email ₹1,500,000.01 displayed a cap warning. Reset restored the baseline.

Combined Email filter and date search 2023-01-01 returned exactly source row 6. Its dialog showed spend ₹71,900.90, recorded revenue ₹344,908.62, spend × reported ROAS ₹345,124.32, and difference −₹215.70 with a rounding explanation. Sorting Email by descending spend returned 1,095 rows; next page showed records 16–30 and page 2 of 73. A nonexistent query showed an explicit empty state.

Channel charts showed ROAS rankings, monthly means, spend quartiles, and weekday/weekend comparisons. Meta Ads' extreme quartiles showed 3.24× and 1.24×. Google Search weekday/weekend means showed 4.03× and 2.49×. An observed fixed chart scale was corrected to use the actual maximum so seasonal means above 15× are not clipped.

Methodology navigation and provenance values were verified. Mobile viewport testing at 390×844 reported a 375px content viewport and 375px document scroll width: no page-level horizontal overflow. Tables deliberately scroll within their containers. Authentic screenshots are retained under `artifacts/demo/`.

## Demo and public HTTP

The video is 107.836 seconds, 1920×1080, 24 fps, H.264/AAC, with 29 burned-in caption cues and a separate SRT. Mean audio level is −20.6 dB and peak is −2.7 dB. Representative encoded frames were inspected; final captions fit the lower caption band. See `artifacts/demo/validation.json`.

After deployment, seven unauthenticated endpoint checks returned HTTP 200, with no cookies or bypass tokens. The report JSON, full record JSON, both CSVs, video, and subtitles matched local bytes exactly. Production browser QA confirmed combined search/filter, source row 6 evidence, methodology rounding disclosure, and the correct baseline. No browser console errors were observed. Full receipts are in `artifacts/http-validation.json`.
