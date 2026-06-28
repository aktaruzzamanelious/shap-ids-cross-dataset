#!/usr/bin/env python3
"""
verify_canonical_artifacts.py  --  MDPI Sensors Paper 1 repository gate.

Run on the VPS BEFORE building/pushing the repo:

    python3 verify_canonical_artifacts.py /path/to/vps/project/root

What it does:
  * Locates each of the 13 canonical result CSVs the manuscript depends on.
  * Verifies each one against (a) an embedded sha256 (exact-identical signal)
    and (b) the specific cell values that appear in the manuscript tables/
    figures (the real gate; tolerant to float-formatting differences).
  * Lists any *.csv found that is NOT a canonical file -> candidate orphan,
    for human review (do not auto-delete).
  * Reminds about artifacts the manuscript names but that are not in this set
    (rule baseline results, cpu_info.json, raw_efficiency_timings.json,
    SHAP interactions, trained models, 18 figures).

Exit code 0 only if every canonical file is present and all value asserts pass.
"""
import sys, os, csv, hashlib

TOL = 5e-4  # rounding tolerance for 4-dp manuscript values

EXPECTED_SHA256 = {
    "master_results_all.csv":            "521802dbe96a91dd122ed8d2c608bab536ab5104417f6ce649288e0e4d0f73aa",
    "metrics_with_ci_ugr.csv":           "e69f5fb86ba909ba3ff399da6d21f6d6e4ee90f98a8898568f7cb488bb42c1dd",
    "metrics_with_ci_cic.csv":           "bcd7a33a96baf749687a757b68934701fa9d080d4cb7dffe00e1cb6a9ecd1fa1",
    "rf_seed_robustness.csv":            "15f4e1b957d03ac79eb92cd545205178d099ef03cee9c8ba501bc92c953b4170",
    "mcnemar_results.csv":               "80ad6b8f42d32f4a2155c61ee811a9656ee853e442971ea6081d4cbf269260ad",
    "ablation_ugransome_tier_a.csv":     "3eacdc1f7d507ae066cedbc6161fa0d1ec3b1f1f7188b76e9bebfcc8782a804f",
    "ablation_ugransome_tier_b.csv":     "9f738b615d686d0d362f021cf243184cec3789ca5555573ce19845cab948b928",
    "spearman_correlations.csv":         "808cfaac198aa87c4ebaeec1cf976add9422b1608bd37460bc7a739d0fd7a542",
    "shap_vs_gini_permutation_cic.csv":  "43d12ebc2a16143c0c27e819292d45188463121dd9ee79a74d42f2ab4152eb2a",
    "shap_vs_gini_permutation_ugr.csv":  "fef955fe57ce0404e878e02f326313ee72638def484620e92eb2e1d1c4bedebf",
    "per_category_recall_cic.csv":       "89c0620817394d7023e837650b3f4d7d0923677789dcc9b9279ca95936784bb3",
    "efficiency_table.csv":              "9904b0c314c24de4e7856da7883f2c19f12df7cd0ed3d48656d0276f3b430c9d",
    "soc_workload.csv":                  "2f5540f579fb50b94854407bf17b8052d7e1e0b08c2c85969cae895ead25531c",
}

# Maps each canonical file to the manuscript objects it feeds.
FEEDS = {
    "master_results_all.csv": "Tables 1, 2, 3 (4 classifiers only; no baseline)",
    "metrics_with_ci_ugr.csv": "Table 6 + Sec 4.5 redirect (full per-metric CIs)",
    "metrics_with_ci_cic.csv": "Table 6 + Sec 4.5 redirect (full per-metric CIs)",
    "rf_seed_robustness.csv": "Table 4, Figure 7",
    "mcnemar_results.csv": "Table 5",
    "ablation_ugransome_tier_a.csv": "Table 7, Figure 9 (Tier A)",
    "ablation_ugransome_tier_b.csv": "Table 7, Figure 9 (Tier B)",
    "spearman_correlations.csv": "Table 8",
    "shap_vs_gini_permutation_cic.csv": "Table 9",
    "shap_vs_gini_permutation_ugr.csv": "Table 10",
    "per_category_recall_cic.csv": "Table 11",
    "efficiency_table.csv": "Table 12, Figure 17",
    "soc_workload.csv": "Tables 13, 14, Figure 18",
}

def rows(path):
    with open(path, newline='') as fh:
        return list(csv.DictReader(fh))

def close(a, b, tol=TOL):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False

def find_row(rs, **kv):
    for r in rs:
        if all(r.get(k) == v for k, v in kv.items()):
            return r
    return None

