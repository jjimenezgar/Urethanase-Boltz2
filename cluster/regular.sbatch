#!/bin/bash
#SBATCH --job-name=urethanase-boltz2
#SBATCH --partition=general
#SBATCH --qos=gpu-regular
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --constraint=a100
#SBATCH --output=logs/regular-%j.log
set -euo pipefail
cd /scratch/jcjimenez/Urethanase-Boltz2-benchmark
export PYTHONPATH="$PWD/src"
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
export XDG_CACHE_HOME="$PWD/.cache"
export TORCH_HOME="$PWD/.cache/torch"
export TMPDIR="$PWD/.tmp"
mkdir -p "$TMPDIR" "$XDG_CACHE_HOME"
source .venv/bin/activate
python scripts/run_benchmark.py --out-dir results/boltz2 --seed 42
