# Wealth Tax Watch

Biweekly global briefing on wealth tax proposals, public opinion and international tax cooperation, published for the Global Tax Fairness Fellowship cohort.

- **Latest issue:** No. 01, September 1-23, 2026
- **Live site:** https://wealth-tax-watch.vercel.app

## Layout

```
issues/01/index.html   Issue 01. Each issue is one self-contained page. Edit these.
index.html             Copy of the latest issue            (generated)
archive.html           List of every issue                 (generated)
feed.xml               RSS feed                            (generated)
assets/og-image.png    Link-preview image
scripts/build.py       Generates the three files above
scripts/og-image.*     Source for the link-preview image
```

Each issue page has inline CSS and inline SVG flags and logo.

**Fonts:** Anton for headings and big numbers, and PT Serif for accents (the intro line and the discussion prompt), both from Google Fonts. Body text and navigation use the Helvetica/Arial system fonts already installed on readers' devices, so nothing extra is downloaded for them.

## Publishing a new issue

1. Copy the last issue: `cp -r issues/01 issues/02`.
2. Edit `issues/02/index.html`. In the `<head>`, update these so the archive, feed and link previews are right:
   - `<title>`, `<meta name="description">`, `og:title`, `og:description`
   - `canonical` and `og:url` (`.../issues/02/`)
   - `article:published_time` (publication date, `YYYY-MM-DD`)
3. Run `python3 scripts/build.py`. This rebuilds `index.html`, `archive.html` and `feed.xml`.
4. Commit and push. If this repository is connected to the Vercel project `wealth-tax-watch`, each push to `main` redeploys the site.

Earlier issues stay at their own addresses (`/issues/01/`), so links shared with the cohort keep working.

## Checks

GitHub Actions (`.github/workflows/checks.yml`) runs on every push and pull request, and every Monday:

- **Generated files:** fails if you edited an issue but forgot to run `scripts/build.py`.
- **Links:** checks every source link in the issues. The weekly run catches pages that move or disappear after publication. Sites that block automated checkers (HTTP 403 or 429) are not counted as broken.

## Changing the site address

The address `https://wealth-tax-watch.vercel.app` appears in `scripts/build.py` (`SITE_URL`) and in each issue's `canonical`, `og:url`, `og:image` and RSS link tags. Update all of them if the site moves to a custom domain.

## Link-preview image

`assets/og-image.png` is rendered from `scripts/og-image.html`. After changing the template, regenerate it with `node scripts/og-image.mjs` after installing Playwright in the repo folder: `npm i --no-save playwright && npx playwright install chromium`.
