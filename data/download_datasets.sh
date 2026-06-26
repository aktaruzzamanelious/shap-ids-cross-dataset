#!/usr/bin/env bash
# Download the raw datasets for the SHAP-IDS cross-dataset study.
#
# UGRansome2024 is fetched from Kaggle via the Kaggle CLI.
# CICIoT2023 requires accepting the CIC access form by hand and is NOT scriptable;
# this script only prints instructions for it.
#
# Prerequisites for the Kaggle step:
#   pip install kaggle
#   Place your Kaggle API token at ~/.kaggle/kaggle.json (chmod 600).
#   See https://www.kaggle.com/docs/api
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW="${HERE}/raw"
mkdir -p "${RAW}"

echo "==> Downloading UGRansome2024 from Kaggle into ${RAW}"
if ! command -v kaggle >/dev/null 2>&1; then
  echo "ERROR: kaggle CLI not found. Install with: pip install kaggle" >&2
  exit 1
fi
kaggle datasets download -d azugo/ugransome2024 -p "${RAW}" --unzip

cat <<'EOF'

==> CICIoT2023 (manual step)
    1. Open https://www.unb.ca/cic/datasets/iotdataset-2023.html
    2. Submit the data-access request form and download the archive.
    3. Extract it under data/raw/CICIOT23/ so that the layout is:
         data/raw/CICIOT23/train/train.csv
         data/raw/CICIOT23/test/test.csv
         data/raw/CICIOT23/validation/validation.csv

Done. Next: run notebooks/01_data_cleaning.ipynb and notebooks/02_preprocessing.ipynb
EOF
