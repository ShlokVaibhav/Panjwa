#!/usr/bin/env python3
"""
Auditable build pipeline:  CNT.tex  ->  shlokvaibhav.github.io/cnt.html

TRUST CONTRACT
--------------
Every word of PAGE CONTENT (title, author, date, abstract, section prose,
equations, citations, reference list) is produced by `pandoc` from CNT.tex
and references.bib. This script writes NO sentence describing the paper.

The script only:
  * SITE CHROME  - header nav + footer copied verbatim from the site's own
                   notes.html, plus standard includes (Google font, styles.css,
                   MathJax). Site-owned, not authored here.
  * MECHANICAL   - deterministic fixes to pandoc's output: rewrite the figure
                   path to the site asset, and hand pandoc's \\eqref link to
                   MathJax so it renders the live equation number.
  * NAV-CHROME   - two navigation links (PDF / LaTeX source). These two link
                   labels are the ONLY script-authored strings; see below.

Reproduce:  python3 build_web.py      (idempotent; safe to re-run)
"""
import re, os, sys, subprocess

PAPER_DIR = "/Users/shlok/Documents/Repos/Panjwa/CNT Paper"
SITE_DIR  = "/Users/shlok/Documents/Repos/shlokvaibhav.github.io"
TEX     = os.path.join(PAPER_DIR, "CNT.tex")
BIB     = os.path.join(PAPER_DIR, "references.bib")
FIG_SRC = os.path.join(PAPER_DIR, "Figures", "Restyled graphene lattice and Brillouin zone.png")
OUT     = os.path.join(SITE_DIR, "cnt.html")
FIG_REL = "papers/cnt-graphene-lattice-bz.png"
FIG_DST = os.path.join(SITE_DIR, FIG_REL)
PDF_URL = "https://github.com/ShlokVaibhav/Panjwa/blob/main/CNT%20Paper/CNT.pdf"
SRC_URL = "https://github.com/ShlokVaibhav/Panjwa/tree/main/CNT%20Paper"

# ---- 1. CONTENT: pandoc renders the whole document from source -------------
full = subprocess.run(
    ["pandoc", TEX, "--standalone", "--citeproc", "--bibliography", BIB,
     "--mathjax", "--shift-heading-level-by=1",
     "--metadata", "reference-section-title=References", "-t", "html5"],
    cwd=PAPER_DIR, capture_output=True, text=True, check=True).stdout

m = re.search(r'<header id="title-block-header">.*?</header>', full, re.S)
if not m:
    sys.exit("ERROR: pandoc title block not found")
titleblock = m.group(0)                          # title/author/date/abstract (from source)
body = full[m.end(): full.rindex("</body>")]     # sections/eqns/figure/refs (from source)
tm = re.search(r'<h1 class="title">(.*?)</h1>', titleblock, re.S)
doc_title = re.sub(r"\s+", " ", tm.group(1)).strip() if tm else "CNT paper"

# ---- 2. MECHANICAL fixes to pandoc output (deterministic) ------------------
body = body.replace('src="Restyled graphene lattice and Brillouin zone.png"',
                    f'src="{FIG_REL}"')
body = re.sub(r'<a href="#eq:band-structure"[^>]*>\[eq:band-structure\]</a>',
              r'\\(\\eqref{eq:band-structure}\\)', body)

# ---- 3. SITE CHROME: header + footer taken verbatim from notes.html --------
notes = open(os.path.join(SITE_DIR, "notes.html"), encoding="utf-8").read()
header = notes[notes.index("<header"): notes.index("</header>") + len("</header>")]
header = header.replace(' aria-current="page"', '')
footer = notes[notes.index("<footer"): notes.index("</footer>") + len("</footer>")]

HEAD = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{doc_title} — Shlok Vaibhav</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="styles.css" />
<style>
  .paper, #title-block-header {{ line-height: 1.6; }}
  #title-block-header .title {{ margin-bottom: .2rem; }}
  #title-block-header .author, #title-block-header .date {{ margin: 0; opacity: .7; }}
  .abstract {{ margin: 1.4rem 0; padding-left: 1rem; border-left: 3px solid rgba(0,0,0,.15); }}
  .abstract-title {{ font-weight: 600; }}
  .paper h2 {{ margin-top: 2.2rem; }}
  .paper figure {{ margin: 2rem auto; text-align: center; }}
  .paper figure img {{ max-width: 100%; height: auto; }}
  .paper figcaption {{ font-size: .9rem; opacity: .72; margin-top: .5rem; }}
  .paper mjx-container[display="true"] {{ overflow-x: auto; overflow-y: hidden; padding: .2rem 0; }}
  .csl-bib-body {{ margin-top: .6rem; }}
  .csl-entry {{ margin: .6rem 0; padding-left: 1.4rem; text-indent: -1.4rem; }}
  .doclinks {{ margin: 1rem 0 2rem; opacity: .85; }}
</style>
<script>window.MathJax = {{ tex: {{ tags: 'ams' }} }};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
'''

# NAV-CHROME: the only script-authored strings on the page (navigation links).
doclinks = (f'<p class="doclinks"><a href="{PDF_URL}">PDF</a> &nbsp;·&nbsp; '
            f'<a href="{SRC_URL}">LaTeX source</a></p>')

page = (HEAD + "\n" + header +
        '\n\n<main class="wrap">\n' + titleblock + "\n" + doclinks +
        '\n<article class="paper">\n' + body +
        '\n</article>\n</main>\n\n' + footer + "\n\n</body>\n</html>\n")

# structural asset: downscaled copy of the figure (not content)
if os.path.exists(FIG_SRC):
    subprocess.run(["sips", "-Z", "1000", FIG_SRC, "--out", FIG_DST],
                   capture_output=True, check=True)

open(OUT, "w", encoding="utf-8").write(page)
print(f"wrote {OUT} ({len(page)} bytes); title from source: {doc_title!r}")
