# Wealth Tax Watch

Biweekly global briefing on wealth tax proposals, public opinion and international tax cooperation, published for the Global Tax Fairness Fellowship cohort.

- **Latest issue:** No. 01, September 1-23, 2026
- **Live site:** https://wealth-tax-watch.vercel.app

## Layout

```
issues/01/issue.json    Issue 01 data: hero, tracker, polls, numbers, calendar, discussion, sources. Edit.
issues/01/stories.html  Issue 01 prose: the overview and every dispatch, as plain HTML. Edit.
issues/01/index.html    The issue page                      (generated)
index.html              Copy of the latest issue            (generated)
archive.html            List of every issue                 (generated)
feed.xml                RSS feed                            (generated)
templates/issue.html    The page design (CSS, flags, page script)
scripts/build.py        Builds all generated files
scripts/render_issue.py Renders one issue from issue.json + stories.html
assets/og-image.png     Link-preview image
```

You only edit `issue.json` and `stories.html`. Everything else about an issue page comes from `templates/issue.html`, so a design change there applies to every issue the next time you build.

**Fonts:** Anton for headings and big numbers, and PT Serif for accents, both from Google Fonts. Body text and navigation use the Helvetica/Arial system fonts already on readers' devices.

## What each part of `issue.json` controls

| Key | Section of the page |
|---|---|
| `page_title`, `title`, `description`, `published` | Browser tab, link previews, archive and RSS (`published` is `YYYY-MM-DD`) |
| `kicker`, `hero_lede`, `reading_time` | The dark hero |
| `countdowns` | The day counters under the hero (they count down from each reader's date) |
| `overview` | Heading for the intro; the text is the `overview` article in `stories.html` |
| `tracker.items` | The idea-to-law board. `stage` is one of `research`, `proposal`, `official`, `vote`, `law`; `j` is the flag; `story` is the dispatch it links to |
| `lead` | Optional lead-story block: `polls`, `trend` and `compare` are each optional |
| `numbers` | The numbers wall. `kind` says what sort of claim each number is |
| `calendar` | The to-scale calendar. `side` is `up` or `down` (alternate them); `range` draws a hatched band for an undated event |
| `discussion` | The design comparison: one `answers` entry per `levers` heading |
| `sources` | The source shelf |

Flags available: `us`, `fr`, `uk`, `ca`, `eu`, `un`. For a new country, add a `<symbol id="flag-xx">` to `templates/issue.html` and its name to `JURISDICTIONS` in `scripts/render_issue.py`.

Text in `issue.json` is plain text (no HTML). Prose with links, bold labels and paragraphs goes in `stories.html`.

## Publishing a new issue

1. Copy the last issue's sources: `mkdir issues/02 && cp issues/01/issue.json issues/01/stories.html issues/02/`.
2. Edit `issues/02/issue.json` and `issues/02/stories.html`. Set `number` to `"02"` and update `published`.
3. Run `python3 scripts/build.py`. It renders `issues/02/index.html` and rebuilds `index.html`, `archive.html` and `feed.xml`. It stops with a message if something is inconsistent (for example, a tracker item pointing to a dispatch that doesn't exist).
4. Commit and push. Each push to `main` redeploys the site on Vercel.

Earlier issues stay at their own addresses (`/issues/01/`), so links shared with the cohort keep working.

## Checks

GitHub Actions (`.github/workflows/checks.yml`) runs on every push and pull request, and every Monday:

- **Generated files:** fails if you edited an issue's `issue.json` or `stories.html` (or the template) but forgot to run `scripts/build.py`.
- **Links:** checks every source link in the issues. The weekly run catches pages that move or disappear after publication. Sites that block automated checkers (HTTP 403 or 429) are not counted as broken.

## Changing the site address

The address `https://wealth-tax-watch.vercel.app` appears in `scripts/build.py` (`SITE_URL`) and in each issue's `canonical`, `og:url`, `og:image` and RSS link tags. Update all of them if the site moves to a custom domain.

## Link-preview image

`assets/og-image.png` is rendered from `scripts/og-image.html`. After changing the template, regenerate it with `node scripts/og-image.mjs` after installing Playwright in the repo folder: `npm i --no-save playwright && npx playwright install chromium`.
