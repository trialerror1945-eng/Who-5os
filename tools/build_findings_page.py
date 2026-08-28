import json
figs = json.load(open("/tmp/claude-0/-home-user-Who-5os/731e32d0-c6af-5670-ae4f-02f43eba3ec4/scratchpad/figs.json"))

HEAD = """<title>Which Feet Deserve the Doppler?</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@300;400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#faf9f7; --panel:#ffffff; --ink:#16191b; --body:#33393b;
  --muted:#5c6669; --line:#e2e6e5; --line-soft:#eef1f0;
  --accent:#0e6a66; --accent-soft:#e4efee;
  --caution:#a8531c; --caution-soft:#f7ece3;
  --good:#2f6b4f;
  --shadow:0 1px 2px rgba(20,30,30,.05), 0 8px 24px -16px rgba(20,30,30,.25);
}
:root:not([data-theme="light"]){ }
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#121516; --panel:#181c1d; --ink:#eceeed; --body:#c4cac9;
    --muted:#8d9695; --line:#2a2f30; --line-soft:#212626;
    --accent:#4fb3ac; --accent-soft:#12302e;
    --caution:#d98a52; --caution-soft:#2d211a;
    --good:#6fb894;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.8);
  }
}
:root[data-theme="dark"]{
  --ground:#121516; --panel:#181c1d; --ink:#eceeed; --body:#c4cac9;
  --muted:#8d9695; --line:#2a2f30; --line-soft:#212626;
  --accent:#4fb3ac; --accent-soft:#12302e;
  --caution:#d98a52; --caution-soft:#2d211a;
  --good:#6fb894;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.8);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--body);
  font:400 17px/1.65 "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:920px; margin:0 auto; padding:0 24px 96px}
h1,h2,h3{color:var(--ink); text-wrap:balance; margin:0}
h1{font:600 clamp(31px,5.2vw,50px)/1.1 Spectral, Georgia, serif; letter-spacing:-.015em}
h2{font:600 clamp(21px,3vw,27px)/1.25 Spectral, Georgia, serif; letter-spacing:-.008em}
h3{font:600 17px/1.35 "Source Sans 3", sans-serif}
p{margin:0}
a{color:var(--accent)}

.eyebrow{
  font:500 11.5px/1 "IBM Plex Mono", ui-monospace, monospace;
  letter-spacing:.14em; text-transform:uppercase; color:var(--muted);
}

/* masthead */
header{padding:72px 0 40px; border-bottom:1px solid var(--line)}
.head-inner{display:flex; flex-direction:column; gap:20px}
.lede{font:300 clamp(18px,2.3vw,21px)/1.55 "Source Sans 3",sans-serif;
  color:var(--body); max-width:60ch}
.sub-id{display:flex; flex-wrap:wrap; gap:8px 20px; color:var(--muted);
  font-size:14px}
.sub-id span{display:inline-flex; gap:7px; align-items:baseline}
.sub-id b{color:var(--ink); font-weight:600;
  font-family:"IBM Plex Mono",monospace; font-size:13px}

/* stat band */
.stats{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:1px; background:var(--line); border:1px solid var(--line);
  border-radius:3px; overflow:hidden; margin:36px 0 0}
.stat{background:var(--panel); padding:18px 18px 16px}
.stat .v{font:500 27px/1 "IBM Plex Mono",monospace; color:var(--ink);
  font-variant-numeric:tabular-nums; letter-spacing:-.02em}
.stat .k{font-size:13.5px; color:var(--muted); margin-top:7px; line-height:1.35}

section{padding:52px 0 0}
.section-head{display:flex; flex-direction:column; gap:9px; margin-bottom:22px}
.prose{display:flex; flex-direction:column; gap:16px; max-width:66ch}

/* the decisive finding */
.decisive{
  background:var(--accent-soft); border:1px solid var(--accent);
  border-radius:4px; padding:26px 28px; margin-top:26px;
  display:flex; flex-direction:column; gap:14px;
}
.decisive .verdict{font:600 20px/1.3 Spectral,Georgia,serif; color:var(--ink)}
.decisive p{max-width:64ch}

figure{margin:26px 0 0; display:flex; flex-direction:column; gap:11px}
figure img{width:100%; height:auto; display:block; border:1px solid var(--line);
  border-radius:3px; background:#fff}
figcaption{font-size:14px; color:var(--muted); line-height:1.5; max-width:70ch}
figcaption b{color:var(--ink); font-weight:600}

/* tables */
.scroll{overflow-x:auto; margin-top:20px; border:1px solid var(--line);
  border-radius:3px; background:var(--panel)}
table{width:100%; border-collapse:collapse; font-size:14.5px}
th,td{padding:10px 14px; text-align:left; border-bottom:1px solid var(--line-soft)}
thead th{font:500 11.5px/1 "IBM Plex Mono",monospace; letter-spacing:.09em;
  text-transform:uppercase; color:var(--muted); white-space:nowrap;
  border-bottom:1px solid var(--line)}
tbody tr:last-child td{border-bottom:none}
td.n,th.n{text-align:right; font-family:"IBM Plex Mono",monospace;
  font-variant-numeric:tabular-nums; white-space:nowrap}
td.lbl{color:var(--ink)}

.pill{display:inline-block; padding:2px 9px; border-radius:11px;
  font:500 11.5px/1.6 "IBM Plex Mono",monospace; letter-spacing:.04em;
  white-space:nowrap}
.pill.met{background:var(--accent-soft); color:var(--accent);
  border:1px solid var(--accent)}
.pill.miss{background:var(--caution-soft); color:var(--caution);
  border:1px solid var(--caution)}

/* risk band bars */
.bar-cell{min-width:150px}
.bar{height:7px; border-radius:4px; background:var(--line);
  overflow:hidden; margin-top:5px}
.bar i{display:block; height:100%; background:var(--accent)}

/* points card */
.card{background:var(--panel); border:1px solid var(--line);
  border-radius:4px; padding:24px 26px; margin-top:22px; box-shadow:var(--shadow)}
.pts{display:grid; grid-template-columns:1fr auto; gap:11px 18px;
  font-size:15.5px; margin-top:4px}
.pts .row{display:contents}
.pts dt{color:var(--body)}
.pts dd{margin:0; font:500 15px/1.5 "IBM Plex Mono",monospace;
  color:var(--ink); text-align:right; font-variant-numeric:tabular-nums}
.pts .zero dt,.pts .zero dd{color:var(--muted)}

.two{display:grid; grid-template-columns:1fr 1fr; gap:26px; margin-top:24px}
@media (max-width:720px){ .two{grid-template-columns:1fr} }

.note{border-left:2px solid var(--caution); padding:2px 0 2px 18px;
  margin-top:22px; color:var(--body); max-width:64ch}
.note strong{color:var(--ink)}

ol.traps{margin:20px 0 0; padding:0; list-style:none; counter-reset:t;
  display:flex; flex-direction:column; gap:14px}
ol.traps li{counter-increment:t; display:grid;
  grid-template-columns:28px 1fr; gap:14px; align-items:start}
ol.traps li::before{content:counter(t); font:500 12px/1.7
  "IBM Plex Mono",monospace; color:var(--muted); text-align:right}
ol.traps b{color:var(--ink); font-weight:600}
ol.traps code{font:400 13.5px/1 "IBM Plex Mono",monospace;
  background:var(--line-soft); padding:1px 5px; border-radius:2px;
  color:var(--ink)}

footer{margin-top:64px; padding-top:26px; border-top:1px solid var(--line);
  color:var(--muted); font-size:14px; display:flex; flex-direction:column; gap:9px}
</style>"""

