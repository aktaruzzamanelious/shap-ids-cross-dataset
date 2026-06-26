# SHAP-Based Explainable Intrusion Detection: A Cross-Dataset Study

A cross-dataset comparison of lightweight classifiers for IoT and ransomware
traffic detection, with SHAP-based explainability and an SOC-workload
translation of false-alert rates.

## Author

Aktaruzzaman Elious
University of the West of Scotland
ORCID: 0009-0009-6143-5183

## Paper

Manuscript in preparation. Target journal: MDPI *Sensors*.

## Datasets

- **UGRansome2024** (Azugo, Venter, Nkongolo 2024) — ransomware network traffic
- **CICIoT2023** (Neto et al. 2023) — IoT attack traffic

Both are publicly available. Raw data is **not** shipped here; see
[`data/README.md`](data/README.md) for URLs, access dates, and a download helper.

## Reproducing the results

1. Clone this repository.
2. Create a Python 3.12 virtual environment.
3. `pip install -r requirements.txt`
4. Download the datasets per [`data/README.md`](data/README.md).
5. Run the notebooks in numerical order, `01` → `12`.

All results CSVs, the 8 trained models, the SHAP interaction array, and the 18
publication figures are included so the manuscript numbers can be inspected and
verified without re-running the full pipeline.

## Notebook → canonical artifact map

Definitive mapping of each of the 13 canonical result CSVs to the notebook that
produces it, derived by reading every notebook's output-write paths (the
notebooks were **not** re-run). 11 of the 13 are written directly under the same
name; the remaining 4 (the two `[†]` rows below) are derived by splitting a
single combined file that the notebook writes.

| # | Canonical CSV (in `results/`) | Written by | Name as written by the notebook | Feeds (manuscript) |
|---|---|---|---|---|
| 1 | `master_results_all.csv` | `04_multimodel_comparison.ipynb` | `results/master_results_all.csv` (direct) | Tables 1, 2, 3 |
| 2 | `metrics_with_ci_ugr.csv` [†] | `09_bootstrap_ci.ipynb` | `results/bootstrap_ci.csv`, rows `dataset == UGRansome2024` | Table 6 + Sec 4.5 |
| 3 | `metrics_with_ci_cic.csv` [†] | `09_bootstrap_ci.ipynb` | `results/bootstrap_ci.csv`, rows `dataset == CICIoT2023` | Table 6 + Sec 4.5 |
| 4 | `rf_seed_robustness.csv` | `06_statistical_tests.ipynb` | `results/rf_seed_robustness.csv` (direct) | Table 4; seed-robustness figure |
| 5 | `mcnemar_results.csv` | `06_statistical_tests.ipynb` | `results/mcnemar_results.csv` (direct) | Table 5 |
| 6 | `ablation_ugransome_tier_a.csv` [†] | `08_ablation.ipynb` | `results/ablation_ugr.csv`, row `tier == A_raw_flow_only` | Table 7; feature-ablation figure |
| 7 | `ablation_ugransome_tier_b.csv` [†] | `08_ablation.ipynb` | `results/ablation_ugr.csv`, rows `tier in {B1,B2,B3,B4}` | Table 7; feature-ablation figure |
| 8 | `spearman_correlations.csv` | `10_shap_best_permutation.ipynb` | `results/spearman_correlations.csv` (direct) | Table 8 |
| 9 | `shap_vs_gini_permutation_cic.csv` | `10_shap_best_permutation.ipynb` | `results/shap_vs_gini_permutation_cic.csv` (direct) | Table 9 |
| 10 | `shap_vs_gini_permutation_ugr.csv` | `10_shap_best_permutation.ipynb` | `results/shap_vs_gini_permutation_ugr.csv` (direct) | Table 10 |
| 11 | `per_category_recall_cic.csv` | `12_per_category_recall.ipynb` | `results/per_category_recall_cic.csv` (direct) | Table 11; per-category recall heatmap |
| 12 | `efficiency_table.csv` | `11_efficiency.ipynb` | `results/efficiency_table.csv` (direct) | Table 12; **Figure 17** (`figures/efficiency.{png,pdf}`) |
| 13 | `soc_workload.csv` | `07_soc_workload.ipynb` | `results/soc_workload.csv` (direct) | Tables 13, 14; **Figure 18** (`figures/soc_workload.{png,pdf}`) |

