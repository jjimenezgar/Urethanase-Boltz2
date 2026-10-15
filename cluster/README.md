# Hyperion execution records

The benchmark ran on Hyperion using an NVIDIA A100 80 GB and the environment
recorded in `environment.freeze.txt`. Install the deliberately pinned inference
stack from `requirements-inference.txt` in a separate environment. The full freeze
is an audit of the original installation, including unused packages left by its
setup; the shorter requirements file is the recommended install entrypoint.

| File | Purpose |
|---|---|
| `test.sbatch` | Original ten-minute, single-seed GPU test |
| `seed_batch.sbatch` | Three seeds per ten-minute GPU test |
| `evaluate.sbatch` | CPU evaluation of an already generated prediction |
| `regular.sbatch` | Four-hour fallback; not used for the completed seed campaign |

On this cluster, `test` is a QOS on partition `general`, rather than a partition.
GPU type is requested with `--gres=gpu:1` plus `--constraint=a100`.
The GPU variant of regular service is `gpu-regular`.

The scripts contain the original working directory, account context and output
paths for this experiment. Review these before using another account or creating
another campaign. Never submit a fresh batch into existing seed output folders.
The historical controller starts with this campaign's job IDs and is not a generic
submission tool. All completed jobs and timings are listed in
[the experiment record](../docs/multiseed.md).

For another seed, use a fresh directory and the fixed-MSA input. For example,
inside an allocated GPU job with the project environment active:

```bash
export PYTHONPATH="$PWD/src"
python scripts/run_benchmark.py \
  --input inputs/umg_sp2_a1d5h_cached_msa.yaml \
  --out-dir results/new_seed_52 --seed 52
```

The local repository has all necessary evaluation artifacts. There is no need
to reconnect to Hyperion to reproduce the saved metric calculations.