BODY = """
<div class="wrap">

<header>
  <div class="head-inner">
    <p class="eyebrow">Derivation &amp; internal validation &middot; NHANES 1999&ndash;2004</p>
    <h1>Which feet deserve the Doppler?</h1>
    <p class="lede">Where a clinic can only examine some feet today, the order
    of the queue is a clinical decision currently made by a rule that finds
    barely more disease than picking at random.</p>
    <div class="sub-id">
      <span>Cohort <b>8,080</b></span>
      <span>Events <b>1,813</b></span>
      <span>Follow-up <b>16.2 y</b></span>
      <span>Imputations <b>m=20</b></span>
      <span>Bootstrap <b>1,000</b></span>
    </div>
  </div>

  <div class="stats">
    <div class="stat"><div class="v">+48%</div>
      <div class="k">More cases found than the<br>diabetes rule, same capacity</div></div>
    <div class="stat"><div class="v">2&times;</div>
      <div class="k">Capacity that rule needs<br>to catch up</div></div>
    <div class="stat"><div class="v">0.506</div>
      <div class="k">AUC of asking the patient<br>about leg pain</div></div>
    <div class="stat"><div class="v">88%</div>
      <div class="k">Of cases report<br>no symptoms at all</div></div>
  </div>
</header>

<section>
  <div class="section-head">
    <p class="eyebrow">The question a clinic actually asks</p>
    <h2>We can examine twenty feet today. Whose?</h2>
  </div>
  <div class="prose">
    <p>A decision curve prices a false positive against a true positive at an
    abstract exchange rate. A health centre faces something harder: a ceiling
    set by the morning&rsquo;s staffing. So we ranked every attendee by each
    strategy, examined the top slice, and counted what was found.</p>
  </div>

  <div class="decisive">
    <p class="verdict">At a 20% ceiling the score finds 636 cases. The
    diabetes rule finds 428.</p>
    <p>That is <b>208 more cases from the same 1,373 examinations</b> &mdash; a
    48% increase. Put the other way, the diabetes rule needs <b>40% capacity,
    double,</b> to find what the score finds at 20%. Efficiency: 46.3 against
    31.2 cases per 100 examinations.</p>
  </div>

  <figure>
    <img alt="Cumulative gain curves showing the share of all lower-extremity disease found against the share of attendees examined, for the triage score, the Zhang 2016 model, the diabetes rule, the age 60+ rule and an unordered queue." src="data:image/png;base64,__CAP__">
    <figcaption><b>Figure 1. What each strategy finds under a ceiling.</b>
    Every strategy ranks the same people. Ties inside a binary rule are broken
    at random and averaged &mdash; crediting &ldquo;test everyone with
    diabetes&rdquo; with an ordering it does not have would flatter it.</figcaption>
  </figure>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">The result that changed our claim</p>
    <h2>A published model beats the heuristic too</h2>
  </div>
  <div class="prose">
    <p>We refitted the closest published competitor &mdash; Zhang 2016, same
    survey, overlapping cycles &mdash; on our own participants rather than
    comparing numbers across different samples. It found <b>607 cases</b> at
    the same 20% ceiling, close behind ours, and beat the diabetes rule at
    every threshold, exactly as ours did.</p>
    <p>We could have left that out. Reporting it makes the paper's claim
    better, not worse: <b>the evidence supports abandoning diabetes status as
    the triage rule, and does not depend on adopting our replacement.</b> A
    clinic that prefers an existing model should use it.</p>
  </div>
  <div class="scroll">
    <table>
      <thead><tr><th></th><th>Zhang 2016</th><th>Triage score</th></tr></thead>
      <tbody>
        <tr><td class="lbl">AUC, PAD alone</td><td class="n">0.790</td><td class="n">0.797</td></tr>
        <tr><td class="lbl">AUC, composite endpoint</td><td class="n">0.722</td><td class="n">0.737</td></tr>
        <tr><td class="lbl">Cases at 20% capacity</td><td class="n">607</td><td class="n">636</td></tr>
        <tr><td class="lbl">Beats the diabetes rule</td><td class="n">12/12</td><td class="n">12/12</td></tr>
        <tr><td class="lbl">Needs a laboratory</td><td>Yes &mdash; cholesterol, HDL</td><td>No</td></tr>
        <tr><td class="lbl">Contains US race terms</td><td>Yes &mdash; 3 of 8 terms</td><td>No</td></tr>
        <tr><td class="lbl">Captures neuropathy</td><td>No</td><td>Yes</td></tr>
        <tr><td class="lbl">Deployable form</td><td>logit, intercept &minus;9.37</td><td>integer 0&ndash;18</td></tr>
      </tbody>
    </table>
  </div>
  <div class="note">
    <strong>Discrimination is close enough that it is not the point.</strong>
    What separates the models is what each can be used for. <b>67.7% of cases
    here are neuropathy without PAD</b> &mdash; structurally invisible to a
    PAD-only endpoint at any threshold, however good its AUC.
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Testing our own premise</p>
    <h2>Asking the patient is a coin flip</h2>
  </div>
  <div class="prose">
    <p>Every paper in this literature opens by asserting that symptom-driven
    case finding fails, and supports it with a citation. We tested it in the
    same participants.</p>
  </div>
  <div class="two">
    <div class="card">
      <h3>The symptom item alone</h3>
      <p style="margin-top:9px">AUC <b>0.506</b>. Prevalence is 23.7% among
      those reporting leg pain and 21.5% among those not &mdash; a gap of 2.2
      percentage points. <b>88.1% of all cases report no leg pain.</b></p>
    </div>
    <div class="card">
      <h3>At the same examination burden</h3>
      <p style="margin-top:9px">Examining 10.9% of attendees by symptoms finds
      <b>87</b> cases. Examining the same number by score finds <b>201</b>
      &mdash; a 131% increase. Score discrimination among the symptomless is
      <b>0.755</b>, higher than overall.</p>
    </div>
  </div>
  <div class="prose" style="margin-top:20px">
    <p>Any workflow that waits for a complaint, or uses one to prioritise, is
    close to selecting at random.</p>
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Prespecified targets</p>
    <h2>Six met, one missed</h2>
  </div>
  <div class="scroll">
    <table>
      <thead><tr><th>Target, set before analysis</th><th>Result</th>
        <th>Status</th></tr></thead>
      <tbody>
        <tr><td class="lbl">AUC &ge;0.72, composite endpoint</td>
          <td class="n">0.739</td><td><span class="pill met">met</span></td></tr>
        <tr><td class="lbl">CI lower bound not crossing 0.68</td>
          <td class="n">0.727</td><td><span class="pill met">met</span></td></tr>
        <tr><td class="lbl">Calibration slope 0.85&ndash;1.15</td>
          <td class="n">0.986</td><td><span class="pill met">met</span></td></tr>
        <tr><td class="lbl">Sensitivity &ge;0.85 at chosen threshold</td>
          <td class="n">0.88</td><td><span class="pill met">met</span></td></tr>
        <tr><td class="lbl">Net benefit above the diabetes heuristic</td>
          <td class="n">23/23</td><td><span class="pill met">met</span></td></tr>
        <tr><td class="lbl">Cardiovascular mortality gradient across bands</td>
          <td class="n">27&times;</td><td><span class="pill met">met</span></td></tr>
        <tr><td class="lbl">Examination burden &le;40% at that sensitivity</td>
          <td class="n">65.7%</td><td><span class="pill miss">not met</span></td></tr>
      </tbody>
    </table>
  </div>

  <div class="note">
    <strong>The one we missed matters.</strong> Reaching 85% sensitivity costs
    a 65.7% examination burden &mdash; there is no threshold where both targets
    hold. A clinic willing to examine two-thirds of its attendees does not have
    much of a capacity problem to begin with. The honest reading: the score
    reorders the queue well, but does not shorten it as much as we intended. A
    service adopting it should pick its own point on that trade-off &mdash;
    perhaps 40% burden at 68% sensitivity &mdash; rather than inherit ours.
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Deliverable</p>
    <h2>The card that goes on the wall</h2>
  </div>
  <div class="two">
    <div class="card">
      <h3>Version A &mdash; no laboratory</h3>
      <dl class="pts">
        <div class="row"><dt>Start at</dt><dd>2</dd></div>
        <div class="row"><dt>Age, per 10 years over 40</dt><dd>+2</dd></div>
        <div class="row"><dt>Currently smoking</dt><dd>+2</dd></div>
        <div class="row"><dt>Waist, per 15 cm over 70</dt><dd>+1</dd></div>
        <div class="row"><dt>Diabetes, per duration band</dt><dd>+1</dd></div>
        <div class="row"><dt>Known heart disease or stroke</dt><dd>+1</dd></div>
        <div class="row"><dt>Female sex</dt><dd>&minus;1</dd></div>
        <div class="row zero"><dt>Systolic pressure</dt><dd>0</dd></div>
        <div class="row zero"><dt>Former smoker</dt><dd>0</dd></div>
        <div class="row zero"><dt>On antihypertensives</dt><dd>0</dd></div>
      </dl>
    </div>
    <div class="card">
      <h3>Observed risk by band</h3>
      <div class="scroll" style="margin-top:14px;border:none">
      <table>
        <thead><tr><th>Score</th><th class="n">n</th>
          <th class="bar-cell">Risk</th></tr></thead>
        <tbody>
          <tr><td class="n">&le;4</td><td class="n">1,117</td>
            <td class="bar-cell"><b>5.6%</b><div class="bar"><i style="width:13%"></i></div></td></tr>
          <tr><td class="n">5&ndash;6</td><td class="n">1,430</td>
            <td class="bar-cell"><b>9.5%</b><div class="bar"><i style="width:22%"></i></div></td></tr>
          <tr><td class="n">7&ndash;8</td><td class="n">1,613</td>
            <td class="bar-cell"><b>15.2%</b><div class="bar"><i style="width:36%"></i></div></td></tr>
          <tr><td class="n">9&ndash;10</td><td class="n">1,666</td>
            <td class="bar-cell"><b>24.9%</b><div class="bar"><i style="width:59%"></i></div></td></tr>
          <tr><td class="n">&ge;11</td><td class="n">2,254</td>
            <td class="bar-cell"><b>42.3%</b><div class="bar"><i style="width:100%"></i></div></td></tr>
        </tbody>
      </table>
      </div>
    </div>
  </div>
  <div class="prose" style="margin-top:20px">
    <p>Rounding to whole points costs 0.010 of AUC (0.729 against 0.739). The
    score runs 0&ndash;18 and takes under three minutes with a tape measure and
    four questions.</p>
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Reported as found</p>
    <h2>Two results that argue against our own model</h2>
  </div>
  <div class="two">
    <div class="card">
      <h3>A laboratory adds nothing</h3>
      <p style="margin-top:9px">Version B adds HbA1c and eGFR. It moves the AUC
      by <b>0.001</b> &mdash; 0.740 against 0.739. Where a health centre must
      choose between a phlebotomy pathway and a tape measure, these data
      support the tape measure.</p>
    </div>
    <div class="card">
      <h3>Gradient boosting is worse</h3>
      <p style="margin-top:9px">On identical predictors, boosting scores
      <b>0.725</b> against the spline logistic model's 0.739. With 1,813 events
      and nine well-understood variables there is little non-linear structure
      to find, and a flexible learner pays variance for looking.</p>
    </div>
  </div>
  <div class="prose" style="margin-top:20px">
    <p>Both are reported because the alternative &mdash; quietly dropping the
    benchmark that disappointed &mdash; is how the impression arises that
    flexible methods always win.</p>
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Prognostic anchor</p>
    <h2>Not just predicting a test result</h2>
  </div>
  <div class="prose">
    <p>Linked to death records through 31 December 2019: 3,335 deaths, 1,085
    cardiovascular, over a median 16.2 years. Cardiovascular mortality rises
    from <b>1.1</b> to <b>29.5</b> per 1,000 person-years across score bands.
    Adjusted for age and sex, the hazard ratio per point remains
    <b>1.238</b> (95% CI 1.197&ndash;1.280) &mdash; the gradient is not age
    reappearing under another name.</p>
  </div>
  <figure>
    <img alt="Kaplan-Meier survival curves by score band for all-cause and cardiovascular mortality, showing progressively steeper decline in higher score bands over twenty years." src="data:image/png;base64,__SURV__">
    <figcaption><b>Survival by score band.</b> The score marks people at
    materially higher risk of dying, and of dying of vascular causes &mdash;
    not merely people likely to fail a Doppler today.</figcaption>
  </figure>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Endpoints</p>
    <h2>Not an artefact of one definition</h2>
  </div>
  <div class="scroll">
    <table>
      <thead><tr><th>Endpoint</th><th class="n">n</th><th class="n">Events</th>
        <th class="n">AUC</th></tr></thead>
      <tbody>
        <tr><td class="lbl">Composite lower-extremity disease <em>(primary)</em></td>
          <td class="n">8,080</td><td class="n">1,813</td><td class="n">0.739</td></tr>
        <tr><td class="lbl">PAD alone (ABI &lt;0.90)</td>
          <td class="n">7,477</td><td class="n">586</td><td class="n">0.791</td></tr>
        <tr><td class="lbl">Neuropathy alone</td>
          <td class="n">7,906</td><td class="n">1,381</td><td class="n">0.727</td></tr>
        <tr><td class="lbl">High-risk foot (both present)</td>
          <td class="n">7,303</td><td class="n">154</td><td class="n">0.831</td></tr>
        <tr><td class="lbl">Abnormal ABI, incl. incompressible &gt;1.40</td>
          <td class="n">7,539</td><td class="n">785</td><td class="n">0.766</td></tr>
        <tr><td class="lbl">Neuropathy, &ge;2 insensate sites</td>
          <td class="n">7,906</td><td class="n">523</td><td class="n">0.740</td></tr>
        <tr><td class="lbl">Neuropathy, &ge;1 site on both feet</td>
          <td class="n">7,762</td><td class="n">489</td><td class="n">0.735</td></tr>
      </tbody>
    </table>
  </div>
  <div class="prose" style="margin-top:18px">
    <p>The score performs <em>better</em> for PAD alone than for the composite,
    and best of all for the high-risk foot with both conditions present. It is
    not merely a neuropathy detector, and no alternative neuropathy definition
    changes the conclusion.</p>
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Data integrity</p>
    <h2>Nine ways this could have failed silently</h2>
  </div>
  <div class="prose">
    <p>A verification gate reproduces the published 2003&ndash;2004 codebook
    frequencies exactly &mdash; every level of <code>LEALPN</code> and
    <code>LEARPN</code> including the &minus;1 code, and both ABPI
    present/missing splits &mdash; before any analysis is permitted to run. It
    earned its keep twice. Four traps were known in advance; five were found
    only by checking the delivered files against their own codebooks. The three
    that would have been hardest to notice:</p>
  </div>
  <ol class="traps">
    <li><div><b>A flag masquerading as an age.</b> <code>DID040G</code> takes
      values 1, 2, 7, 9 &mdash; it records <em>whether</em> an age at diabetes
      diagnosis was given. The age itself is <code>DID040Q</code>. Read the
      flag as an age and every diabetic diagnosis lands at age 1, turning
      diabetes duration into a near-constant fifty years: a strong, entirely
      artefactual predictor, with nothing to signal anything went wrong.</div></li>
    <li><div><b>Zero that isn't zero.</b> A SAS XPORT numeric zero decodes to
      <code>5.397605e-79</code>. It never raises, and it doesn't even change
      the endpoint &mdash; but it fails every equality test, which is how 2,269
      genuine zeros came to match no expected level.</div></li>
    <li><div><b>An interstitial that passes every size check.</b> The first
      fetch reported 38 successful downloads. All were 0.0 MB and all shared
      one SHA-256: CDC had served an HTML page, comfortably larger than any
      plausible size threshold. Files are now accepted only if they open with
      the XPORT library header record.</div></li>
  </ol>
  <div class="prose" style="margin-top:20px">
    <p>The remaining six &mdash; the &minus;1 insensate code, non-random
    missingness from incompressible arteries, creatinine renamed mid-study,
    protocol-absent second readings, mortality fields at unexpected offsets,
    and six-year survey weights &mdash; are documented in full alongside the
    code.</p>
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Model performance</p>
    <h2>Discrimination and calibration</h2>
  </div>
  <div class="two">
    <figure style="margin-top:0">
      <img alt="Receiver operating characteristic curves for Version A, Version B and the gradient boosting benchmark, all closely overlapping." src="data:image/png;base64,__ROC__">
      <figcaption>Version A and Version B are indistinguishable; boosting sits
      below both.</figcaption>
    </figure>
    <figure style="margin-top:0">
      <img alt="Calibration plot by deciles of predicted risk, with observed proportions closely following the diagonal." src="data:image/png;base64,__CAL__">
      <figcaption>Decile calibration. Slope 0.986, calibration-in-the-large
      0.000; optimism was 0.0024.</figcaption>
    </figure>
  </div>
</section>

<section>
  <div class="section-head">
    <p class="eyebrow">Standing</p>
    <h2>What this does and does not claim</h2>
  </div>
  <div class="prose">
    <p>This is internal validation in US data from 1999&ndash;2004. The
    optimism correction was small and calibration near-perfect, but a bootstrap
    cannot substitute for a new population, and external validation in the
    setting the score is designed for is required before deployment.</p>
    <p>Participants with bilateral amputation or weighing over 400 lb were
    excluded from examination by survey protocol and never enter the data. The
    highest-risk group is absent, and every prevalence here is a lower bound.</p>
    <p>The USPSTF concluded in 2018 that evidence is insufficient to recommend
    ABI screening in asymptomatic adults. That concerns whether to screen a
    population where the alternative is doing nothing. The question here is
    different: given a clinic that will examine <em>some</em> patients today,
    which ones? Allocating scarce capacity is not the same decision as creating
    a screening programme.</p>
  </div>
</section>

<footer>
  <p>Derived in NHANES 1999&ndash;2004, the only cycles in which the Lower
  Extremity Disease component was fielded. Reporting follows TRIPOD+AI.
  All data are public; code, the SHA-256 manifest of every file used, and the
  verification gate are in the repository.</p>
  <p>Primary endpoint: ABI &lt;0.90 in either leg <em>or</em> &ge;1 insensate
  site on 10 g monofilament testing. Thresholds fixed before the data were
  examined.</p>
</footer>

</div>
"""

html = HEAD + BODY
for key, tok in [("dca","__DCA__"),("surv","__SURV__"),("roc","__ROC__"),
                 ("cal","__CAL__"),("cap","__CAP__")]:
    html = html.replace(tok, figs[key])

open("/tmp/claude-0/-home-user-Who-5os/731e32d0-c6af-5670-ae4f-02f43eba3ec4/scratchpad/doppler-findings.html","w",encoding="utf-8").write(html)
print("written", len(html)//1024, "KB")
