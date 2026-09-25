#!/usr/bin/env python3
"""Illustrative causal sandbox. Synthetic data only; parameters are assumptions, not estimates."""
import csv
from pathlib import Path
import numpy as np

SEED = 20260925
N = 200_000
rng = np.random.default_rng(SEED)
OUT = Path(__file__).resolve().parent / 'sandbox_results'
OUT.mkdir(exist_ok=True)

# DAG: background adversity C -> T,B,D,Y and placebo Z; T,B,D -> Y;
# hazard H -> Y; solidarity S -> Y conditional on H; factor interactions -> Y.
# Outcomes and labels are deliberately narrow and hypothetical.
def risk(c, t, b, d, h, s):
    hazard = (h > 0).astype(float) if isinstance(h, np.ndarray) else float(h > 0)
    return (0.08 + .06*c + .08*t + .06*b + .02*d
            + .02*t*b + .01*t*d + .01*b*d + .01*t*b*d
            + .10*(h == 1) + .14*(h == 2)
            + .01*hazard*(t+b+d) - .04*hazard*s)

def corr(x, y):
    return float(np.corrcoef(x, y)[0, 1])

def se_risk(p, n):
    return float(np.sqrt(p*(1-p)/n))

# In the observational sample, background adversity raises exposures and risk.
c = rng.binomial(1, .35, N)
t = rng.binomial(1, .15 + .40*c)
b = rng.binomial(1, .25 + .35*c)
d = rng.binomial(1, .25 + .25*c)
z = rng.binomial(1, .12 + .64*c)  # negative-control marker: has NO effect on outcome
h = rng.choice(3, size=N, p=[.70, .18, .12])
s = rng.binomial(1, .60, N)
p = risk(c,t,b,d,h,s)
assert np.min(p) >= 0 and np.max(p) <= 1
u = rng.random(N)
y = (u < p).astype(int)
observed = {name: corr(v,y) for name,v in [('background C',c),('trauma vulnerability T',t),('bias B',b),('dissonance D',d),('placebo Z',z),('natural event', (h==1).astype(int)),('human-caused event',(h==2).astype(int))]}

# Controlled experiments: same background population, set exposure by intervention,
# keep other factors OFF unless named. Shared random draw u gives paired outcomes.
def arm(t0=0,b0=0,d0=0,h0=0,s0=0):
    pp = risk(c,t0,b0,d0,h0,s0)
    return float(np.mean(u<pp)), float(np.mean(pp))

arms = {}
for hh,hl in [(0,'ordinary'),(1,'natural disaster'),(2,'human-caused disaster')]:
    for tt in (0,1):
        for bb in (0,1):
            for dd in (0,1):
                for ss in ((0,1) if hh else (0,)):
                    arms[(hh,tt,bb,dd,ss)] = arm(tt,bb,dd,hh,ss)

with (OUT/'factorial_scenarios.csv').open('w',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['hazard','trauma_vulnerability','cognitive_bias','dissonance','solidarity','observed_risk','structural_expected_risk','sample_n'])
    for (hh,tt,bb,dd,ss),(r,expect) in arms.items():
        writer.writerow([['ordinary','natural','human-caused'][hh],tt,bb,dd,ss,f'{r:.6f}',f'{expect:.6f}',N])

