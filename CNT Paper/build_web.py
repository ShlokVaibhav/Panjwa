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
  * MECHANICAL   - deterministic fixes to pandoc's output: copy EVERY figure to
                   a site asset + rewrite its path, and hand pandoc's \\eqref
                   link to MathJax so it renders the live equation number.
  * NAV-CHROME   - two navigation links (PDF / LaTeX source). These two link
                   labels are the ONLY script-authored strings; see below.

Reproduce:  python3 build_web.py      (idempotent; safe to re-run)
"""
import re, os, sys, subprocess

PAPER_DIR = "/Users/shlok/Documents/Repos/Panjwa/CNT Paper"
SITE_DIR  = "/Users/shlok/Documents/Repos/shlokvaibhav.github.io"
PAPER_ID  = "cnt"                       # namespace prefix for this paper's assets
TEX     = os.path.join(PAPER_DIR, "CNT.tex")
BIB     = os.path.join(PAPER_DIR, "references.bib")
FIG_DIR = os.path.join(PAPER_DIR, "Figures")
OUT     = os.path.join(SITE_DIR, "cnt.html")
PDF_URL = "https://github.com/ShlokVaibhav/Panjwa/blob/main/CNT%20Paper/CNT.pdf"
SRC_URL = "https://github.com/ShlokVaibhav/Panjwa/tree/main/CNT%20Paper"

# Preserve already-published asset URLs; any figure not listed is auto-named.
FIG_RENAME = {"Restyled graphene lattice and Brillouin zone.png":
              "papers/cnt-graphene-lattice-bz.png"}

def asset_rel(fname):
    """Site-relative asset path for a figure referenced in the .tex."""
    if fname in FIG_RENAME:
        return FIG_RENAME[fname]
    slug = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(fname)[0].lower()).strip("-")
    if not slug.startswith(PAPER_ID):
        slug = f"{PAPER_ID}-{slug}"
    return f"papers/{slug}.png"

# ---- 0. Refresh LaTeX .aux / .pdf so cross-reference numbers are current ----
# (not check=True: latexmk may exit nonzero on transient ref warnings while
#  still producing a correct .aux; we validate labels from the .aux below.)
subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", TEX],
               cwd=PAPER_DIR, capture_output=True)

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
body = full[m.end(): full.rindex("</body>")]     # sections/eqns/figures/refs (from source)
tm = re.search(r'<h1 class="title">(.*?)</h1>', titleblock, re.S)
doc_title = re.sub(r"\s+", " ", tm.group(1)).strip() if tm else "CNT paper"

# ---- 2. MECHANICAL fixes to pandoc output (deterministic) ------------------
# 2a. FIGURES: discover EVERY \includegraphics in the source; copy each to a
#     downscaled site asset and rewrite its <img src="..."> to that asset.
figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}",
                  open(TEX, encoding="utf-8").read())
copied = []
for fname in dict.fromkeys(figs):                # de-dup, preserve order
    src = os.path.join(FIG_DIR, fname)
    if not os.path.exists(src):
        sys.exit(f"ERROR: figure referenced but not found: {src}")
    rel = asset_rel(fname)
    dst = os.path.join(SITE_DIR, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(["sips", "-Z", "1000", src, "--out", dst],
                   capture_output=True, check=True)
    body = body.replace(f'src="{fname}"', f'src="{rel}"')
    copied.append(rel)

# 2b. Pandoc renders every \eqref/\ref as a link showing the raw label text
#     (e.g. "[eq:dkx-dE]"). Hand equation refs to MathJax so they render "(N)"
#     from the SAME counter that numbers the displayed equations.
body = re.sub(r'<a href="#(eq:[^"]+)"[^>]*>\[[^\]]*\]</a>',
              r'\\(\\eqref{\1}\\)', body)
# 2c. section refs -> re-assert the number from LaTeX's .aux (single source of
#     truth), keeping the working anchor link.
_aux = open(os.path.join(PAPER_DIR, "CNT.aux"), encoding="utf-8").read()
_auxnum = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', _aux))
body = re.sub(r'<a href="#(sec:[^"]+)"[^>]*>.*?</a>',
              lambda mo: f'<a href="#{mo.group(1)}">{_auxnum.get(mo.group(1), mo.group(1))}</a>',
              body, flags=re.S)

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
  .tune {{ margin: .2rem 0 1.6rem; }}
  .tune button {{ font: inherit; cursor: pointer; padding: .35rem .9rem; border: 1px solid rgba(0,0,0,.28); border-radius: 5px; background: transparent; color: inherit; opacity: .85; }}
  .tune button:hover {{ opacity: 1; border-color: rgba(0,0,0,.5); }}
</style>
<script>window.MathJax = {{ tex: {{ tags: 'ams' }} }};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
'''

# NAV-CHROME: script-authored strings on the page (nav links + audio button label).
doclinks = (f'<p class="doclinks"><a href="{PDF_URL}">PDF</a> &nbsp;·&nbsp; '
            f'<a href="{SRC_URL}">LaTeX source</a></p>')

# Opt-in audio easter egg. NOT autoplay (browsers block sound-on-load); the clip
# plays on click, toggles on a second click, and resets its label when it ends.
TUNE = ('<div class="tune">\n'
        '  <button id="tune-btn" type="button">▶ Laufet Brüder eure Bahn!</button>\n'
        '  <audio id="tune-audio" src="media/eurebahn.m4a" preload="none"></audio>\n'
        '</div>\n'
        '<script>\n'
        '(function(){var b=document.getElementById("tune-btn"),a=document.getElementById("tune-audio"),'
        'P="▶ Laufet Brüder eure Bahn!",S="◼ Halt!";'
        'b.addEventListener("click",function(){if(a.paused){a.currentTime=0;a.play();b.textContent=S;}'
        'else{a.pause();b.textContent=P;}});'
        'a.addEventListener("ended",function(){b.textContent=P;});})();\n'
        '</script>')

page = (HEAD + "\n" + header +
        '\n\n<main class="wrap">\n' + titleblock + "\n" + doclinks + "\n" + TUNE +
        '\n<article class="paper">\n' + body +
        '\n</article>\n</main>\n\n' + footer + "\n\n</body>\n</html>\n")

open(OUT, "w", encoding="utf-8").write(page)
print(f"wrote {OUT} ({len(page)} bytes); title from source: {doc_title!r}")
print(f"figures copied ({len(copied)}): " + ", ".join(copied))
