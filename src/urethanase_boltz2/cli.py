from __future__ import annotations
import argparse
from pathlib import Path
from .evaluate import evaluate_complex, save_metrics

def main():
    p = argparse.ArgumentParser(description="Evaluate a Boltz-2 UMG-SP2 complex")
    sub = p.add_subparsers(dest="command", required=True)
    e = sub.add_parser("evaluate")
    e.add_argument("--reference", type=Path, required=True)
    e.add_argument("--prediction", type=Path, required=True)
    e.add_argument("--ligand", required=True)
    e.add_argument("--output", type=Path, required=True)
    e.add_argument("--ref-chain", default="A")
    e.add_argument("--pred-chain", default="A")
    a = p.parse_args()
    if a.command == "evaluate":
        metrics = evaluate_complex(a.reference, a.prediction, a.ligand, a.ref_chain, a.pred_chain)
        save_metrics(metrics, a.output)
        print(metrics)