[†] **Split note.** The notebooks as committed write two *combined* files:
`08_ablation.ipynb` writes `results/ablation_ugr.csv` (one file holding the Tier A
row plus the four Tier B rows), and `09_bootstrap_ci.ipynb` writes
`results/bootstrap_ci.csv` (one file holding both datasets). The shipped
canonical files are these split by row — `ablation_ugransome_tier_a.csv` is the
single `A_raw_flow_only` row, `ablation_ugransome_tier_b.csv` is the four
`B1`–`B4` rows, and `metrics_with_ci_{ugr,cic}.csv` are the per-dataset subsets.
All four carry the same columns as the combined file and are the
manuscript-canonical versions verified by `verify_canonical_artifacts.py`.

The split was originally a one-off manual step (it is not a committed notebook
cell). To let a reviewer reproduce the four canonical filenames from the
combined files, run `split_canonical_csvs.py` at the repository root. The full
reproduction order is:

1. Run `notebooks/08_ablation.ipynb` → writes `results/ablation_ugr.csv`
2. Run `notebooks/09_bootstrap_ci.ipynb` → writes `results/bootstrap_ci.csv`
3. Run `python3 split_canonical_csvs.py`, which produces:
   - `results/ablation_ugr.csv` → `ablation_ugransome_tier_a.csv` (Tier A row)
     and `ablation_ugransome_tier_b.csv` (the four B1–B4 rows)
   - `results/bootstrap_ci.csv` → `metrics_with_ci_ugr.csv` (UGRansome2024 rows)
     and `metrics_with_ci_cic.csv` (CICIoT2023 rows)

```
python3 split_canonical_csvs.py
```

The split copies the header and matching data lines verbatim, so the output is
byte-identical to the committed canonical files (same sha256 the gate checks).
If the combined inputs are absent, the script reports which files are missing
and tells you to run notebooks 08/09 first.

### Supporting artifacts (not in the 13 canonical CSVs)

| Notebook | Produces | Used for |
|---|---|---|
| `01_data_cleaning.ipynb` | `data/processed/ugr_clean.csv` | preprocessing |
| `02_preprocessing.ipynb` | `data/processed/{ugr,cic}_{train,test}.csv` | preprocessing |
| `03_baselines.ipynb` | `results/baselines/baseline_metrics.csv`, `results/baselines/rules.json` | Sec 4.1 rule baseline (UGR macro-F1 0.6274 / CIC 0.5986) |
| `04_multimodel_comparison.ipynb` | `results/models/*.joblib` (8 models) | trained models |
| `05_shap_v5.ipynb` | `figures/shap_bar_rf_{ugr,cic}`, `figures/shap_beeswarm_rf_{ugr,cic}` | RF SHAP importance figures |
| `10_shap_best_permutation.ipynb` | `results/top_interactions_ugr_xgb.csv`, `results/shap_interaction_ugr_xgb.npy` | Sec 4.7 SHAP interactions |
| `11_efficiency.ipynb` | `results/cpu_info.json`, `results/raw_efficiency_timings.json` | Sec 3.8 timing environment |

### Figures 17 and 18 (regenerated from the canonical CSVs)

**Figure 17** (`figures/efficiency.{png,pdf}`) and **Figure 18**
(`figures/soc_workload.{png,pdf}`) are not written by the notebooks; they are
produced by `make_corrected_figs.py` at the repository root, which reads
`results/efficiency_table.csv` (Figure 17) and `results/soc_workload.csv`
(Figure 18) and writes both the 600 DPI PNG and a true vector PDF for each.
Run from the repository root:

```
python3 make_corrected_figs.py
```

## Repository structure

```
notebooks/   12 Jupyter notebooks (data cleaning -> final experiments), run 01..12
results/     13 canonical result CSVs + supporting JSON, SHAP interaction array,
             baselines/ (metrics + rule thresholds), and models/ (8 trained .joblib)
figures/     18 publication figures at 600 DPI, each with a PNG and a PDF (36 files)
data/        Download instructions + helper script (no raw data shipped)
audit/       SHAP interaction note
make_corrected_figs.py   regenerates Figure 17 (efficiency.*) and Figure 18
                         (soc_workload.*) from the canonical results/ CSVs
split_canonical_csvs.py  splits the two combined CSVs the notebooks write
                         (ablation_ugr.csv, bootstrap_ci.csv) into the four
                         canonical per-tier / per-dataset files
```

The pipeline notebooks are self-contained and import no local helper module.

## License

MIT — see [`LICENSE`](LICENSE).

## Citation

If you use this work, please cite the published article (citation to be added
after publication).
