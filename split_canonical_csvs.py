#!/usr/bin/env python3
"""
split_canonical_csvs.py -- reproduce the four split canonical result CSVs.

Notebooks 08 and 09 each write a single *combined* file:
    results/ablation_ugr.csv   (08_ablation.ipynb)  -- Tier A row + four Tier B rows
    results/bootstrap_ci.csv   (09_bootstrap_ci.ipynb) -- both datasets stacked

The manuscript-canonical artifacts are these split by row. This split was
originally a one-off manual step; this script makes it reproducible. Run from
the repository root AFTER notebooks 08 and 09 have produced the combined files:

    python3 split_canonical_csvs.py

Writes (into results/):
    ablation_ugransome_tier_a.csv   tier == A_raw_flow_only
    ablation_ugransome_tier_b.csv   the four B1..B4 rows
    metrics_with_ci_ugr.csv         dataset == UGRansome2024
    metrics_with_ci_cic.csv         dataset == CICIoT2023

The split copies the header and matching data lines verbatim (no re-parsing of
floats), so the output is byte-identical to the combined source's rows and
matches the sha256 gate in verify_canonical_artifacts.py.
"""
import os
import sys

RESULTS = os.environ.get("RESULTS_DIR", "results")


def first_field(line):
    return line.split(",", 1)[0]


def split_file(src, specs):
    """specs: list of (out_basename, predicate(first_field) -> bool)."""
    path = os.path.join(RESULTS, src)
    if not os.path.exists(path):
        print(f"[MISSING] {path}")
        print(f"          run the notebook that writes {src} first "
              f"(08_ablation.ipynb / 09_bootstrap_ci.ipynb).")
        return False
    with open(path, newline="") as fh:
        lines = fh.readlines()          # keep exact line endings
    header, data = lines[0], lines[1:]
    ok = True
    for out_name, pred in specs:
        rows = [ln for ln in data if ln.strip() and pred(first_field(ln))]
        if not rows:
            print(f"[WARN] no rows matched for {out_name} (check {src} contents)")
            ok = False
        out_path = os.path.join(RESULTS, out_name)
        with open(out_path, "w", newline="") as fh:
            fh.write(header)
            fh.writelines(rows)
        print(f"  wrote {out_path}  ({len(rows)} data row(s))")
    return ok


# combined input file -> notebook that writes it
INPUTS = {
    "ablation_ugr.csv": "notebooks/08_ablation.ipynb",
    "bootstrap_ci.csv": "notebooks/09_bootstrap_ci.ipynb",
}


def check_inputs():
    """Return list of (basename, notebook) for any combined file that is absent."""
    return [(src, nb) for src, nb in INPUTS.items()
            if not os.path.exists(os.path.join(RESULTS, src))]


def main():
    missing = check_inputs()
    if missing:
        print("=" * 64)
        print("COMBINED FILES NOT FOUND -- run notebooks 08/09 first")
        print("=" * 64)
        for src, nb in missing:
            print(f"  missing: {os.path.join(RESULTS, src)}")
            print(f"           produced by {nb} -- run it, then re-run this script.")
        print("\nNothing written. This script only splits existing combined")
        print("files; it does not regenerate them.")
        sys.exit(1)

    print("Splitting combined CSVs into canonical filenames ...")
    a = split_file("ablation_ugr.csv", [
        ("ablation_ugransome_tier_a.csv", lambda t: t == "A_raw_flow_only"),
        ("ablation_ugransome_tier_b.csv", lambda t: t != "A_raw_flow_only"),
    ])
    b = split_file("bootstrap_ci.csv", [
        ("metrics_with_ci_ugr.csv", lambda d: d == "UGRansome2024"),
        ("metrics_with_ci_cic.csv", lambda d: d == "CICIoT2023"),
    ])
    if a and b:
        print("Done. Verify with: python3 verify_canonical_artifacts.py .")
        sys.exit(0)
    print("Incomplete -- see messages above.")
    sys.exit(1)


if __name__ == "__main__":
    main()
