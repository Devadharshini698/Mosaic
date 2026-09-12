# Deployment notes

Target GitHub repository: https://github.com/Devadharshini698/Mosaic (provided by the user).

App origin: https://mosaic-mix-lab-ajay.ochre-deer-1487.chatgpt.site

Hosting platform: **OpenAI Sites**. Do not describe this as Vercel, Netlify, or Cloudflare Pages. It uses the managed Sites publishing service. The required audience is public with no login.

Status: **live and publicly accessible without login**. The Sites deployment succeeded, and seven unauthenticated HTTP checks returned 200. Every JSON, CSV, video, and subtitle payload matched the corresponding local file byte for byte. Receipts are recorded in `artifacts/publication-status.json` and `artifacts/http-validation.json`. Production browser QA confirmed the baseline, combined record search/filter, evidence dialog, and methodology; no browser console errors were observed.

GitHub status: **not published**. The requested repository was publicly readable and empty when inspected. The browser session was signed in as Ajayyy00 and exposed no write/upload controls. No GitHub credential was available through Git Credential Manager in noninteractive mode. An actual push to `origin main` failed because authentication could not be obtained without prompting. Public-repository publication requires write access for an authenticated account; no account switching, new personal-access token, or permission expansion was performed. The complete source is committed locally and provided as `artifacts/mosaic-source.bundle` and `artifacts/mosaic-source.zip` for handoff.

Static deployment:

```sh
npm ci
npm run verify
```

Upload the generated `dist` output using the chosen public hosting provider. Hash routes require no server rewrites. JSON, CSV, and demo video live under `results/` and `demo/`. Build artifacts contain no credentials. `.openai/hosting.json` stores only the Sites project ID and the static output directory.

For the requested GitHub repo, the prepared local Git checkout uses that repository as `origin`; push `main` with an authorized account. Do not force push. No repository contents existed at the read-only inspection. Recheck remote state before pushing if access is granted later.

No fellowship submission action is part of deployment.
