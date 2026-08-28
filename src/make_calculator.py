#!/usr/bin/env python3
"""
make_calculator.py - emit the offline scoring card as a single HTML file.

    python3 src/make_calculator.py

Reads results/points_A.csv and results/score_bands.csv and writes
docs/calculator.html: one file, no network, no fonts to fetch, no scripts to
load. It has to open on a five-year-old Android phone in a puskesmas with the
data switched off, which rules out every convenience that assumes a CDN.
"""

import json
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT

DOCS = "docs"

# How each scored term is presented to the person holding the phone. Order is
# the order of the form.
FIELDS = [
    ("age", "number", "Umur", "tahun", None),
    ("sex_f", "select", "Jenis kelamin", None,
     [("Laki-laki", 0), ("Perempuan", 1)]),
    ("waist", "number", "Lingkar perut", "cm", None),
    ("sbp", "number", "Tekanan darah sistolik", "mmHg", None),
    ("smoke_current", "select", "Status merokok", None,
     [("Tidak pernah", 0), ("Mantan perokok", 0), ("Masih merokok", 1)]),
    ("dm_dur_cat", "select", "Diabetes", None,
     [("Tidak ada", 0), ("< 5 tahun", 1), ("5-10 tahun", 2),
      ("> 10 tahun", 3)]),
    ("htn_med", "select", "Minum obat hipertensi", None,
     [("Tidak", 0), ("Ya", 1)]),
    ("prior_cvd", "select", "Riwayat jantung / stroke", None,
     [("Tidak", 0), ("Ya", 1)]),
]


