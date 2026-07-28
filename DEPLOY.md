# Deploying to Vercel

This repo is a static site — a landing hub (`index.html`) linking three
surfaces: the intake clay model, the scoping doc, and the pre-quote catalog.
No build step. `vercel.json` sets clean URLs and a `noindex` header.

> The deploy must run from your own machine or the Vercel dashboard — it can't
> be run from the Claude Code web sandbox (outbound access to Vercel is blocked
> by the environment's network policy, and there's no token here).

## Access — do this, the content is internal

These are internal working drafts. To keep the link shareable but not public,
turn on **Deployment Protection** (Vercel Pro/Enterprise):

1. Vercel dashboard → your project → **Settings → Deployment Protection**.
2. Enable **Vercel Authentication** (viewers must be logged-in Vercel team
   members) or **Password Protection** (one shared password).
3. Apply it to **all deployments** (production + preview), not just preview.

On the free/Hobby plan the URL is public (only obscured by a random name), so
use a Pro team if the access control matters. The repo already sends
`X-Robots-Tag: noindex` so search engines won't index it either way.

## Option A — Git integration (recommended)

1. Push this branch (already done) or merge to your default branch.
2. Vercel dashboard → **Add New → Project → Import** the `danirivasf/TestDaniela`
   repo.
3. Framework preset: **Other** (it's static). Leave build/output empty.
4. Choose the branch to deploy (`claude/sox-readiness-intake-4ryx6p` or `main`).
5. **Deploy**, then set Deployment Protection as above.

Every push to the chosen branch will redeploy automatically.

## Option B — Vercel CLI (from your machine)

```bash
npm i -g vercel
cd TestDaniela
vercel            # first run links/creates the project (accept static defaults)
vercel --prod     # promote to the production URL
```

Then enable Deployment Protection in the dashboard.

## After deploy — check these

- `/` → the landing hub
- `/clay-model/` → the interactive prototype (submit a request, run it through)
- `/spec/product-licensing-intake-scoping` → the scoping doc
- `/pre-quote-pricing/request-type-catalog` → the straw-man catalog

The clay model persists to `localStorage` in a normal browser tab, so state
survives reloads on the deployed site (unlike an embedded artifact sandbox).
