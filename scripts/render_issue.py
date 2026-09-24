"""Render one issue page from issues/NN/issue.json + issues/NN/stories.html.

Used by scripts/build.py. The template is templates/issue.html. Plain-text
fields in issue.json are HTML-escaped; stories.html is trusted HTML written by
the editor.
"""
import html
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "issue.html"

STAGES = [
    ("research", "Research & talks"),
    ("proposal", "Proposal"),
    ("official", "Official recommendation"),
    ("vote", "On a ballot or in a bill"),
    ("law", "Enacted"),
]
JURISDICTIONS = {
    "us": "United States", "fr": "France", "uk": "United Kingdom",
    "ca": "Canada", "eu": "Europe & OECD", "un": "Multilateral",
}

e = html.escape


def flag(j, cls=""):
    if j not in JURISDICTIONS:
        raise SystemExit("unknown flag %r (add a <symbol id=\"flag-%s\"> to templates/issue.html)" % (j, j))
    c = ' class="%s"' % cls if cls else ""
    return '<svg%s aria-hidden="true"><use href="#flag-%s"/></svg>' % (c, j)


def parse_stories(path):
    text = path.read_text(encoding="utf-8")
    stories = []
    for m in re.finditer(r"<article\s([^>]*)>(.*?)</article>", text, re.S):
        attrs = dict((k, html.unescape(v)) for k, v in re.findall(r'data-([\w-]+)="([^"]*)"', m.group(1)))
        if "id" not in attrs:
            raise SystemExit("%s: every <article> needs data-id" % path)
        attrs["body"] = m.group(2).strip()
        stories.append(attrs)
    return stories


def long_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%B %-d, %Y")


def sec_head(eyebrow, title, intro, title_id, intro_class=""):
    cls = ' class="%s"' % intro_class if intro_class else ""
    return ('<div class="sec-head reveal"><div><p class="eyebrow">%s</p><h2 id="%s">%s</h2></div><p%s>%s</p></div>'
            % (e(eyebrow), title_id, e(title), cls, e(intro)))


def render_tracker(t):
    items = t["items"]
    total = len(items)
    out = ['<section class="block" id="tracker" aria-labelledby="tracker-title"><div class="wrap">',
           sec_head(t["eyebrow"], t["title"], t["intro"], "tracker-title")]
    used = [j for j in JURISDICTIONS if any(i["j"] == j for i in items)]
    out.append('<div class="filters" role="group" aria-label="Filter by jurisdiction" id="filters">'
               '<button class="chip-f" type="button" data-j="all" aria-pressed="true">All</button>'
               + "".join('<button class="chip-f" type="button" data-j="%s" aria-pressed="false">%s%s</button>'
                         % (j, flag(j), e(JURISDICTIONS[j])) for j in used) + "</div>")
    out.append('<div class="pipe reveal" id="pipe">')
    for n, (sid, name) in enumerate(STAGES, 1):
        its = [(k, i) for k, i in enumerate(items) if i["stage"] == sid]
        if sid == "law" and not its:
            out.append('<div class="stage enacted"><span class="step">Stage %d</span><h3>%s</h3><p>%s</p>'
                       '<div class="zero">0</div></div>' % (n, name, e(t["enacted_note"])))
            continue
        out.append('<div class="stage"><span class="step">Stage %d · %d of %d</span><h3>%s</h3>'
                   '<div class="meter" aria-hidden="true"><i style="width:%.1f%%"></i></div>'
                   % (n, len(its), total, e(name), len(its) / total * 100))
        for k, i in its:
            out.append('<button class="item" type="button" data-k="%d" data-j="%s" aria-expanded="false" aria-controls="detail">%s'
                       '<span><b>%s</b><small>%s</small></span></button>'
                       % (k, i["j"], flag(i["j"]), e(i["title"]), e(i["meta"])))
        out.append("</div>")
    out.append('</div><div class="pipe-arrow" aria-hidden="true">Closer to law</div>'
               '<div class="detail" id="detail" hidden aria-live="polite"></div></div></section>')
    return "\n".join(out)


