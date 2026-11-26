#!/usr/bin/env python3
"""Writes the bucksley-site pages (index, download, mcp, help, privacy, 404) and llms.txt on the house
app-site template, with one shared head, header and footer. tools/family.html is the template's
home-page tail (Discord and newsletter callouts, </main>, the More from Protomota block), kept
unchanged apart from the app name.

Two states. Until the first signed Mac build ships, every page says "Coming soon" and the JSON-LD
offer is PreOrder. tools/set-release.sh VERSION BUILD SHA256 BYTES runs this script with
--release, which switches the site to the real download (InStock offer, downloadUrl, install guide).
After that, the current release is read back from the download page, so a plain rerun keeps it.

Not deployed (tools/ is left out of the Pages build). Run from anywhere: python3 tools/build-site.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://bucksley.ai"
GA = "G-NZ4KDPXME2"
GSC = "7iIXr-PMFJ_aGS43oSrPEZ5DRntgBF09yLD61lN2gac"  # google-site-verification token for the home page, once Search Console has one
BING = "E2001B47E91F72A19BB1E8E642B26928"  # account-wide msvalidate.01 token
V = "20261125"  # cache-buster for the icon, favicon and social card
FAMILY = open(os.path.join(ROOT, "tools", "family.html")).read()


def current_release():
    """--release VERSION BUILD SHA SIZE from set-release.sh, else what the download page already shows, else None."""
    if "--release" in sys.argv:
        version, build, sha, size = sys.argv[sys.argv.index("--release") + 1:][:4]
        return {"version": version, "build": build, "sha": sha, "size": size}
    try:
        page = open(os.path.join(ROOT, "download", "index.html")).read()
    except FileNotFoundError:
        return None
    rel = {}
    for key in ("version", "build", "size", "sha"):
        m = re.search(rf'data-release="{key}">([^<]*)<', page)
        if m:
            rel[key] = m.group(1)
    return rel if len(rel) == 4 else None


REL = current_release()
LIVE = REL is not None
DMG = f"/downloads/Bucksley-{REL['version']}.dmg" if LIVE else None


def rel(key):
    tag = "code" if key == "sha" else "span"
    return f'<{tag} data-release="{key}">{REL[key]}</{tag}>'


STATUS = "Free and open source." if LIVE else "Coming soon, free and open source."
DESC = ("Bucksley is a free, local-first personal finance app for Mac and iPhone. It brings your bank accounts, cards "
        "and investments into one place to track spending, budgets, recurring bills and net worth. It is read-only, "
        "never moves money, and keeps your data on your devices and in your own iCloud, with no Bucksley server. " + STATUS)
TITLE = "Bucksley · Every account in one place, on your Mac and iPhone"

ORG = {"@type": "Organization", "@id": "https://protomota.com/#protomota", "name": "Protomota", "legalName": "Protomota, LLC",
       "url": "https://protomota.com/", "logo": "https://protomota.com/redesign/logo.png", "founder": {"@id": "https://protomota.com/#brad"},
       "sameAs": ["https://github.com/protomota", "https://x.com/protomotalab", "https://youtube.com/@protomota", "https://newsletter.protomota.com"]}
PERSON = {"@type": "Person", "@id": "https://protomota.com/#brad", "name": "Brad Dunlap", "url": "https://protomota.com/about",
          "sameAs": ["https://www.linkedin.com/in/brad--dunlap/", "https://github.com/protomota"]}
APP = {"@type": "SoftwareApplication", "@id": f"{SITE}/#app", "name": "Bucksley", "url": f"{SITE}/", "description": DESC,
       "applicationCategory": "FinanceApplication", "applicationSubCategory": "Personal finance and budgeting",
       "operatingSystem": "macOS 15 or later, iOS 18 or later", "isAccessibleForFree": True,
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                  "availability": "https://schema.org/InStock" if LIVE else "https://schema.org/PreOrder"},
       "image": f"{SITE}/assets/icon.png?v={V}",
       "featureList": ["Net worth, accounts and transactions in one place", "Bank connections through SimpleFIN Bridge or your own Plaid keys",
                       "Apple Card, Apple Cash and Savings on iPhone through FinanceKit", "CSV import from other finance apps",
                       "Categories, groups and rules", "Budgets with rollover and pace", "Recurring bills and subscriptions",
                       "Ask Bucksley, with Apple's on-device model by default", "iPhone review inbox synced through your private iCloud",
                       "Read-only: never moves money", "Built-in MCP server with 18 tools for Claude Code, Codex and Claude chat"],
       "author": {"@id": "https://protomota.com/#brad"}, "publisher": {"@id": "https://protomota.com/#protomota"},
       "sameAs": ["https://protomota.com/apps"]}
if LIVE:
    APP.update({"softwareVersion": REL["version"], "downloadUrl": SITE + DMG, "installUrl": f"{SITE}/download/"})

APPLE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/></svg>'
ICON_ARROW = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'
ICON_CHART = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/></svg>'
ICON_BELL = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>'
ICON_PLUG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22v-5"/><path d="M15 8V2"/><path d="M17 8a1 1 0 0 1 1 1v4a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1z"/><path d="M9 8V2"/></svg>'
ICON_BOOK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/></svg>'
ICON_CHAT = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"/></svg>'
ICON_HOME = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>'
ICON_HELP = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>'
ICON_ACTION = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19.414 14.414C21 12.828 22 11.5 22 9.5a5.5 5.5 0 0 0-9.591-3.676.6.6 0 0 1-.818.001A5.5 5.5 0 0 0 2 9.5c0 2.3 1.5 4 3 5.5l5.535 5.362a2 2 0 0 0 2.879.052 2.12 2.12 0 0 0-.004-3 2.124 2.124 0 1 0 3-3 2.124 2.124 0 0 0 3.004 0 2 2 0 0 0 0-2.828l-1.881-1.882a2.41 2.41 0 0 0-3.409 0l-1.71 1.71a2 2 0 0 1-2.828 0 2 2 0 0 1 0-2.828l2.823-2.762"/></svg>'
NEWSLETTER = "https://newsletter.protomota.com/"

NAV = [("/#features", "Features", "nav-hide"), ("/#connect", "Connect", "nav-hide"), ("/#iphone", "iPhone", "nav-hide"), ("/mcp/", "MCP setup", "nav-hide-sm")]
FOOT_NAV = [("/download/", "Download" if LIVE else "Coming soon"), ("/mcp/", "MCP setup"), ("/help/", "Support"), ("/privacy/", "Privacy"),
            ("https://newsletter.protomota.com/", "Newsletter"), ("https://x.com/ProtomotaLab", "Follow on X"),
            ("https://projectatom.ai/", "Project ATOM"), ("https://protomota.com/apps?app=bucksley#feedback", "Send Feedback")]


def ld(graph):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")) + "</script>"


def head(path, title, desc, graph, noindex=False, home=False):
    url = SITE + path
    meta = []
    if noindex:
        meta.append('  <meta name="robots" content="noindex">')
    else:
        meta.append(f'  <meta name="description" content="{desc}">')
    meta += ['  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">',
             '  <meta name="theme-color" content="#0d0e17" media="(prefers-color-scheme: dark)">']
    if not noindex:
        meta += [
            f'  <link rel="canonical" href="{url}">',
            '  <meta property="og:type" content="website">', '  <meta property="og:site_name" content="Bucksley">',
            '  <meta property="og:locale" content="en_US">',
            f'  <meta property="og:title" content="{title}">', f'  <meta property="og:description" content="{desc}">',
            f'  <meta property="og:url" content="{url}">', f'  <meta property="og:image" content="{SITE}/social-card.png?v={V}">',
            '  <meta property="og:image:type" content="image/png">',
            '  <meta property="og:image:width" content="1200">', '  <meta property="og:image:height" content="630">',
            '  <meta property="og:image:alt" content="Bucksley. Every account, one honest picture. Personal finance for Mac and iPhone. Free and open source.">',
            '  <meta name="twitter:card" content="summary_large_image">', '  <meta name="twitter:site" content="@ProtomotaLab">',
            f'  <meta name="twitter:title" content="{title}">', f'  <meta name="twitter:description" content="{desc}">',
            f'  <meta name="twitter:image" content="{SITE}/social-card.png?v={V}">',
            '  <meta name="author" content="Brad Dunlap">']
    if home:
        if GSC:
            meta.append(f'  <meta name="google-site-verification" content="{GSC}">')
        meta.append(f'  <meta name="msvalidate.01" content="{BING}">')
    meta += [f'  <link rel="icon" href="/favicon.png?v={V}" type="image/png">', f'  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png?v={V}">',
             '  <link rel="stylesheet" href="/assets/site.css">',
             '  <link rel="stylesheet" href="/protomota-family.css">' if home else None,
             '  <link rel="stylesheet" href="/project-atom/project-atom-promo.css?v=20261126b">' if home else None,
             f'  <script src="/assets/analytics.js" data-ga="{GA}" data-site="bucksley" data-host="bucksley.ai" data-privacy="/privacy/" data-footer=".footer nav" data-css="/assets/analytics.css" defer></script>',
             '  <script src="/assets/site.js" defer></script>' if home else None,
             '  <script src="/assets/protomota-share.js" defer></script>' if home else None,
             f'  <title>{title}</title>', ('  ' + ld(graph)) if graph else None]
    return '<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n' + "\n".join(m for m in meta if m) + "\n</head>\n"


def header(current=None, body_class=None):
    current_attr = ' aria-current="page"'
    links = "\n".join(f'        <a class="{c}" href="{h}"{current_attr if h == current else ""}>{t}</a>' for h, t, c in NAV)
    if LIVE and current == "/download/":
        cta = f'<a class="nav-cta" href="#install">{ICON_BOOK}Install guide</a>'
        links = ""
    elif LIVE:
        cta = f'<a class="nav-cta mac-download" href="/download/">{APPLE} Download for Mac</a>'
    else:
        cta = f'<a class="nav-cta" href="/download/"{current_attr if current == "/download/" else ""}>Coming soon</a>'
    body = f'<body class="{body_class}">' if body_class else "<body>"
    return f'''{body}
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="shell nav">
      <a class="wordmark" href="/" aria-label="Bucksley home"><img src="/assets/icon.png?v={V}" alt="" width="30" height="30">Bucksley</a>
      <nav aria-label="Main">
{links + chr(10) if links else ""}        {cta}
      </nav>
    </div>
  </header>
'''


def footer(family=False):
    nav = "".join(f'<a href="{h}">{t}</a>' for h, t in FOOT_NAV)
    return (FAMILY if family else "") + f'''  <footer>
    <div class="shell footer">
      <a class="product-credit" href="https://protomota.com/" target="_blank" rel="noopener noreferrer"><img src="/assets/protomota-logo.png" width="22" height="22" alt=""><span>A Protomota Product</span></a>
      <nav aria-label="Footer">{nav}</nav>
    </div>
    <div class="shell footer-credit">
      <span>&copy; <span data-pm-year>2026</span> Protomota · <a href="https://protomota.com/about#hosting" style="color:inherit">Hosted on Cloudflare</a></span>
    </div>
  </footer>
  <script src="/assets/pm-year.js" defer></script>
</body>
</html>
'''


def crumbs(name, path):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Bucksley", "item": SITE + "/"},
                                                           {"@type": "ListItem", "position": 2, "name": name, "item": SITE + path}]}


def webpage(path, name, desc):
    return {"@type": "WebPage", "@id": f"{SITE}{path}#webpage", "url": SITE + path, "name": name, "description": desc,
            "isPartOf": {"@id": f"{SITE}/#website"}, "inLanguage": "en-US", "publisher": {"@id": "https://protomota.com/#protomota"},
            "about": {"@id": f"{SITE}/#app"}}


def write(rel_path, text):
    p = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(p) or ROOT, exist_ok=True)
    open(p, "w").write(text)


# Made-up sample accounts for the preview. Never real numbers. [id, name, balance text, class, spark class]
ACCOUNTS = [("checking", "Everyday Checking", "$4,812", "", "c3"), ("savings", "High-Yield Savings", "$28,450", "", "c3"),
            ("card", "Rewards Card", "−$1,236", "neg", "c5"), ("brokerage", "Brokerage", "$142,381", "", "c1"),
            ("crypto", "Crypto", "$9,640", "", "c2")]


def window():
    side = "\n".join(f'''                <button type="button" class="acct" data-acct="{i}" aria-pressed="false"><span class="acct-text"><span>{n}</span><b class="fig {c}">{b}</b></span><span class="spark {k}" aria-hidden="true"></span></button>''' for i, n, b, c, k in ACCOUNTS)
    return f'''        <div class="stage">
          <div class="gw" data-theme="ah" data-appearance="dark" role="group" aria-label="Working preview of the Bucksley window, with sample data">
            <div class="gw-title">
              <span class="lights" aria-hidden="true"><i></i><i></i><i></i></span>
              <span class="tabs" role="group" aria-label="View">
                <button type="button" data-view="home" aria-pressed="true">Home</button>
                <button type="button" data-view="spending" aria-pressed="false">Spending</button>
                <button type="button" data-view="budgets" aria-pressed="false">Budgets</button>
              </span>
              <span class="grow"></span>
              <span class="sync"><i></i><span>Synced to iCloud</span></span>
            </div>
            <div class="gw-body">
              <div class="gw-side">
                <span class="side-label">Accounts</span>
                <button type="button" class="acct all" data-acct="all" aria-pressed="true"><span class="acct-text"><span>All accounts</span><b class="fig" data-k="nw-side">$183,047</b></span></button>
{side}
              </div>
              <div class="gw-main">
                <div class="view" data-pane="home">
                  <div class="nw-head">
                    <div><div class="lbl" data-k="nw-label">Net worth</div><div class="big fig" data-k="nw">–</div><span class="chip fig" data-k="nw-chip"></span></div>
                    <span class="seg" role="group" aria-label="Range">
                      <button type="button" data-range="30" aria-pressed="false">1M</button>
                      <button type="button" data-range="90" aria-pressed="false">3M</button>
                      <button type="button" data-range="365" aria-pressed="true">1Y</button>
                      <button type="button" data-range="730" aria-pressed="false">All</button>
                    </span>
                  </div>
                  <div class="keys" data-k="keys"></div>
                  <div class="nw-chart"><svg viewBox="0 0 640 200" role="img" aria-label="Stacked area chart of net worth by investments, cash and crypto"></svg><span class="readout fig" aria-live="polite"></span></div>
                  <div class="sech"><b>Recent activity</b><span data-k="tx-scope">All accounts</span></div>
                  <ul class="txs" data-k="txs"></ul>
                </div>
                <div class="view" data-pane="spending" hidden>
                  <div class="sech top"><b>Spending · November</b><span>Excludes transfers</span></div>
                  <div class="donutrow">
                    <div class="donut"><svg viewBox="0 0 42 42" aria-hidden="true"></svg><div><b class="fig" data-k="spend-total">–</b><span data-k="spend-label">This month</span></div></div>
                    <ul class="legend" data-k="legend"></ul>
                  </div>
                </div>
                <div class="view" data-pane="budgets" hidden>
                  <div class="sech top"><b>Budgets · November</b><span data-k="pace">Day 24 of 30</span></div>
                  <ul class="rings" data-k="rings"></ul>
                </div>
                <form class="ask" data-k="ask">
                  <label class="visually-hidden" for="ask-q">Ask Bucksley</label>
                  <select id="ask-q" data-k="ask-q">
                    <option value="dining">How much did I spend on dining this month?</option>
                    <option value="subs">Which subscriptions went up?</option>
                    <option value="budget">Am I on pace with my budgets?</option>
                  </select>
                  <button type="submit" class="ask-go">Ask</button>
                </form>
                <p class="answer" data-k="answer" aria-live="polite" hidden></p>
              </div>
            </div>
          </div>
          <div class="stage-note">
            <span>A working preview with sample data. Switch views, pick an account or a range, hover the chart, or ask a question.</span>
            <span class="chooser"><span id="theme-label">Theme</span>
              <span class="opts" role="group" aria-labelledby="theme-label">
                <button type="button" data-theme-to="ah" aria-pressed="true">Afterhours</button>
                <button type="button" data-theme-to="ev" aria-pressed="false">Evergreen</button>
                <button type="button" data-theme-to="al" aria-pressed="false">Almanac</button>
              </span>
            </span>
            <span class="chooser"><span id="look-label">Appearance</span>
              <span class="opts" role="group" aria-labelledby="look-label">
                <button type="button" data-look="light" aria-pressed="false">Light</button>
                <button type="button" data-look="dark" aria-pressed="true">Dark</button>
              </span>
            </span>
          </div>
        </div>
'''


def phone():
    return '''        <figure class="phone">
          <div class="phone-frame">
            <div class="phone-screen" data-theme="ah" data-appearance="light" data-review>
              <div class="ph-head"><h4>Review</h4><span class="count fig" data-k="count">1 of 5</span></div>
              <div class="deck">
                <div class="dcard">
                  <div class="dtop"><i class="av c3" data-k="av">HB</i><span class="tag c3" data-k="cat">Home</span></div>
                  <div class="dm" data-k="merchant">Hardware Barn</div>
                  <div class="da fig" data-k="amount">−$146.83</div>
                  <div class="dmeta"><span data-k="date">Sun, Nov 22</span><span data-k="acct">Everyday Checking</span></div>
                  <div class="dnote" data-k="note">About $60 more than your usual Hardware Barn visit.</div>
                </div>
              </div>
              <div class="dbtn">
                <button type="button" class="pbtn ghost" data-act="category">Change category</button>
                <button type="button" class="pbtn pri" data-act="reviewed">Reviewed</button>
              </div>
              <p class="hint" data-k="hint">Swipe right to mark reviewed.</p>
              <h5 class="up">Up next</h5>
              <ul class="next" data-k="next"></ul>
            </div>
          </div>
          <figcaption>iPhone app coming soon · sample data</figcaption>
        </figure>
'''


TOOLS = [("get_status", "Which connections are set up, how many accounts and transactions there are, and when each last synced."),
         ("list_accounts · get_net_worth", "Accounts with balances, and net worth over time by what it is made of."),
         ("list_transactions", "Search and filter transactions by date, account, category, amount, tag or review state."),
         ("get_spending", "Spending by category or group for any period."),
         ("list_categories · list_rules", "Your categories, groups and the rules that file transactions."),
         ("list_budgets · list_recurring", "Budgets with spent, left and pace, and recurring bills and subscriptions."),
         ("get_review_queue", "Transactions waiting for review."),
         ("mark_reviewed · set_category · set_note · rename_transaction · set_tags", "Tidy up transactions. Off until you allow changes."),
         ("create_rule · set_budget", "Add a categorization rule or set a budget. Off until you allow changes."),
         ("sync_now", "Fetch new transactions from your connections now. Off until you allow changes.")]


def index():
    graph = [{"@type": "WebSite", "@id": f"{SITE}/#website", "url": SITE + "/", "name": "Bucksley", "description": DESC, "inLanguage": "en-US",
              "publisher": {"@id": "https://protomota.com/#protomota"}},
             {**webpage("/", TITLE, DESC), "mainEntity": {"@id": f"{SITE}/#app"}}, APP, ORG, PERSON]
    share = ('<button type="button" class="pm-share-btn bk-share" data-pm-share data-share-url="https://bucksley.ai/" data-share-title="Bucksley" '
             'data-share-text="Every account, one honest picture. Free personal finance for Mac and iPhone." aria-haspopup="menu" aria-label="Share Bucksley">'
             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M12 3v12"/><path d="m7.5 7.5 4.5-4.5 4.5 4.5"/><path d="M5 12v6.5A2.5 2.5 0 0 0 7.5 21h9a2.5 2.5 0 0 0 2.5-2.5V12"/></svg><span data-pm-share-label>Share</span></button>')
    if LIVE:
        pill = "Mac app · Free · Open source"
        primary = f'<a class="button mac-download" href="/download/">{APPLE} Download for Mac</a>'
        fine = f'Free · Open source · macOS 15 or later · Version {rel("version")} · iPhone app coming soon'
    else:
        pill = "Mac and iPhone · Free · Coming soon"
        primary = f'<a class="button" href="{NEWSLETTER}" target="_blank" rel="noopener noreferrer">{ICON_BELL}Get launch news</a>'
        fine = "Free · Open source · macOS 15 and iOS 18 or later · In development"
    h = head("/", TITLE, DESC, graph, home=True) + header()
    h += f'''
  <main id="main">
    <section class="hero" aria-labelledby="hero-title">
      <div class="shell">
        <p class="pill"><i></i>{pill}</p>
        <h1 id="hero-title">Every account. <em>One honest picture.</em></h1>
        <p class="lead">Bucksley brings your bank accounts, cards and investments together on your Mac and iPhone: spending, budgets, recurring bills and net worth in one place. It only reads, it never moves money, and your data stays on your devices and in your own iCloud. <strong>There is no Bucksley server.</strong></p>
        <div class="actions">
          {primary}
          <a class="button secondary" href="#features">{ICON_CHART}See what it does</a>
          {share}
        </div>
        <p class="fineprint">{fine}</p>

{window()}
        <dl class="facts">
          <div><dt>0</dt><dd>Bucksley servers. Your finances stay on your devices</dd></div>
          <div><dt>4</dt><dd>ways in: SimpleFIN, your own Plaid keys, Apple Wallet and CSV</dd></div>
          <div><dt>18</dt><dd>MCP tools for the agent you connect</dd></div>
          <div><dt>$0</dt><dd>free and open source</dd></div>
        </dl>
      </div>
    </section>

    <section id="features" class="section">
      <div class="shell">
        <div class="section-head">
          <span class="mark">features</span>
          <h2>Know where it went. <em>Decide where it goes.</em></h2>
          <p class="lead">Bucksley does the everyday work of a paid finance app without the subscription or the account: it pulls in your transactions, files them, and shows you how the month is going at a glance.</p>
        </div>
        <div class="bento">
          <article class="card wide">
            <h3>Transactions you can actually tidy</h3>
            <p>Search and filter everything. Rename a merchant, change a category, split a purchase, add a note or tags, and mark it reviewed. Fix one and Bucksley offers a rule so the next one files itself.</p>
            <div class="visual"><div class="mini" aria-hidden="true">
              <div class="mini-row"><span class="lbl">Rule</span><span class="val">Merchant contains <b>“bean there”</b> → <b>Dining</b></span><span class="end">12 matched</span></div>
              <div class="mini-row"><span class="lbl">Split</span><span class="val"><b>Big Box Store</b> $182.40 → Groceries $121.15 · Home $61.25</span><span class="end">2 parts</span></div>
            </div></div>
          </article>
          <article class="card wide">
            <h3>Budgets that keep pace with you</h3>
            <p>Set a budget per category or group. Leftovers can roll into next month, a pace marker shows whether you’re ahead of the calendar, and Bucksley can suggest budgets from what you really spend.</p>
            <div class="visual"><div class="mini" aria-hidden="true">
              <div class="mini-row"><span class="lbl">Groceries</span><span class="val"><b>$486</b> of $600 · on pace</span><span class="end">81%</span></div>
              <div class="mini-row"><span class="lbl">Dining</span><span class="val"><b>$312</b> of $300 · $12 over</span><span class="end">104%</span></div>
            </div></div>
          </article>
          <article class="card">
            <h3>Net worth, by what it’s made of</h3>
            <p>Cash, investments, crypto and debt stacked over time, with every account’s balance and trend in the sidebar.</p>
          </article>
          <article class="card">
            <h3>Recurring, spotted for you</h3>
            <p>Bills and subscriptions are found automatically, with what’s due next and which ones quietly went up.</p>
            <div class="visual"><ul class="chips"><li>Weekly</li><li>Monthly</li><li>Yearly</li></ul></div>
          </article>
          <article class="card">
            <h3>Ask Bucksley</h3>
            <p>Ask about your money in plain words. Answers come from Apple’s on-device model by default, or from your own Claude or OpenAI key if you add one.</p>
          </article>
        </div>
      </div>
    </section>

    <section id="connect" class="section band" aria-labelledby="connect-title">
      <div class="shell">
        <div class="section-head">
          <span class="mark">connect</span>
          <h2 id="connect-title">Bring your accounts. <em>Keep the keys.</em></h2>
          <p class="lead">Bucksley talks to your banks through services you sign up for yourself, so the connection belongs to you. Every connection is read-only, and its secret is kept in the Keychain on your device.</p>
        </div>
        <div class="connect">
          <article><h3>SimpleFIN Bridge</h3><p>Link thousands of US banks and cards through your own SimpleFIN Bridge account. Paste its setup token and Bucksley does the rest.</p></article>
          <article><h3>Plaid, with your keys</h3><p>Already have Plaid developer keys? Add them and connect institutions through Plaid’s own sign-in. Bucksley never sees your bank password.</p></article>
          <article><h3>Apple Wallet</h3><p>On iPhone, Bucksley reads Apple Card, Apple Cash and Savings through Apple’s FinanceKit, with your permission.</p></article>
          <article><h3>CSV import</h3><p>Moving from another finance app? Import its transaction export, categories and tags included, and keep your history.</p></article>
        </div>
      </div>
    </section>

    <section id="iphone" class="section">
      <div class="shell split">
        <div>
          <span class="mark">iphone · coming soon</span>
          <h2>Review it <em>in a spare minute.</em></h2>
          <p class="lead">The iPhone app turns new transactions into a short review inbox. Swipe through them while you wait for coffee, and everything you mark syncs back to your Mac through your private iCloud.</p>
          <ul class="ticks">
            <li><span><strong>Your iCloud, not ours.</strong> Your workspace syncs through your own private iCloud database. Bucksley has no server to send it to.</span></li>
            <li><span><strong>Widgets and Shortcuts.</strong> Net worth, budgets and what’s left to spend on your Home Screen, plus App Intents for Shortcuts and Siri.</span></li>
            <li><span><strong>Apple Wallet on board.</strong> Apple Card, Apple Cash and Savings come in straight from FinanceKit on your iPhone.</span></li>
          </ul>
        </div>
{phone()}      </div>
    </section>

    <section id="agents" class="section band">
      <div class="shell agent">
        <div>
          <span class="mark">agents</span>
          <h2>Let your agent <em>do the bookkeeping.</em></h2>
          <p class="lead">Bucksley has an MCP server built in. Connect Claude Code, Codex or Claude chat and it can answer questions about your money, clear the review queue and write rules. Agents can only look until you allow changes, and every change is logged in the app.</p>
          <div class="clients">
            <a href="/mcp/#claude-code">{ICON_PLUG}Claude Code <span aria-hidden="true">→</span></a>
            <a href="/mcp/#codex">{ICON_PLUG}Codex <span aria-hidden="true">→</span></a>
            <a href="/mcp/#claude-chat">{ICON_PLUG}Claude chat <span aria-hidden="true">→</span></a>
          </div>
          <div class="actions"><a class="button secondary" href="/mcp/">{ICON_BOOK}How agent setup works</a></div>
        </div>
        <div class="session" data-mode="write">
          <div class="session-bar">
            <span id="mode-label">Bucksley › Settings › Agents</span>
            <span class="chooser"><span class="opts" role="group" aria-labelledby="mode-label">
              <button type="button" data-mode-to="read" aria-pressed="false">View only</button>
              <button type="button" data-mode-to="write" aria-pressed="true">Can make changes</button>
            </span></span>
          </div>
          <div class="session-body">
            <p class="say you">File my coffee runs under Dining and make it stick. Then tell me how dining looks this month.</p>
            <ul class="calls">
              <li><div><b>list_transactions</b><span>“Bean There” · 4 unreviewed · filed as Shopping</span></div></li>
              <li class="only-read blocked"><div><b>set_category</b><span>Agents can view only. Turn on “Let agents make changes” in Settings → Agents.</span></div></li>
              <li class="only-write"><div><b>set_category</b><span>4 transactions → Dining</span></div></li>
              <li class="only-write"><div><b>create_rule</b><span>Merchant contains “bean there” → Dining</span></div></li>
              <li><div><b>get_spending</b><span>Dining · November · $312 of $300</span></div></li>
            </ul>
            <p class="say agent-says only-write">Done. Four coffee runs moved to Dining and a rule will file the next ones. Dining is at $312, $12 over its $300 budget.</p>
            <p class="say agent-says only-read">I found four coffee runs filed as Shopping. Bucksley is set to view only, so I haven’t changed them. Dining is at $312 of $300.</p>
          </div>
        </div>
      </div>
    </section>

    <section id="privacy" class="section" aria-labelledby="privacy-title">
      <div class="shell">
        <div class="section-head">
          <span class="mark">privacy</span>
          <h2 id="privacy-title">Your money stays <em>yours.</em></h2>
        </div>
        <div class="trio">
          <div><h3>Read-only, always</h3><p>Bucksley reads balances and transactions. It can’t move money, pay bills or make transfers, and it never asks for your bank password.</p></div>
          <div><h3>No Bucksley server</h3><p>Your data lives on your devices and in your own iCloud. There’s no account to make and nothing for us to store.</p></div>
          <div><h3>Agents on your terms</h3><p>The MCP server runs on your Mac. Agents can only look until you allow changes, and keys are never handed to them. <a href="/privacy/#mcp">How agent access works</a></p></div>
        </div>
      </div>
    </section>
'''
    if LIVE:
        steps = "\n".join(f'          <li><span><strong>{a}</strong> {b}</span></li>' for a, b in INSTALL_STEPS)
        h += f'''
    <section id="download" class="section band" aria-labelledby="download-title">
      <div class="shell split install">
        <div>
          <span class="mark">download</span>
          <h2 id="download-title">Bucksley for <em>Mac.</em></h2>
          <p class="lead">Free for Macs running macOS 15 or later. Signed by Protomota, notarized by Apple, and kept up to date automatically. The iPhone app is coming soon.</p>
          <div class="actions">
            <a class="button mac-download" href="/download/">{APPLE} Download and install</a>
            <a class="button secondary" href="/mcp/">{ICON_PLUG}MCP setup</a>
          </div>
        </div>
        <ol class="install-steps" aria-label="Getting started">
{steps}
        </ol>
      </div>
    </section>
'''
    else:
        h += f'''
    <section class="section closing" aria-labelledby="closing-title">
      <div class="shell">
        <span class="mark">coming soon</span>
        <h2 id="closing-title">Free and <em>open source.</em></h2>
        <p class="lead">Bucksley is in development for Mac and iPhone. Join the Protomota newsletter or our Discord to hear the day it ships.</p>
        <div class="actions actions-left">
          <a class="button" href="{NEWSLETTER}" target="_blank" rel="noopener noreferrer">{ICON_BELL}Get launch news</a>
          <a class="button secondary" href="/download/">What’s coming {ICON_ARROW}</a>
        </div>
      </div>
    </section>
'''
    # Discord and newsletter callouts, </main> and the More from Protomota block come from the template.
    h += footer(family=True)
    write("index.html", h)


INSTALL_STEPS = [("Open the disk image", "and drag Bucksley into Applications."),
                 ("Connect your accounts", "with SimpleFIN Bridge or your own Plaid keys, or import a CSV."),
                 ("Review and budget.", "Bucksley files your transactions; you set budgets and check the month at a glance.")]

FIRST_RELEASE = [("Mac app", "Home, accounts, transactions, categories and rules, budgets, recurring and net worth", "now", "In development"),
                 ("iPhone app", "Review inbox, budgets and balances, synced through your private iCloud", "now", "In development"),
                 ("Connections", "SimpleFIN Bridge, your own Plaid keys, Apple Card, Cash and Savings (iPhone), CSV import", "now", "In development"),
                 ("Ask Bucksley", "Questions about your money, on Apple’s on-device model or your own Claude or OpenAI key", "now", "In development"),
                 ("Widgets and Shortcuts", "Home Screen widgets and App Intents for Shortcuts and Siri", "now", "In development"),
                 ("MCP server", "18 tools for Claude Code, Codex and Claude chat, view only until you allow changes", "now", "In development")]

WHATS_NEW = [("Home", "Net worth stacked by cash, investments and crypto, every account’s balance and trend, and recent activity."),
             ("Transactions", "Search, filter, rename, recategorize, split, notes, tags and mark reviewed."),
             ("Categories and rules", "Groups of categories, and rules that file new transactions for you."),
             ("Budgets", "Per category or group, with rollover, a pace marker and suggested amounts."),
             ("Recurring", "Bills and subscriptions found automatically, with what’s due next."),
             ("Connections", "SimpleFIN Bridge, your own Plaid keys and CSV import. Read-only; secrets kept in the Keychain."),
             ("Ask Bucksley", "Plain-language questions, on Apple’s on-device model or your own Claude or OpenAI key."),
             ("MCP server", "18 tools for Claude Code, Codex and Claude chat, view only until you allow changes, with a log of every agent change."),
             ("Automatic updates", "Signed updates through Sparkle. Bucksley checks for new versions and installs them for you.")]


def download():
    if not LIVE:
        d = "Bucksley for Mac and iPhone is in development. See what the first release includes and how to hear when it ships."
        graph = [webpage("/download/", "Coming soon · Bucksley", d), crumbs("Coming soon", "/download/"), APP, ORG, PERSON]
        tr = "\n".join(f'              <tr><td>{a}</td><td>{b}</td><td><span class="status {c}">{s}</span></td></tr>' for a, b, c, s in FIRST_RELEASE)
        h = head("/download/", "Coming soon · Bucksley", d, graph) + header("/download/") + f'''  <main id="main">
    <div class="shell page-head">
      <span class="mark">coming soon</span>
      <h1>Bucksley is on its way.</h1>
      <p class="lead">{d}</p>
      <div class="actions actions-left">
        <a class="button" href="{NEWSLETTER}" target="_blank" rel="noopener noreferrer">{ICON_BELL}Get launch news</a>
        <a class="button secondary" href="https://lab.protomota.com" target="_blank" rel="noopener noreferrer">Join our Discord <span aria-hidden="true">↗</span></a>
      </div>
    </div>
    <div class="shell doc single">
      <div class="prose">
        <section>
          <h2>The first release</h2>
          <div class="table-wrap">
            <table class="tide-table">
              <thead><tr><th>Part</th><th>What it does</th><th>Status</th></tr></thead>
              <tbody>
{tr}
              </tbody>
            </table>
          </div>
        </section>
        <section>
          <h2>What you’ll need</h2>
          <ul>
            <li>A Mac running macOS 15 or later. The iPhone app needs iOS 18 or later and the same iCloud account.</li>
            <li>A way in for your accounts: a SimpleFIN Bridge account, your own Plaid developer keys, Apple Wallet on iPhone, or a CSV export.</li>
            <li>For Ask Bucksley on-device, a Mac or iPhone with Apple Intelligence. Otherwise, your own Claude or OpenAI key.</li>
          </ul>
          <p>Bucksley will be free, with no account and nothing to unlock. The source will be available on GitHub.</p>
        </section>
      </div>
    </div>
  </main>
''' + footer()
        write("download/index.html", h)
        return
    d = "Download Bucksley for Mac. Free, signed and notarized, with automatic updates. Install it, connect your accounts and see the whole picture."
    graph = [webpage("/download/", "Download and install Bucksley for Mac", d), crumbs("Download", "/download/"), APP, ORG, PERSON]
    rows = "\n".join(f'              <tr><td>{a}</td><td>{b}</td></tr>' for a, b in WHATS_NEW)
    big_apple = APPLE.replace('width="16" height="16"', 'width="20" height="20"')
    h = head("/download/", "Download and install Bucksley for Mac", d, graph) + header("/download/") + f'''  <main id="main">
    <div class="hero download-intro shell">
      <div class="download-head">
        <h1>Download Bucksley <em>for Mac.</em></h1>
        <p class="lead">Every account, one honest picture. Every feature is free.</p>
      </div>
      <section class="download-support" aria-labelledby="download-support-title">
        <span class="support-icon" aria-hidden="true">{ICON_CHAT}</span>
        <h2 id="download-support-title">Free software. <span>Shaped by people.</span></h2>
        <p class="support-copy">Every Bucksley feature is free, with nothing to unlock. Report a bug, suggest a bank or a feature, or tell us how Bucksley is working for you.</p>
        <div class="support-actions">
          <a class="button secondary" href="https://protomota.com/apps?app=bucksley#feedback">{ICON_CHAT}Send Feedback <span aria-hidden="true">↗</span></a>
        </div>
      </section>
      <div class="download-get">
        <a class="button download-button mac-download" href="{DMG}" download>{big_apple}<span>Download Bucksley {rel("version")}</span></a>
        <p class="fineprint">macOS 15 or later · Version {rel("version")} (build {rel("build")}) · {rel("size")}</p>
        <p class="fineprint">Signed by Protomota · Notarized by Apple · Signed automatic updates</p>
      </div>
    </div>
    <section class="shell download-guide" id="install" aria-labelledby="install-title">
      <h2 id="install-title">How to install Bucksley</h2>
      <ol class="install-steps">
        <li><div><strong>Open the disk image.</strong><p>Open <code>Bucksley-{REL["version"]}.dmg</code> in Downloads. Drag Bucksley into Applications, then eject the disk&nbsp;image.</p></div></li>
        <li><div><strong>Launch Bucksley from Applications.</strong><p>If macOS asks for confirmation, choose Open.</p></div></li>
        <li><div><strong>Connect your accounts.</strong><p>Use your SimpleFIN Bridge setup token or your own Plaid keys, or import a CSV from another finance app. Connection secrets are saved in the Keychain.</p></div></li>
        <li><div><strong>Review and budget.</strong><p>Bucksley files new transactions by category. Mark them reviewed, add rules and set budgets. Or connect an agent and let it help: see <a href="/mcp/">MCP setup</a>.</p></div></li>
      </ol>
      <p><strong>Automatic updates.</strong> Bucksley checks for new versions and installs signed updates for you. You can also choose <strong>Check for Updates</strong> from the Bucksley menu.</p>
      <details class="download-verification">
        <summary>Verify your download</summary>
        <p>In Terminal, run <code>shasum -a 256 ~/Downloads/Bucksley-{REL["version"]}.dmg</code> and compare the result with this SHA-256 checksum.</p>
        {rel("sha")}
      </details>
    </section>
    <section class="shell download-guide" id="whats-new" aria-labelledby="whats-new-title">
      <h2 id="whats-new-title">What’s in Bucksley</h2>
      <div class="table-wrap">
        <table class="tide-table">
          <thead><tr><th>Part</th><th>What it does</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
      <p>The iPhone app, with the review inbox, Apple Wallet accounts and widgets, is coming. Follow along on the <a href="https://newsletter.protomota.com/">Protomota newsletter</a>.</p>
    </section>
  </main>
''' + footer()
    write("download/index.html", h)


def mcp():
    d = "How Bucksley’s built-in MCP server lets Claude Code, Codex and Claude chat answer questions about your money, review transactions and write rules."
    graph = [webpage("/mcp/", "MCP setup · Bucksley", d), crumbs("MCP setup", "/mcp/"), APP, ORG, PERSON]
    tools = "\n".join(f'              <tr><td><code>{n}</code></td><td>{t}</td></tr>' for n, t in TOOLS)
    intro = ("Bucksley’s MCP server runs on your Mac, on the same data as the app. Install Bucksley, add it to your agent, and ask."
             if LIVE else "Bucksley’s MCP server runs on your Mac, on the same data as the app. Here’s how it will connect and what your agent can do. It works once the Mac app ships.")
    h = head("/mcp/", "MCP setup · Bucksley", d, graph) + header("/mcp/") + f'''  <main id="main">
    <div class="shell page-head">
      <span class="mark">mcp setup</span>
      <h1>Connect an agent to Bucksley.</h1>
      <p class="lead">{intro}</p>
    </div>
    <div class="shell doc">
      <nav class="toc" aria-label="On this page">
        <strong>On this page</strong>
        <a href="#how">How it works</a>
        <a href="#claude-code">Claude Code</a>
        <a href="#codex">Codex</a>
        <a href="#claude-chat">Claude chat</a>
        <a href="#tools">Tools</a>
        <a href="#try">Try it</a>
      </nav>
      <div class="prose">
        <section id="how">
          <h2>How it works</h2>
          <p>The Bucksley app runs as an MCP server when your agent starts it with <code>--mcp</code>. It talks over standard input and output, on your Mac only, and works on the same local workspace the app shows. Changes appear in the app right away and are listed under <strong>Settings → Agents</strong>.</p>
          <p class="note"><strong>You stay in control.</strong> Agents can only read until you turn on <strong>Let agents make changes</strong> in Settings → Agents, and every change they make is logged in the app. Bank secrets and AI keys stay in the Keychain and are never passed to an agent as tool arguments. Bucksley is read-only with your banks, so no tool can move money.</p>
        </section>
        <section id="claude-code">
          <h2>Claude Code</h2>
          <p>Add Bucksley as a local server for your user or project:</p>
          <p class="prompt">claude mcp add bucksley -- /Applications/Bucksley.app/Contents/MacOS/Bucksley --mcp</p>
        </section>
        <section id="codex">
          <h2>Codex</h2>
          <p>Add this to <code>~/.codex/config.toml</code>:</p>
          <p class="prompt">[mcp_servers.bucksley]<br>command = "/Applications/Bucksley.app/Contents/MacOS/Bucksley"<br>args = ["--mcp"]</p>
        </section>
        <section id="claude-chat">
          <h2>Claude chat</h2>
          <p>In the Claude desktop app, open <strong>Settings → Developer → Edit Config</strong> and add a <code>bucksley</code> entry under <code>mcpServers</code> with the same command and the <code>--mcp</code> argument. Restart Claude.</p>
        </section>
        <section id="tools">
          <h2>Tools</h2>
          <p>Ten tools read. Eight make changes, and stay off until you allow them.</p>
          <div class="table-wrap">
            <table class="tide-table">
              <thead><tr><th>Tool</th><th>What it does</th></tr></thead>
              <tbody>
{tools}
              </tbody>
            </table>
          </div>
        </section>
        <section id="try">
          <h2>Try it</h2>
          <p class="prompt">What did I spend on dining this month, and how does that compare with last month?</p>
          <p class="prompt">Go through my review queue, fix any obvious categories and make rules for the merchants you fixed.</p>
          <p class="prompt">Which subscriptions went up this year, and what do they cost me in total?</p>
        </section>
      </div>
    </div>
  </main>
''' + footer()
    write("mcp/index.html", h)


def faq():
    get = (("How do I get it?", "Download the signed and notarized disk image from bucksley.ai/download, open it and drag Bucksley into Applications. It needs macOS 15 or later.")
           if LIVE else ("When can I get it?", "Bucksley is in development for Mac and iPhone. Join the Protomota newsletter or Discord to hear when the first release ships."))
    items = [("What is Bucksley?", "Bucksley is a free personal finance app for Mac and iPhone, made by Protomota. It brings your bank accounts, cards and investments into one place to track spending, budgets, recurring bills and net worth. It is read-only and has no server: your data stays on your devices and in your own iCloud."),
             get,
             ("Is it free?", "Yes. Bucksley is free and open source, with no account, no trial and nothing to unlock."),
             ("How does it connect to my bank?", "Through services you sign up for yourself: SimpleFIN Bridge, or Plaid with your own developer keys. On iPhone it can also read Apple Card, Apple Cash and Savings through Apple’s FinanceKit. You can also import a CSV export from another finance app."),
             ("Can Bucksley move my money?", "No. Bucksley only reads balances and transactions. It cannot make payments or transfers, and it never asks for your bank password."),
             ("Where is my data kept?", "On your devices, and in your own private iCloud database so your Mac and iPhone stay in sync. Bucksley has no server. Connection secrets and AI keys are kept in the Keychain."),
             ("How does Ask Bucksley work?", "By default it uses Apple’s on-device model, so your question and your data stay on your device. If you add your own Claude or OpenAI key, questions you ask go to that provider."),
             ("Which AI agents can work with Bucksley?", "Claude Code, Codex and Claude chat, through a local MCP server with 18 tools. Agents can only read until you turn on Let agents make changes, and every change is logged.")]
    if LIVE:
        items.insert(3, ("How does it update?", "Bucksley checks for new versions and installs signed updates automatically. You can also choose Check for Updates from the Bucksley menu."))
        items.insert(4, ("Is there an iPhone app?", "The iPhone app is coming soon. It will sync with your Mac through your own private iCloud database."))
    return items


def help_page():
    d = ("Answers about Bucksley for Mac and iPhone: installing, updates, bank connections, privacy and agents, and how to reach us." if LIVE
         else "Answers about Bucksley for Mac and iPhone: bank connections, privacy, Ask Bucksley and agents, and how to reach us.")
    qs = faq()
    fq = {"@type": "FAQPage", "@id": f"{SITE}/help/#faq", "url": f"{SITE}/help/",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qs]}
    graph = [webpage("/help/", "Help · Bucksley", d), fq, crumbs("Help", "/help/"), APP, ORG, PERSON]
    qa = "\n".join(f"          <h3>{q}</h3>\n          <p>{a}</p>" for q, a in qs)
    h = head("/help/", "Help · Bucksley", d, graph) + header() + f'''  <main id="main">
    <div class="shell page-head">
      <span class="mark">help</span>
      <h1>Bucksley Help</h1>
      <p class="lead">{d}</p>
    </div>
    <div class="shell doc">
      <nav class="toc" aria-label="On this page">
        <strong>On this page</strong>
        <a href="#questions">Common questions</a>
        <a href="#contact">Get in touch</a>
      </nav>
      <div class="prose">
        <section id="questions">
          <h2>Common questions</h2>
{qa}
        </section>
        <section id="contact">
          <h2>Get in touch</h2>
          <p>Ask a question or tell us which bank or feature you’d like in <a href="https://lab.protomota.com">our Discord</a>, send feedback with <a href="https://protomota.com/apps?app=bucksley#feedback">the Protomota apps form</a>, or email <a href="mailto:hello@bucksley.ai">hello@bucksley.ai</a>.</p>
        </section>
      </div>
    </div>
  </main>
''' + footer()
    write("help/index.html", h)


def privacy():
    d = "How Bucksley, its bank connections, Ask Bucksley, agent connections and this website handle information."
    graph = [webpage("/privacy/", "Privacy · Bucksley", d), crumbs("Privacy", "/privacy/"), ORG]
    updates = ("\n          <p>To check for updates, the Mac app downloads a small feed from bucksley.ai. The request carries the app and macOS version, as any web request does, and none of your financial data.</p>" if LIVE else "")
    h = head("/privacy/", "Privacy · Bucksley", d, graph) + header() + f'''  <main id="main">
    <div class="shell page-head">
      <span class="mark">privacy</span>
      <h1>Privacy</h1>
      <p class="lead">Bucksley is made by Protomota, LLC. Your financial data stays on your devices and in your own iCloud. There is no Bucksley server.</p>
    </div>
    <div class="shell doc single">
      <div class="prose">
        <section>
          <h2>The app</h2>
          <p>Bucksley stores your workspace (accounts, balances, transactions, categories, rules, budgets, notes and tags) on your device. It has no account and no server, and sends none of your financial data to Protomota.</p>
          <p>Bucksley is read-only. It reads balances and transactions and cannot make payments, transfers or any other change at your bank.</p>{updates}
        </section>
        <section id="connections">
          <h2>Bank connections</h2>
          <p>Bucksley connects to financial institutions only through services you set up yourself. With SimpleFIN Bridge or Plaid, your device fetches balances and transactions directly from that service under your own account and keys; their privacy terms apply to what they hold. Bucksley never sees your bank password. On iPhone, Apple Card, Apple Cash and Savings are read through Apple’s FinanceKit only with your permission. CSV files you import are read on your device.</p>
          <p>Connection secrets (such as a SimpleFIN access URL or Plaid access token) and your Plaid keys are kept in the Keychain, never in the synced workspace.</p>
        </section>
        <section>
          <h2>iCloud sync</h2>
          <p>To keep your Mac and iPhone in step, Bucksley syncs your workspace through your own private iCloud database. Only you can read it. Apple’s iCloud terms apply. Keychain items sync only if you use iCloud Keychain.</p>
        </section>
        <section id="ask">
          <h2>Ask Bucksley</h2>
          <p>By default, Ask Bucksley uses Apple’s on-device model, so your questions and the data used to answer them stay on your device. If you add your own Claude or OpenAI key, your question and the relevant transactions are sent to that provider to answer it, under your account and their privacy terms. Your key is kept in the Keychain.</p>
        </section>
        <section id="mcp">
          <h2>Local agent connections</h2>
          <p>The MCP server runs on your Mac when an agent starts it, and works on the same local workspace. Agents can only read until you turn on Let agents make changes, and every change an agent makes is logged in Settings → Agents. Keys are never passed to agents.</p>
          <p>Your chosen agent may send information it retrieves to its AI provider. Review that provider’s privacy terms before connecting.</p>
        </section>
        <section>
          <h2 id="hosting">Where we host</h2>
          <p>This site runs on <a href="https://www.cloudflare.com/">Cloudflare</a>. Cloudflare serves every page and manages our traffic, so it handles standard request details such as your IP address and browser to deliver the site and protect it from abuse. Our images and downloads are stored in Cloudflare R2. Cloudflare handles that data under its <a href="https://www.cloudflare.com/privacypolicy/">privacy policy</a>.</p>
          <p>We&rsquo;re not a Cloudflare sponsor. We chose them because we think they&rsquo;re the best value and the best service, and we&rsquo;ll keep using them for as long as that stays true. <a href="https://protomota.com/about#hosting">How we build and&nbsp;host</a></p>
        </section>
        <section>
          <h2>Website and support</h2>
          <p>The site provides information about Bucksley. Hosting providers may process request information to deliver the site. If you contact us, we use the details you send to respond.</p>
          <p>If you click Allow analytics, the site loads Google Analytics, which sets cookies to count visits, page views and link clicks. Page addresses are sent without query strings, and advertising features are off. If you decline, Google Analytics does not load. Change your choice any time with Analytics settings in the footer.</p>
          <p><a href="https://protomota.com/apps?app=bucksley#feedback">Send Feedback</a> · <a href="mailto:hello@bucksley.ai">hello@bucksley.ai</a></p>
        </section>
      </div>
    </div>
  </main>
''' + footer()
    write("privacy/index.html", h)


def notfound():
    h = head("/404", "Page not found · Bucksley", "", None, noindex=True) + header(body_class="missing-page") + f'''  <main id="main" class="hero missing-hero shell">
    <img src="/assets/icon.png?v={V}" width="66" height="66" alt="">
    <h1>Page <em>not found.</em></h1>
    <p class="lead">The page may have moved. You can still get back to Bucksley or find help.</p>
    <div class="actions">
      <a class="button" href="/">{ICON_HOME}Back to Home</a>
      <a class="button secondary" href="/help/">{ICON_HELP}Get Help</a>
    </div>
  </main>
''' + footer()
    write("404.html", h)


def llms():
    if LIVE:
        platform = "- Platform: Mac, macOS 15 or later. The iPhone app (iOS 18 or later) is coming soon and is not on the App Store yet."
        install = (f"- Install: a signed and notarized disk image from {SITE}/download/ with signed automatic updates (Sparkle).\n"
                   f"- Download: {SITE}{DMG}\n"
                   f"- Current release: Bucksley {REL['version']} (build {REL['build']}), {REL['size']}. SHA-256: {REL['sha']}")
        status = "Bucksley for Mac is available. The iPhone app is coming soon."
    else:
        platform = "- Platform: Mac (macOS 15 or later) and iPhone (iOS 18 or later). Both are in development and not available yet."
        install = "- Status: coming soon. There is no download yet and it is not on the App Store."
        status = "Bucksley is in development and coming soon for Mac and iPhone."
    text = f"""# Bucksley