# ---- per-file value gates (the real checks, not just checksums) ----
def check_values(name, path):
    """Return list of (ok, message)."""
    out = []
    rs = rows(path)
    if name == "master_results_all.csv":
        if len(rs) != 8:
            out.append((False, f"expected 8 rows (4 classifiers x 2 datasets), got {len(rs)}"))
        r = find_row(rs, dataset="UGRansome2024", model="XGBoost")
        out.append((r is not None and close(r["f1_macro"], 0.994416) and r["tp"]=="4090" and r["fp"]=="64" and r["fn"]=="7" and r["tn"]=="13811",
                    "UGR/XGBoost f1=0.9944, cm=4090/64/7/13811"))
        r = find_row(rs, dataset="CICIoT2023", model="RandomForest")
        out.append((r is not None and close(r["f1_macro"], 0.962162) and r["tp"]=="38985" and r["fp"]=="75" and r["fn"]=="64" and r["tn"]=="871",
                    "CIC/RandomForest f1=0.9622, cm=38985/75/64/871"))
        # baseline must NOT be in this file
        out.append((find_row(rs, model="RuleBaseline") is None and find_row(rs, model="Baseline") is None,
                    "no rule-baseline row in master_results_all (baseline lives elsewhere)"))
    elif name == "metrics_with_ci_ugr.csv":
        r = find_row(rs, model="XGBoost")
        out.append((r and close(r["f1_macro"],0.994416) and close(r["f1_macro_lo"],0.993178) and close(r["f1_macro_hi"],0.995667),
                    "UGR/XGBoost f1=0.9944 [0.9932,0.9957]"))
    elif name == "metrics_with_ci_cic.csv":
        r = find_row(rs, model="RandomForest")
        out.append((r and close(r["f1_macro"],0.962162) and close(r["f1_macro_lo"],0.955639) and close(r["f1_macro_hi"],0.967918),
                    "CIC/RandomForest f1=0.9622 [0.9556,0.9679]"))
    elif name == "rf_seed_robustness.csv":
        out.append((len(rs)==10, f"expected 10 rows (5 seeds x 2 datasets), got {len(rs)}"))
        r = find_row(rs, dataset="UGRansome2024", seed="42")
        out.append((r and close(r["f1_macro"],0.99108), "UGR seed42 f1=0.9911"))
        r = find_row(rs, dataset="CICIoT2023", seed="42")
        out.append((r and close(r["f1_macro"],0.962162), "CIC seed42 f1=0.9622"))
    elif name == "mcnemar_results.csv":
        out.append((len(rs)==12, f"expected 12 pairs, got {len(rs)}"))
        r = find_row(rs, dataset="UGRansome2024", model_A="RandomForest", model_B="LogisticRegression")
        out.append((r and close(r["statistic"],1162.8695,1e-2), "UGR RF-vs-LR statistic=1162.8695"))
        out.append((all(x.get("significant_holm")=="True" for x in rs), "all 12 pairs significant after Holm"))
    elif name == "ablation_ugransome_tier_a.csv":
        out.append((len(rs)==1 and close(rs[0]["f1_macro"],0.967663), "Tier A f1=0.9677, n_features=19"))
        out.append((rs and rs[0]["n_features"]=="19", "Tier A n_features=19"))
    elif name == "ablation_ugransome_tier_b.csv":
        full = [r for r in rs if "full" in r["tier"]]
        out.append((full and close(full[0]["f1_macro"],0.99108) and full[0]["n_features"]=="49", "Tier B full f1=0.9911, n_features=49"))
    elif name == "spearman_correlations.csv":
        r = find_row(rs, dataset="CICIoT2023", comparison="SHAP vs Tree")
        out.append((r and close(r["rho"],0.933040) and r["tree_importance_type"]=="rf_gini", "CIC SHAP-vs-Tree rho=0.9330 (rf_gini)"))
        r = find_row(rs, dataset="UGRansome2024", comparison="SHAP vs Tree")
        out.append((r and close(r["rho"],0.773340) and r["tree_importance_type"]=="xgboost_gain", "UGR SHAP-vs-Tree rho=0.7733 (xgboost_gain)"))
    elif name == "shap_vs_gini_permutation_cic.csv":
        r = find_row(rs, feature="IAT")
        out.append((r and r["shap_rank"]=="2" and r["tree_rank"]=="14" and r["perm_rank"]=="2" and r["tree_importance_type"]=="rf_gini",
                    "IAT: SHAP rank 2, Gini rank 14, perm rank 2"))
    elif name == "shap_vs_gini_permutation_ugr.csv":
        r = find_row(rs, feature="Protocol_TCP")
        out.append((r and r["shap_rank"]=="13" and r["tree_rank"]=="3" and r["tree_importance_type"]=="xgboost_gain",
                    "Protocol_TCP: SHAP rank 13, gain rank 3"))
    elif name == "per_category_recall_cic.csv":
        r = find_row(rs, model="RandomForest", category="Brute Force")
        out.append((r and r["total_samples"]=="11" and r["tp"]=="10" and r["fn"]=="1" and close(r["recall"],0.909091),
                    "RF Brute Force: 11 samples, recall 0.9091"))
    elif name == "efficiency_table.csv":
        r = find_row(rs, dataset="UGRansome2024", model="RandomForest")
        out.append((r and close(r["per_flow_us"],4.5673,1e-3) and close(r["model_size_mb"],3.295,1e-3),
                    "UGR/RF inference 4.57 us, size 3.295 MB"))
    elif name == "soc_workload.csv":
        out.append((len(rs)==2, f"expected 2 rows, got {len(rs)}"))
        r = find_row(rs, dataset="UGRansome2024", best_model="XGBoost")
        out.append((r and close(r["baseline_false_alerts_per_1000"],617.1875,1e-2) and close(r["ml_false_alerts_per_1000"],15.4068,1e-2) and r["baseline_fn"]=="1206" and r["ml_fn"]=="7",
                    "UGR SOC: FA/1000 617.19->15.41, missed 1206->7"))
        r = find_row(rs, dataset="CICIoT2023", best_model="RandomForest")
        out.append((r and r["baseline_fn"]=="4520" and r["ml_fn"]=="64", "CIC SOC: missed 4520->64"))
    return out