def render_lead(lead):
    p = lead["polls"]
    out = ['<section class="block" id="lead" aria-labelledby="lead-title"><div class="wrap">',
           sec_head(lead["eyebrow"], lead["title"], lead["lede"], "lead-title", "lede"),
           '<div class="ca reveal"><div class="ca-grid"><div>',
           '<h3 class="chart-title">%s</h3><p class="chart-sub">%s</p>' % (e(p["title"]), e(p["sub"])),
           '<div class="legend" aria-hidden="true"><span style="--c:var(--yes)">Yes</span><span style="--c:var(--und)">Undecided</span><span style="--c:var(--no)">No</span></div>',
           '<div id="tugs"></div>',
           '<details class="table-toggle"><summary>Show as a table</summary><table><thead><tr><th>Survey</th><th>Population</th><th>Dates</th><th>Yes</th><th>No</th><th>Undecided</th></tr></thead><tbody>']
    for r in p["rows"]:
        out.append("<tr><td>%s</td><td>%s, %s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>"
                   % (e(r["name"]), e(r["population"]), e(r["sample"]), e(r["dates"]), r["yes"], r["no"], r["undecided"]))
    out.append("</tbody></table></details>")
    if p.get("note"):
        out.append('<p class="chart-sub" style="margin-top:14px">%s</p>' % e(p["note"]))
    out.append("</div>")
    tr = lead.get("trend")
    if tr:
        desc = "; ".join("%s went from %d to %d percent" % (s["label"], s["from"], s["to"]) for s in tr["series"])
        out.append('<div class="slope"><h3 class="chart-title">%s</h3><p class="chart-sub">%s</p>'
                   '<svg viewBox="0 0 360 250" role="img" aria-label="%s: %s."><g id="slopeLines"></g></svg>'
                   '<p class="chart-sub" style="margin-top:8px">%s</p></div>'
                   % (e(tr["title"]), e(tr["sub"]), e(tr["sub"]), e(desc), e(tr["caption"])))
    out.append("</div>")
    c = lead.get("compare")
    if c:
        aria = ", ".join("%s at %d percent" % (r["label"], r["value"]) for r in c["rows"])
        out.append('<div class="catch"><div><p class="eyebrow" style="margin-bottom:8px">%s</p><h4>%s</h4></div>'
                   '<div><div class="props" id="props" role="img" aria-label="%s: %s."></div><p>%s</p></div></div>'
                   % (e(c["eyebrow"]), e(c["title"]), e(c["survey"]), e(aria), e(c["text"])))
    if lead.get("links"):
        out.append('<p class="lead-links">' + " · ".join(
            '<a class="src" href="%s" target="_blank" rel="noopener">%s ↗</a>' % (e(l["url"]), e(l["label"])) for l in lead["links"]) + "</p>")
    out.append("</div></div></section>")
    return "\n".join(out)


def fmt_number(n):
    dec = n.get("decimals", 0)
    return "%s%s%s" % (n.get("prefix", ""), ("%." + str(dec) + "f") % n["value"], n.get("suffix", ""))


def render_numbers(nb):
    out = ['<section class="block" id="numbers" aria-labelledby="num-title"><div class="wrap">',
           sec_head(nb["eyebrow"], nb["title"], nb["intro"], "num-title"), '<div class="wall reveal">']
    for n in nb["items"]:
        out.append('<div class="stat"><div class="v" data-count="%s" data-prefix="%s" data-suffix="%s" data-dec="%d">%s</div>'
                   '<span class="k">%s</span><p>%s</p></div>'
                   % (n["value"], e(n.get("prefix", "")), e(n.get("suffix", "")), n.get("decimals", 0),
                      e(fmt_number(n)), e(n["kind"]), e(n["text"])))
    out.append('</div><p class="wall-note">%s</p></div></section>' % e(nb["note"]))
    return "\n".join(out)


