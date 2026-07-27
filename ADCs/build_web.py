#!/usr/bin/env python3
"""
Build pipeline: ADCs/OnQuantization.md -> shlokvaibhav.github.io/quantization.html

pandoc renders ALL page content (prose + LaTeX math) from the markdown source.
This script only adds site chrome (header/footer copied verbatim from the site's
notes.html, fonts, styles.css, MathJax) and one link back to the source on GitHub.
No prose is authored here.

Reproduce:  python3 build_web.py
"""
import re, os, subprocess, sys

SRC     = "/Users/shlok/Documents/Repos/Panjwa/ADCs/OnQuantization.md"
SITE    = "/Users/shlok/Documents/Repos/shlokvaibhav.github.io"
OUT     = os.path.join(SITE, "quantization.html")
SRC_URL = "https://github.com/ShlokVaibhav/Panjwa/blob/main/ADCs/OnQuantization.md"

# ---- 1. CONTENT: pandoc renders the markdown (math via MathJax) ----
body = subprocess.run(
    ["pandoc", SRC, "--mathjax", "-f", "markdown", "-t", "html5"],
    capture_output=True, text=True, check=True).stdout

# title = first H1; lift it out of the body (shown once in the page-head)
m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "Tech note"
body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.S).strip()

# ---- 2. SITE CHROME: header + footer taken verbatim from notes.html ----
notes  = open(os.path.join(SITE, "notes.html"), encoding="utf-8").read()
header = notes[notes.index("<header"): notes.index("</header>") + len("</header>")].replace(' aria-current="page"', '')
footer = notes[notes.index("<footer"): notes.index("</footer>") + len("</footer>")]

HEAD = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} — Shlok Vaibhav</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="styles.css" />
<style>
  .paper {{ line-height: 1.65; }}
  .paper h2 {{ margin-top: 2.2rem; }}
  .paper h3 {{ margin-top: 1.4rem; }}
  .paper img {{ max-width: 100%; height: auto; }}
  .paper blockquote {{ border-left: 3px solid rgba(0,0,0,.18); margin: 1.2rem 0; padding-left: 1rem; opacity: .85; }}
  .paper mjx-container[display="true"] {{ overflow-x: auto; overflow-y: hidden; padding: .2rem 0; }}
  .doclinks {{ margin: .6rem 0 1.5rem; opacity: .85; }}
</style>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
'''

doclinks = f'<p class="doclinks"><a href="{SRC_URL}">Source (markdown) →</a></p>'

page = (HEAD + "\n" + header +
        '\n\n<main class="wrap">\n  <section class="page-head">\n    <h1>' + title + '</h1>\n    ' +
        doclinks + '\n  </section>\n  <article class="paper">\n' + body +
        '\n  </article>\n</main>\n\n' + footer + "\n\n</body>\n</html>\n")

open(OUT, "w", encoding="utf-8").write(page)
print(f"wrote {OUT} ({len(page)} bytes); title: {title!r}")
