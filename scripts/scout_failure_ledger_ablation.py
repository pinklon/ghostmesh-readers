"""Matched candidate-stream ablation for the value of a tried-candidate ledger.

Both arms receive identical seeded proposal streams and exactly 12 evaluations.
The sole difference is whether previously evaluated candidates are skipped.
This is synthetic duplicate avoidance, not a reproduction of SpecEvo or an LLM test.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

TARGETS=(5,18,31,44,57,9,22,35,48,61,14,53)
SEEDS=tuple(range(12))
BUDGET=12
DOMAIN=64

def trial(target:int,seed:int,use_history:bool)->dict:
    if not 0<=target<DOMAIN:raise ValueError("invalid target")
    # Candidate proposal tape generated ONCE per task and seed. No adaptive
    # modeling: this isolates the effect of a seen-candidate exclusion ledger.
    rng=random.Random(seed*100003+target)
    tape=[rng.randrange(DOMAIN) for _ in range(200)]
    seen=set()
    scores=[]
    consumed=0
    duplicates=0
    evaluated=[]
    for candidate in tape:
        consumed+=1
        if use_history and candidate in seen:
            continue
        if candidate in seen:duplicates+=1
        seen.add(candidate)
        evaluated.append(candidate)
        scores.append(1-abs(candidate-target)/63)
        if len(scores)>=BUDGET:break
    assert len(scores)==BUDGET
    return {"best_reward":round(max(scores),6),"exact_match":target in evaluated,
            "duplicate_evaluations":duplicates,"proposals_examined":consumed,
            "evaluations":len(scores)}

def benchmark()->dict:
    results=[]
    for target_index,target in enumerate(TARGETS):
        for seed in SEEDS:
            for ledger in (False,True):
                results.append({"task":target_index,"seed":seed,
                    "policy":"ledger" if ledger else "no_ledger",
                    **trial(target,seed,ledger)})
    aggregate={}
    for policy in ("no_ledger","ledger"):
        subset=[r for r in results if r["policy"]==policy]
        aggregate[policy]={
          "trials":len(subset),
          "mean_best_reward":round(sum(r["best_reward"] for r in subset)/len(subset),6),
          "exact_matches":sum(r["exact_match"] for r in subset),
          "duplicate_evaluations":sum(r["duplicate_evaluations"] for r in subset),
          "total_evaluations":sum(r["evaluations"] for r in subset),
          "total_proposals_examined":sum(r["proposals_examined"] for r in subset)}
    return {"schema":"scout-failure-ledger-ablation-v0",
      "design":"12 fixed 1D targets x 12 seeded repeats; same proposal tape per pair; 12 evaluations per arm",
      "policy_difference":"Ledger arm skips previously evaluated candidates on same fixed candidate tape",
      "summary":aggregate,"trials":results,
      "limitations":["Skipping duplicates can improve sample efficiency but consumes extra proposal inspection work",
                     "This is a narrow deterministic ablation of duplicate avoidance, not memory-guided reasoning",
                     "One-dimensional synthetic reward does not establish results in agent orchestration or scientific research",
                     "No costs for model guidance, training, or real-runtime authority were tested"],
      "production_adoption":"NOT_AUTHORIZED","outreach_authorized":False,
      "publication_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    result=benchmark()
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],indent=2))
if __name__=="__main__":main()