def render_calendar(cal):
    items = "".join("<li>%s: %s</li>" % (e(ev["label"]), e(ev["text"])) for ev in cal["events"])
    if cal.get("later"):
        items += "<li>%s: %s</li>" % (e(cal["later"]["label"]), e(cal["later"]["text"]))
    return "\n".join([
        '<section class="block" id="calendar" aria-labelledby="cal-title"><div class="wrap">',
        sec_head(cal["eyebrow"], cal["title"], cal["intro"], "cal-title"),
        '<p class="tl-hint">Scroll sideways to see the whole calendar.</p>',
        '<div class="tl-wrap reveal" tabindex="0" aria-label="Calendar, scrollable"><div class="tl" id="tl" aria-hidden="true"><div class="axis"></div></div></div>',
        '<ol class="sr">%s</ol></div></section>' % items])


def render_dispatches(meta, stories):
    out = ['<section class="block" id="dispatches" aria-labelledby="disp-title"><div class="wrap">',
           sec_head(meta["eyebrow"], meta["title"], meta["intro"], "disp-title"), '<div class="dispatches">']
    for s in stories:
        sub = "<small>%s</small>" % e(s["sub"]) if s.get("sub") else ""
        out.append('<article class="disp reveal" id="d-%s"><div class="who">%s<div class="where">%s%s</div>'
                   '<span class="kind">%s</span></div><div class="body">\n%s\n</div></article>'
                   % (s["id"], flag(s["flag"]), e(s["where"]), sub, e(s["kind"]), s["body"]))
    out.append("</div></div></section>")
    return "\n".join(out)


def render_discussion(d):
    first = d["designs"][0]["answers"]
    btns = "".join('<button class="design" type="button" aria-pressed="%s" data-i="%d">%s<b>%s</b><span>%s</span></button>'
                   % ("true" if i == 0 else "false", i, flag(x["j"]), e(x["title"]), e(x["source"]))
                   for i, x in enumerate(d["designs"]))
    levers = "".join('<div class="lever"><h5>%s</h5><p data-lever="%d">%s</p></div>' % (e(l), i, e(first[i]))
                     for i, l in enumerate(d["levers"]))
    return ('<section class="block" id="discussion" aria-labelledby="dq-title"><div class="wrap"><div class="discuss reveal">'
            '<p class="eyebrow">%s</p><h2 id="dq-title">%s</h2><div class="designs" role="group" aria-label="Choose a design" id="designs">%s</div>'
            '<div class="levers" aria-live="polite">%s</div><p class="question">%s</p></div></div></section>'
            % (e(d["eyebrow"]), e(d["title"]), btns, levers, e(d["question"])))


def render_sources(s):
    links = "\n".join('<a href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s</span></a>'
                      % (e(x["url"]), e(x["title"]), e(x["meta"])) for x in s["items"])
    return ('<section class="block" id="sources" aria-labelledby="src-title"><div class="wrap">%s<div class="shelf">\n%s\n</div></div></section>'
            % (sec_head("Source shelf", "Primary reading", "Primary documents where available. Cutoff: %s." % s["cutoff"], "src-title"), links))