def main():
    pts = pd.read_csv(os.path.join(OUT, "points_A.csv"))
    bands = pd.read_csv(os.path.join(OUT, "score_bands.csv"))
    with open(os.path.join(OUT, "summary.json")) as f:
        summary = json.load(f)

    spec = {r["term"]: dict(per_unit=float(r["per_unit"]),
                            reference=float(r["reference"]),
                            points=int(r["points"]))
            for _, r in pts.iterrows()}
    offset = int(summary.get("points_offset_a", 0))

    band_list = [dict(band=str(r["band"]), risk=float(r["risk"]),
                      n=int(r["n"]), events=int(r["events"]))
                 for _, r in bands.iterrows()]

    # smoke_former shares a control with smoke_current; both carry points.
    fields_json = json.dumps(FIELDS, ensure_ascii=False)
    spec_json = json.dumps(spec)
    bands_json = json.dumps(band_list, ensure_ascii=False)

    html = TEMPLATE.replace("__SPEC__", spec_json) \
                   .replace("__FIELDS__", fields_json) \
                   .replace("__BANDS__", bands_json) \
                   .replace("__OFFSET__", str(offset)) \
                   .replace("__THRESH__", str(summary.get(
                       "chosen_threshold", {}).get("threshold", 0.2))) \
                   .replace("__AUC__", f"{summary['version_a']['auc_corr']:.2f}")

    os.makedirs(DOCS, exist_ok=True)
    path = os.path.join(DOCS, "calculator.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(path)
    print(f"Wrote {path} ({size / 1024:.1f} KB, self-contained)")
    return 0


TEMPLATE = r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skor Triase Kaki - ABI &amp; Monofilamen</title>
<style>
  :root{
    --bg:#fbfaf8; --fg:#1c1a17; --muted:#6b6560; --line:#e0dbd4;
    --card:#ffffff; --accent:#8a3324;
    --low:#2f6b4f; --mid:#a8761f; --high:#8a3324;
  }
  @media (prefers-color-scheme: dark){
    :root{ --bg:#171614; --fg:#eeebe6; --muted:#a29b93; --line:#33302c;
           --card:#201e1b; --low:#7fc0a0; --mid:#e0b464; --high:#e08272; }
  }
  *{box-sizing:border-box}
  body{margin:0;padding:16px;background:var(--bg);color:var(--fg);
    font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
    max-width:520px;margin-inline:auto}
  h1{font-size:19px;margin:0 0 2px;letter-spacing:-.01em}
  .sub{color:var(--muted);font-size:13px;margin:0 0 18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;
    padding:14px;margin-bottom:14px}
  label{display:block;margin-bottom:12px}
  label:last-child{margin-bottom:0}
  .lab{display:block;font-size:13px;color:var(--muted);margin-bottom:4px}
  input,select{width:100%;padding:9px 10px;font-size:16px;color:var(--fg);
    background:var(--bg);border:1px solid var(--line);border-radius:7px}
  input:focus,select:focus{outline:2px solid var(--accent);outline-offset:-1px}
  .score{font-size:40px;font-weight:600;line-height:1;letter-spacing:-.02em}
  .risk{font-size:15px;margin-top:6px}
  .verdict{margin-top:12px;padding:11px 12px;border-radius:8px;font-size:14px;
    border:1px solid var(--line)}
  .go{border-color:var(--high);color:var(--high);font-weight:600}
  table{width:100%;border-collapse:collapse;font-size:13px;margin-top:6px}
  th,td{text-align:left;padding:5px 4px;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-weight:500}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  .foot{color:var(--muted);font-size:12px;line-height:1.5}
  .bar{height:5px;border-radius:3px;background:var(--line);overflow:hidden;
    margin-top:8px}
  .bar > i{display:block;height:100%;background:var(--accent)}
</style>
</head>
<body>

<h1>Skor Triase Kaki</h1>
<p class="sub">Menentukan pasien mana yang diperiksa ABI dan monofilamen lebih
dulu. Tanpa alat, tanpa laboratorium.</p>

<div class="card" id="form"></div>

<div class="card">
  <div class="lab">Total skor</div>
  <div class="score" id="score">-</div>
  <div class="risk" id="risk"></div>
  <div class="bar"><i id="bar" style="width:0%"></i></div>
  <div class="verdict" id="verdict"></div>
</div>

<div class="card">
  <div class="lab">Risiko menurut pita skor (data NHANES 1999-2004)</div>
  <table id="bands"><thead><tr><th>Skor</th><th class="num">n</th>
    <th class="num">Kasus</th><th class="num">Risiko</th></tr></thead>
    <tbody></tbody></table>
</div>

<p class="foot">
Endpoint: penyakit ekstremitas bawah - ABI &lt;0,90 pada salah satu tungkai
<em>atau</em> titik insensat pada monofilamen 10 g.
AUC terkoreksi optimisme __AUC__.
Skor ini menentukan <em>urutan pemeriksaan</em>, bukan diagnosis. Pasien dengan
ulkus, luka, atau nyeri istirahat dirujuk tanpa memandang skor.
</p>

<script>
const SPEC   = __SPEC__;
const FIELDS = __FIELDS__;
const BANDS  = __BANDS__;
const OFFSET = __OFFSET__;

const form = document.getElementById('form');
FIELDS.forEach(([key, kind, label, unit, opts]) => {
  const l = document.createElement('label');
  const s = document.createElement('span');
  s.className = 'lab';
  s.textContent = label + (unit ? ' (' + unit + ')' : '');
  l.appendChild(s);
  let el;
  if (kind === 'select') {
    el = document.createElement('select');
    opts.forEach(([text, val], i) => {
      const o = document.createElement('option');
      o.value = String(val); o.textContent = text;
      // The smoking control carries three labels over two scored levels;
      // index is kept so "former" can be told from "never".
      o.dataset.idx = String(i);
      el.appendChild(o);
    });
  } else {
    el = document.createElement('input');
    el.type = 'number'; el.inputMode = 'numeric';
    el.value = ({age:55, waist:90, sbp:130})[key] ?? '';
  }
  el.id = 'f_' + key;
  el.addEventListener('input', calc);
  el.addEventListener('change', calc);
  l.appendChild(el);
  form.appendChild(l);
});

function pointsFor(key, value){
  const s = SPEC[key];
  if (!s) return 0;
  return Math.round((value - s.reference) / s.per_unit) * s.points;
}

function calc(){
  let total = OFFSET;
  FIELDS.forEach(([key, kind]) => {
    const el = document.getElementById('f_' + key);
    if (!el) return;
    const v = parseFloat(el.value);
    if (kind === 'number') {
      if (!isFinite(v)) return;
      total += pointsFor(key, v);
    } else if (key === 'smoke_current') {
      const idx = parseInt(el.selectedOptions[0].dataset.idx, 10);
      total += pointsFor('smoke_current', idx === 2 ? 1 : 0);
      total += pointsFor('smoke_former',  idx === 1 ? 1 : 0);
    } else {
      total += pointsFor(key, v);
    }
  });

  document.getElementById('score').textContent = total;

  // Nearest band by parsing its printed range.
  let hit = null;
  for (const b of BANDS) {
    const m = b.band.match(/^(<=|>=)?(-?\d+)(?:-(-?\d+))?$/);
    if (!m) continue;
    const a = parseInt(m[2], 10);
    if (m[1] === '<=' && total <= a) { hit = b; break; }
    if (m[1] === '>=' && total >= a) { hit = b; break; }
    if (!m[1] && m[3] !== undefined &&
        total >= a && total <= parseInt(m[3], 10)) { hit = b; break; }
  }
  if (!hit) hit = total < 0 ? BANDS[0] : BANDS[BANDS.length - 1];

  const pct = (hit.risk * 100);
  document.getElementById('risk').textContent =
    'Perkiraan risiko penyakit ekstremitas bawah: ' + pct.toFixed(0) + '%';
  document.getElementById('bar').style.width =
    Math.min(100, pct * 2).toFixed(0) + '%';

  const v = document.getElementById('verdict');
  const top = BANDS[BANDS.length - 1];
  if (hit.band === top.band || hit.risk >= top.risk * 0.9) {
    v.className = 'verdict go';
    v.textContent = 'Prioritas tinggi - periksa ABI dan monofilamen hari ini.';
  } else if (pct >= 20) {
    v.className = 'verdict';
    v.textContent = 'Prioritas menengah - jadwalkan pemeriksaan bila kapasitas '
      + 'masih ada hari ini.';
  } else {
    v.className = 'verdict';
    v.textContent = 'Prioritas rendah - pemeriksaan dapat ditunda; '
      + 'edukasi perawatan kaki tetap diberikan.';
  }
}

const tb = document.querySelector('#bands tbody');
BANDS.forEach(b => {
  const tr = document.createElement('tr');
  tr.innerHTML = '<td>' + b.band + '</td>'
    + '<td class="num">' + b.n + '</td>'
    + '<td class="num">' + b.events + '</td>'
    + '<td class="num">' + (b.risk * 100).toFixed(0) + '%</td>';
  tb.appendChild(tr);
});

calc();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