with (OUT/'observational_correlations.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['factor','Pearson_r_with_outcome','status'])
    for name,val in observed.items():
        writer.writerow([name,f'{val:.6f}','synthetic observational correlation'])

baseline=arms[(0,0,0,0,0)][0]
comparisons=[
 ('Trauma vulnerability only',arms[(0,1,0,0,0)][0]-baseline),
 ('Cognitive bias only',arms[(0,0,1,0,0)][0]-baseline),
 ('Dissonance only',arms[(0,0,0,1,0)][0]-baseline),
 ('All three combined',arms[(0,1,1,1,0)][0]-baseline),
 ('Natural disaster, factors off',arms[(1,0,0,0,0)][0]-baseline),
 ('Human-caused disaster, factors off',arms[(2,0,0,0,0)][0]-baseline),
 ('Solidarity during natural disaster',arms[(1,0,0,0,1)][0]-arms[(1,0,0,0,0)][0]),
 ('Solidarity during human-caused disaster',arms[(2,0,0,0,1)][0]-arms[(2,0,0,0,0)][0]),
 ('Placebo Z intervention',0.0),
]
# Model-level interaction estimand, measured by a difference of differences.
synergy=(arms[(0,1,1,1,0)][0]-baseline -sum(arms[x][0]-baseline for x in [(0,1,0,0,0),(0,0,1,0,0),(0,0,0,1,0)]))
with (OUT/'controlled_comparisons.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['controlled_contrast','absolute_risk_difference_percentage_points'])
    for name,diff in comparisons+[('Excess of all three over sum of separate effects',synergy)]:
        writer.writerow([name,f'{100*diff:.4f}'])

# Observational association for negative control illustrates confounding.
placebo_assoc=float(y[z==1].mean()-y[z==0].mean())
assert observed['placebo Z'] > 0 and abs(comparisons[-1][1]) < 1e-12
lines=['# Causal sandbox: synthetic data only','',
'**Purpose.** Show which comparisons can establish causation *inside a known simulation*, and why observational correlations alone cannot establish real-world causation. Outcome: one hypothetical avoidable defensive or harmful response under pressure.','',
'## Assumptions and design','',
'- 200,000 simulated individuals (seed 20260925); all probabilities and prevalence choices are hypothetical. They were not calibrated to any population or pooled across studies.',
'- Background C is present in 35%; it increases activation of trauma vulnerability T, bias B, dissonance D, and outcome risk. It also predicts a placebo marker Z that has no causal effect.',
'- Observational natural and human-caused hazards occur in 18% and 12% of simulated rows. Solidarity is active for 60% of rows, but protects only under a hazard.',
'- Controlled conditions intervene on T, B, D, hazard and solidarity in a 3 × 2 × 2 × 2 × (1 or 2) factorial grid (40 cells), using the same underlying population and shared outcome draws.',
'- Risk equation: 0.08 + 0.06 C + 0.08 T + 0.06 B + 0.02 D + 0.02 TB + 0.01 TD + 0.01 BD + 0.01 TBD + 0.10 natural + 0.14 human-caused + 0.01 hazard × (T+B+D) − 0.04 hazard × solidarity.',
'- The dissonance sign represents defensive rationalization. Real dissonance can also motivate positive behavioral change; changing that sign is a required sensitivity analysis before applying the framework to a specific outcome.','',
'## Controlled comparison results','',
f'Baseline, all factors and hazard off: **{baseline:.2%}** (background C remains distributed as in the simulated sample).','',
'| Intervention or contrast | Change in probability (percentage points) |','|---|---:|']
for name,diff in comparisons+[('Interaction: all three beyond sum',synergy)]:
    lines.append(f'| {name} | {100*diff:+.2f} |')
lines += ['',
'Each estimate above is a synthetic intervention contrast, so the model’s programmed direction is causal *within this simulator*. The placebo intervention is zero by construction.', '',
'## Observational correlation with the outcome','',
'| Variable | Pearson r |','|---|---:|']
for name,val in observed.items():lines.append(f'| {name} | {val:+.3f} |')
lines += ['',f'Placebo Z has a **{100*placebo_assoc:+.2f} percentage-point observational risk association**, despite **zero true causal effect**. It correlates because C causes both Z and the outcome. The other observed correlations likewise mix genuine effects with shared causes and interactions.','',
'## What this establishes','',
'1. When rules and assignments are known, interventions identify causal effects within the simulator; correlations do not automatically recover them.',
'2. Combined factors amplify the model outcome through the specified interaction terms. This amplification is an assumption, not a discovered real-world law.',
'3. Natural and human-caused disaster labels do not isolate the mechanism of a real event. Exposure severity, deprivation, response quality, trust, and social ties could confound any observed comparison.',
'4. No synthetic p-value, sample size, or narrow confidence interval validates an invented coefficient. This sandbox does **not** establish causation or the strength of correlation in humanity.', '',
'## Path to an empirical test','',
'- Pre-register a specific observable outcome, such as willingness to share verified evacuation information, and identify the target population.',
'- Randomize a bias-reduction prompt and a dissonance/values-consistency prompt where ethical; use a 2 × 2 design and measure actual behavior, with a no-prompt control. Randomization estimates effects of the prompts, not of bias or dissonance as whole constructs.',
'- Follow adversity measures prospectively where possible. Do not randomly impose trauma; use rich covariates, family comparisons and sensitivity analyses, while acknowledging unmeasured confounding.',
'- Study disasters using prospective baseline measures, variation in exposure and solidarity, and repeated outcomes. Do not randomize disasters. Compare like severity and resources; measure help-giving alongside harmful responses.',
'- Estimate risk differences, uncertainty intervals, factor interactions, and correlations; examine whether results replicate across contexts.','',
'## Research background (not used as numeric calibration)','',
'- Baldwin et al. (2025), *Nature Human Behaviour*, review of educational debiasing trials: https://doi.org/10.1038/s41562-025-02253-y',
'- Priolo et al. (2019), induced-hypocrisy meta-analysis: https://doi.org/10.1177/0146167219841621',
'- Maternal ACEs and offspring behavior cohort: https://pubmed.ncbi.nlm.nih.gov/40373311/',
'- Drury et al. (2016), solidarity after the Chile earthquake: https://doi.org/10.1002/ejsp.2146',
'', 'Run with: `python causal_sandbox.py` (requires NumPy).']
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[16:43]))
print('FILES:',*[str(p) for p in sorted(OUT.iterdir())],sep='\n')