def render(issue_dir, site_url):
    d = json.loads((issue_dir / "issue.json").read_text(encoding="utf-8"))
    stories = parse_stories(issue_dir / "stories.html")
    overview = next((s for s in stories if s["id"] == "overview"), None)
    dispatches = [s for s in stories if s["id"] != "overview"]
    ids = {s["id"] for s in dispatches}
    for i in d["tracker"]["items"]:
        if i["story"] not in ids:
            raise SystemExit("tracker item %r points to unknown story %r" % (i["title"], i["story"]))
        if i["stage"] not in dict(STAGES):
            raise SystemExit("tracker item %r has unknown stage %r" % (i["title"], i["stage"]))

    slug = issue_dir.name
    url = "%s/issues/%s/" % (site_url, slug)
    lead = d.get("lead")

    head = "\n".join([
        '<title>%s</title>' % e(d["page_title"]),
        '<meta name="description" content="%s">' % e(d["description"]),
        '<link rel="canonical" href="%s">' % url,
        '<link rel="alternate" type="application/rss+xml" title="Wealth Tax Watch" href="%s/feed.xml">' % site_url,
        '<meta property="og:type" content="article">',
        '<meta property="og:site_name" content="Wealth Tax Watch">',
        '<meta property="og:title" content="%s">' % e(d["title"]),
        '<meta property="og:description" content="%s">' % e(d["description"]),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s/assets/og-image.png">' % site_url,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="Wealth Tax Watch seal and wordmark">',
        '<meta property="article:published_time" content="%s">' % d["published"],
        '<meta name="twitter:card" content="summary_large_image">',
    ])
    nav = ['<a href="#tracker" class="keep">Tracker</a>']
    if lead:
        nav.append('<a href="#lead">%s</a>' % e(lead["nav"]))
    nav += ['<a href="#numbers">Numbers</a>', '<a href="#calendar">Calendar</a>',
            '<a href="#dispatches">Dispatches</a>', '<a href="#sources">Sources</a>']
    countdowns = "".join('<div class="cd" data-date="%s"><div class="n" aria-hidden="true">–</div><div><div class="l">%s</div><div class="d">%s</div></div></div>'
                         % (c["date"], e(c["label"]), e(c["when"])) for c in d["countdowns"])
    overview_html = ""
    if overview:
        overview_html = ('<section class="block" id="overview" aria-labelledby="ov-title"><div class="wrap"><div class="ov reveal">'
                         '<div><p class="eyebrow">%s</p><h2 id="ov-title">%s</h2></div><div class="ov-body">%s</div></div></div></section>'
                         % (e(d["overview"]["eyebrow"]), e(d["overview"]["title"]), overview["body"]))

    # Data the page script needs for charts and interactions (plain text only).
    data = {
        "items": [{k: i[k] for k in ("j", "title", "kind", "summary", "story")} for i in d["tracker"]["items"]],
        "jurisdictions": JURISDICTIONS,
        "polls": lead["polls"]["rows"] if lead else [],
        "trend": lead.get("trend") if lead else None,
        "compare": lead.get("compare", {}).get("rows") if lead else None,
        "calendar": d["calendar"],
        "designs": [x["answers"] for x in d["discussion"]["designs"]],
    }
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    parts = {
        "HEAD": head,
        "NAV": "\n      ".join(nav),
        "KICKER": e(d["kicker"]),
        "HERO_LEDE": e(d["hero_lede"]),
        "META_LINE": "Global Tax Fairness Fellowship · Published %s · %s" % (e(long_date(d["published"])), e(d["reading_time"])),
        "PUBLISHED": d["published"],
        "COUNTDOWNS": countdowns,
        "OVERVIEW": overview_html,
        "TRACKER": render_tracker(d["tracker"]),
        "LEAD": render_lead(lead) if lead else "",
        "NUMBERS": render_numbers(d["numbers"]),
        "CALENDAR": render_calendar(d["calendar"]),
        "DISPATCHES": render_dispatches(d["dispatches"], dispatches),
        "DISCUSSION": render_discussion(d["discussion"]),
        "SOURCES": render_sources(d["sources"]),
        "FOOTER": "<b>Global Tax Fairness Fellowship</b> · Wealth Tax Watch · Issue %s, %s" % (e(d["number"]), e(datetime.strptime(d["published"], "%Y-%m-%d").strftime("%B %Y"))),
        "DATA": data_json,
    }
    page = TEMPLATE.read_text(encoding="utf-8")
    for k, v in parts.items():
        page = page.replace("{{%s}}" % k, v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", page)
    if left:
        raise SystemExit("unfilled template slots: %s" % ", ".join(left))
    return page