> Bucksley is a free, local-first personal finance app for Mac and iPhone, made by Protomota. It brings bank accounts, cards and investments into one place to track spending, budgets, recurring bills and net worth. It is read-only and never moves money. Data stays on the user's devices and in their own private iCloud; there is no Bucksley server and no account. A built-in MCP server lets AI agents such as Claude Code, Codex and Claude chat work with it. {status}

Bucksley's website is {SITE}. Other products with similar names are not related to it.

Key facts:

- Maker: Protomota (Protomota, LLC), the independent studio of Brad Dunlap. https://protomota.com
- Price: free. Every feature is included.
- License: free and open source (MIT).
{platform}
{install}
- Connections: SimpleFIN Bridge (the user's own account), Plaid with the user's own developer keys, Apple Card, Apple Cash and Savings through Apple FinanceKit on iPhone, and CSV import from other finance apps. All read-only.
- Features: net worth stacked by what it is made of, accounts, transactions (search, filter, rename, recategorize, split, notes, tags, mark reviewed), categories and groups with rules, budgets with rollover, pace and suggested amounts, recurring bills and subscriptions, Ask Bucksley, an iPhone review inbox that syncs back to the Mac, widgets and App Intents.
- Ask Bucksley: Apple's on-device model by default; optionally the user's own Claude or OpenAI key.
- Privacy: the workspace is stored on the user's devices and synced through their private iCloud database. Connection secrets and AI keys are kept in the Keychain, never on a server and never in agent tool arguments.
- Agents: the Mac app runs as a local MCP server with `Bucksley --mcp` (18 tools: 10 read, 8 that make changes). Agents can only read until the user turns on Let agents make changes; every agent change is logged in Settings → Agents.

## Pages

- [Bucksley]({SITE}/): what it does, the working preview, connections, the iPhone app, agents and privacy
- [{"Download and install" if LIVE else "Coming soon"}]({SITE}/download/): {"the Mac installer, install steps and the SHA-256 checksum" if LIVE else "what the first release includes and what you will need"}
- [MCP setup]({SITE}/mcp/): connecting Claude Code, Codex and Claude chat, and the tool list
- [Help]({SITE}/help/): common questions
- [Privacy]({SITE}/privacy/): how the app, bank connections, Ask Bucksley, agent connections and the website handle information

## Common questions

- What is Bucksley? A free, read-only personal finance app for Mac and iPhone with no Bucksley server.
- Is Bucksley free? Yes. It is free and open source, with no account, no trial and nothing to unlock.
- Can it move money? No. It only reads balances and transactions.
- How does it connect to banks? SimpleFIN Bridge or the user's own Plaid keys, Apple FinanceKit on iPhone, or CSV import.
- Which agents work with Bucksley? Claude Code, Codex and Claude chat, through its local MCP server.

## Optional

- [Bucksley on protomota.com](https://protomota.com/apps)
- [More Protomota apps](https://protomota.com/apps): OpenTalon, Inkspring, Jotley, Glimmer, PulseCanvas Studio, Voxley, Graphley and Textley
"""
    write("llms.txt", text)


index(); download(); mcp(); help_page(); privacy(); notfound(); llms()
print("ok", REL or "coming soon")
