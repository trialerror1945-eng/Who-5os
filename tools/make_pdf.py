#!/usr/bin/env python3
"""
make_pdf.py - render the manuscript to a typeset PDF.

    python3 tools/make_pdf.py

Markdown -> HTML -> Chromium print-to-PDF. Chromium is used rather than a
LaTeX toolchain because it is already present and because the manuscript's
figures are PNGs that need to sit inline at a controlled width.

Figures named in the text as `results/figN_*.png` are inlined as base64 at the
point where the Figures section lists them, so the PDF is self-contained.
"""

import base64
import os
import re
import sys
import markdown

SRC = os.path.join("docs", "manuscript.md")
OUT_HTML = os.path.join("docs", "manuscript.html")
OUT_PDF = os.path.join("docs", "manuscript.pdf")

FIGS = {
    "fig1_capacity.png": "Figure 1",
    "fig2_roc.png": "Figure 2",
    "fig3_calibration.png": "Figure 3",
    "fig4_dca.png": "Figure 4",
    "fig5_survival.png": "Figure 5",
}

CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
body { font: 10.5pt/1.5 "Source Serif 4", Georgia, "Times New Roman", serif;
       color: #16191b; max-width: none; }
h1 { font-size: 17pt; line-height: 1.22; margin: 0 0 4mm;
     font-weight: 600; letter-spacing: -0.01em; }
h2 { font-size: 12.5pt; margin: 8mm 0 3mm; font-weight: 600;
     border-bottom: 0.6pt solid #ccd2d1; padding-bottom: 1.6mm; }
h3 { font-size: 10.8pt; margin: 5mm 0 2mm; font-weight: 600; }
p  { margin: 0 0 2.6mm; text-align: justify; hyphens: auto; }
strong { font-weight: 600; }
em { font-style: italic; }
hr { border: none; border-top: 0.6pt solid #ccd2d1; margin: 6mm 0; }
ul, ol { margin: 0 0 3mm 5mm; padding: 0; }
li { margin-bottom: 1.2mm; }
code { font: 9pt "DejaVu Sans Mono", monospace; background: #f2f4f4;
       padding: 0.3mm 1mm; border-radius: 1mm; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0 5mm;
        font-size: 8.8pt; page-break-inside: avoid; }
th, td { border-bottom: 0.4pt solid #dde2e1; padding: 1.5mm 2mm;
         text-align: left; vertical-align: top; }
thead th { border-bottom: 0.8pt solid #9aa3a2; font-weight: 600;
           font-size: 8.4pt; }
td:not(:first-child), th:not(:first-child) { text-align: right;
  font-variant-numeric: tabular-nums; }
figure { margin: 5mm 0; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; height: auto; }
figcaption { font-size: 8.6pt; color: #4a5254; margin-top: 2mm;
             text-align: left; }
.abstract { background: #f7f9f9; border-left: 1.2pt solid #0e6a66;
            padding: 4mm 5mm; margin: 4mm 0 6mm; font-size: 10pt; }
h2 + p, h3 + p { margin-top: 0; }
"""


def main():
    md = open(SRC, encoding="utf-8").read()

    # Inline each figure where the Figures section names it.
    for fname, label in FIGS.items():
        path = os.path.join("results", fname)
        if not os.path.exists(path):
            print(f"  missing figure: {path}")
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        img = (f'\n\n<figure><img src="data:image/png;base64,{b64}" '
               f'alt="{label}"></figure>\n\n')
        # Replace the backticked path reference with the image itself.
        md = md.replace(f"`results/{fname}`", img)

    html_body = markdown.markdown(
        md, extensions=["tables", "sane_lists", "attr_list"])

    html = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{CSS}</style></head><body>{html_body}</body></html>")
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUT_HTML} ({len(html)/1024:.0f} KB)")

    # The pip playwright here is newer than the image's bundled browser, so it
    # looks for a revision that is not present. The environment ships chromium
    # at a stable symlink; point at that rather than downloading a second copy.
    from playwright.sync_api import sync_playwright
    chrome = "/opt/pw-browsers/chromium"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=chrome if os.path.exists(chrome) else None,
            args=["--no-sandbox"])
        page = browser.new_page()
        page.goto("file://" + os.path.abspath(OUT_HTML),
                  wait_until="networkidle")
        page.pdf(path=OUT_PDF, format="A4", print_background=True,
                 margin={"top": "20mm", "bottom": "18mm",
                         "left": "18mm", "right": "18mm"},
                 display_header_footer=True,
                 header_template="<div></div>",
                 footer_template=(
                     "<div style='font:8pt Georgia,serif;color:#6b7472;"
                     "width:100%;text-align:center;padding-top:4mm'>"
                     "<span class='pageNumber'></span></div>"))
        browser.close()
    size = os.path.getsize(OUT_PDF)
    print(f"Wrote {OUT_PDF} ({size/1e6:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
