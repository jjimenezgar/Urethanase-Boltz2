#!/bin/bash
#SBATCH --job-name=urethanase-test
#SBATCH --partition=general
#SBATCH --qos=test
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --constraint=a100
#SBATCH --output=logs/test-%j.log
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
nvidia-smi
python -c 'import torch; print(torch.__version__, torch.cuda.is_available()); assert torch.cuda.is_available()'
python -m pytest -m 'not integration' -q
python scripts/run_benchmark.py --out-dir results/test --seed 42