def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def main(root):
    found = {}   # basename -> fullpath
    for dirpath, _, files in os.walk(root):
        if "/.git" in dirpath:
            continue
        for f in files:
            if f.endswith(".csv"):
                found.setdefault(f, os.path.join(dirpath, f))

    print("="*70)
    print("CANONICAL FILE VERIFICATION")
    print("="*70)
    all_ok = True
    for name in EXPECTED_SHA256:
        path = found.get(name)
        if not path:
            print(f"[MISSING] {name}  <- {FEEDS[name]}")
            all_ok = False
            continue
        digest = sha256(path)
        sha_ok = (digest == EXPECTED_SHA256[name])
        checks = check_values(name, path)
        vals_ok = all(ok for ok, _ in checks)
        tag = "OK" if vals_ok else "VALUE-FAIL"
        sha_note = "sha256 identical" if sha_ok else "sha256 DIFFERS (re-exported? verify values below)"
        print(f"[{tag}] {name}  ({sha_note})  <- {FEEDS[name]}")
        print(f"        path: {path}")
        for ok, msg in checks:
            print(f"          {'PASS' if ok else 'FAIL'}: {msg}")
        all_ok = all_ok and vals_ok

    # orphan CSVs
    extras = sorted(set(found) - set(EXPECTED_SHA256))
    print("\n" + "="*70)
    print("NON-CANONICAL CSVs FOUND (review; do NOT auto-delete)")
    print("="*70)
    if extras:
        for e in extras:
            print(f"  REVIEW: {e}  ->  {found[e]}")
        print("  (could be: intermediate output, older/orphan experiment, or a")
        print("   legitimately needed extended file such as SHAP interactions.)")
    else:
        print("  none")

    # named artifacts not in the CSV set
    print("\n" + "="*70)
    print("ALSO REQUIRED BY THE MANUSCRIPT (confirm these exist + committed)")
    print("="*70)
    for item in [
        "Rule baseline results source (macro-F1 0.6274 UGR / 0.5986 CIC + baseline confusion matrices, Sec 4.1) -- NOT in master_results_all.csv",
        "results/cpu_info.json (Sec 3.8, 4.9)",
        "results/raw_efficiency_timings.json (Sec 3.8)",
        "SHAP interaction output: top-5 interaction pairs per dataset (Sec 4.7 redirect)",
        "Rule-threshold derivation script (Sec 3.3)",
        "8 trained models: RF/DT/XGBoost/LR x {UGRansome2024, CICIoT2023}",
        "18 figures at 600 DPI (incl. corrected Figure 17 and Figure 18)",
    ]:
        print(f"  CONFIRM: {item}")

    print("\n" + "="*70)
    print("RESULT:", "ALL CANONICAL CHECKS PASSED" if all_ok else "FAILURES ABOVE -- DO NOT PUSH")
    print("="*70)
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    # Default to the current directory so reviewers can run this from the repo root:
    #   python3 verify_canonical_artifacts.py
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    main(root)
