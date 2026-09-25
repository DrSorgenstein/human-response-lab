# Human Response Lab

A self-contained GitHub Pages site for a **synthetic** causal behavior sandbox. No build step, account, external scripts, or API key is needed. The site works offline when opened locally.

## Publish on GitHub Pages

1. Create a new public GitHub repository and upload the **contents of this folder** to its root, including `index.html`.
2. Open repository **Settings → Pages**. Under **Build and deployment**, select **Deploy from a branch**, then `main` and `/ (root)`; save.
3. GitHub will display the published URL. Site updates deploy when you commit edits to `main`.

## Update the analysis

- Edit `DEFAULTS` and `DEFINITIONS` in `app.js` for starting slider values and ranges. The user interface recalculates the model from those assumptions.
- Edit `sandbox/causal_sandbox.py` for the underlying synthetic experiment. Run `python sandbox/causal_sandbox.py` with NumPy installed. It writes fresh CSVs in `sandbox/sandbox_results/`; copy them into `data/` to replace the downloaded datasets.
- The observational table and placebo example in `index.html` are **fixed to the packaged run**. If you change the generator, update those displayed values from the regenerated files. Live sliders change causal scenarios only, not observational data.
- Edit `index.html` for explanatory text and source links; `styles.css` for styling.

## Model and interpretation

The default structural risk model uses `0.08 + 0.06 C + 0.08 T + 0.06 B + 0.02 D + 0.02 TB + 0.01 TD + 0.01 BD + 0.01 TBD + hazard terms − solidarity term`. The interface averages background C using the assumed 35% prevalence. It clips results to 0–100%. The Python file simulates individual outcomes with a fixed random seed, so its results fluctuate slightly around structural expectations.

**Limits:** Values are illustrative, not empirical estimates. Correlation does not imply causation. The programmed causal effects are causal only inside the synthetic data generator. Dissonance may motivate constructive change; the positive default coefficient is a scenario assumption.

## Files

- `index.html`, `styles.css`, `app.js`: static site.
- `data/`: 40 factorial scenarios, controlled comparisons, and observational correlations.
- `sandbox/causal_sandbox.py`: reproducible experiment. It writes its results relative to its own location.

## Research background

- [Debiasing educational interventions](https://doi.org/10.1038/s41562-025-02253-y)
- [Induced-hypocrisy meta-analysis](https://doi.org/10.1177/0146167219841621)
- [Maternal ACEs and offspring behavior](https://pubmed.ncbi.nlm.nih.gov/40373311/)
- [Solidarity after the 2010 Chile earthquake](https://doi.org/10.1002/ejsp.2146)
