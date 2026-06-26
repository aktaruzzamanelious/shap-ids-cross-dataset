#!/usr/bin/env python3
"""
make_corrected_figs.py -- regenerate Figure 17 (efficiency) and Figure 18
(SOC workload) for the MDPI Sensors paper directly from the canonical CSVs.

Run from the repository root:
    python3 make_corrected_figs.py

Reads:
    results/efficiency_table.csv
    results/soc_workload.csv
Writes (600 DPI PNG + true vector PDF):
    figures/efficiency.png    figures/efficiency.pdf     (Figure 17)
    figures/soc_workload.png  figures/soc_workload.pdf   (Figure 18)
"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RESULTS = os.environ.get("RESULTS_DIR", "results")
FIGS = os.environ.get("FIGS_DIR", "figures")

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

def rows(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))

def label_bars(ax, bars, fmt):
    for b in bars:
        h = b.get_height()
        ax.annotate(fmt(h), xy=(b.get_x() + b.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.5)

DATASETS = ["UGRansome2024", "CICIoT2023"]
MODELS = ["RandomForest", "DecisionTree", "XGBoost", "LogisticRegression"]
MODEL_LABELS = ["Random\nForest", "Decision\nTree", "XGBoost", "Logistic\nRegression"]
C_UGR, C_CIC = "#3b6ea5", "#e08214"
C_BASE, C_ML = "#9aa3ad", "#2f6f8f"

# ---------------- Figure 17: computational efficiency ----------------
eff = {(r["dataset"], r["model"]): r for r in rows(os.path.join(RESULTS, "efficiency_table.csv"))}

def col(metric):
    ugr = [float(eff[("UGRansome2024", m)][metric]) for m in MODELS]
    cic = [float(eff[("CICIoT2023", m)][metric]) for m in MODELS]
    return ugr, cic

x = np.arange(len(MODELS)); w = 0.38
fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

tu, tc = col("training_time_sec")
ax = axes[0]
b1 = ax.bar(x - w/2, tu, w, color=C_UGR); b2 = ax.bar(x + w/2, tc, w, color=C_CIC)
ax.set_ylabel("Training time (s)"); ax.set_title("(a) Training time")
ax.set_xticks(x); ax.set_xticklabels(MODEL_LABELS); ax.set_ylim(0, max(tu + tc) * 1.15)
label_bars(ax, b1, lambda v: f"{v:.2f}"); label_bars(ax, b2, lambda v: f"{v:.2f}")

iu, ic = col("per_flow_us")
ax = axes[1]
b1 = ax.bar(x - w/2, iu, w, color=C_UGR); b2 = ax.bar(x + w/2, ic, w, color=C_CIC)
ax.set_yscale("log"); ax.set_ylabel("Inference per flow (us, log scale)")
ax.set_title("(b) Per-flow inference time")
ax.set_xticks(x); ax.set_xticklabels(MODEL_LABELS); ax.set_ylim(0.01, 10)
label_bars(ax, b1, lambda v: f"{v:.2f}"); label_bars(ax, b2, lambda v: f"{v:.2f}")

su, sc = col("model_size_mb")
ax = axes[2]
b1 = ax.bar(x - w/2, su, w, color=C_UGR); b2 = ax.bar(x + w/2, sc, w, color=C_CIC)
ax.set_yscale("log"); ax.set_ylabel("Model size on disk (MB, log scale)")
ax.set_title("(c) On-disk model size")
ax.set_xticks(x); ax.set_xticklabels(MODEL_LABELS); ax.set_ylim(0.0005, 10)
label_bars(ax, b1, lambda v: f"{v:.3f}"); label_bars(ax, b2, lambda v: f"{v:.3f}")

handles = [plt.Rectangle((0, 0), 1, 1, color=C_UGR), plt.Rectangle((0, 0), 1, 1, color=C_CIC)]
fig.legend(handles, DATASETS, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.03))
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(FIGS, "efficiency.png"), dpi=600, bbox_inches="tight")
fig.savefig(os.path.join(FIGS, "efficiency.pdf"), bbox_inches="tight")
plt.close(fig)

# ---------------- Figure 18: SOC workload impact ----------------
soc = {r["dataset"]: r for r in rows(os.path.join(RESULTS, "soc_workload.csv"))}
fa_base = [float(soc[d]["baseline_false_alerts_per_1000"]) for d in DATASETS]
fa_ml   = [float(soc[d]["ml_false_alerts_per_1000"]) for d in DATASETS]
miss_base = [int(float(soc[d]["baseline_fn"])) for d in DATASETS]
miss_ml   = [int(float(soc[d]["ml_fn"])) for d in DATASETS]

x = np.arange(len(DATASETS)); w = 0.36
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))

ax = axes[0]
b1 = ax.bar(x - w/2, fa_base, w, color=C_BASE); b2 = ax.bar(x + w/2, fa_ml, w, color=C_ML)
ax.set_yscale("log"); ax.set_ylabel("False alerts per 1,000 alerts (log scale)")
ax.set_title("(a) False alerts per 1,000 alerts")
ax.set_xticks(x); ax.set_xticklabels(DATASETS); ax.set_ylim(1, 3000)
label_bars(ax, b1, lambda v: f"{v:.2f}"); label_bars(ax, b2, lambda v: f"{v:.2f}")

ax = axes[1]
b1 = ax.bar(x - w/2, miss_base, w, color=C_BASE); b2 = ax.bar(x + w/2, miss_ml, w, color=C_ML)
ax.set_yscale("log"); ax.set_ylabel("Missed attacks (log scale)")
ax.set_title("(b) Missed attacks (false negatives)")
ax.set_xticks(x); ax.set_xticklabels(DATASETS); ax.set_ylim(1, 12000)
label_bars(ax, b1, lambda v: f"{int(v)}"); label_bars(ax, b2, lambda v: f"{int(v)}")

handles = [plt.Rectangle((0, 0), 1, 1, color=C_BASE), plt.Rectangle((0, 0), 1, 1, color=C_ML)]
fig.legend(handles, ["Rule baseline", "Best ML model"], frameon=False, ncol=2,
           loc="upper center", bbox_to_anchor=(0.5, 1.02))
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(os.path.join(FIGS, "soc_workload.png"), dpi=600, bbox_inches="tight")
fig.savefig(os.path.join(FIGS, "soc_workload.pdf"), bbox_inches="tight")
plt.close(fig)

print("Wrote figures/efficiency.{png,pdf} and figures/soc_workload.{png,pdf} at 600 DPI")
