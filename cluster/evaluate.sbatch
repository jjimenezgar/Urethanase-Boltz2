#!/bin/bash
#SBATCH --job-name=urethanase-evaluate
#SBATCH --partition=general
#SBATCH --qos=test
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=logs/evaluate-%j.log
set -euo pipefail
cd /scratch/jcjimenez/Urethanase-Boltz2-benchmark
export PYTHONPATH="$PWD/src"
export XDG_CACHE_HOME="$PWD/.cache"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
source .venv/bin/activate
python -m pytest -m 'not integration' -q
python scripts/run_benchmark.py --out-dir results/test --evaluate-only
