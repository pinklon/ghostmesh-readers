"""Provider-free, synthetic search pilot inspired by (not reproducing) SpecEvo.

Tests whether retaining evaluated failures adds value under equal evaluation budgets.
Not a benchmark of LLM agents, authority, real science, or SpecEvo itself.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

TASK_TARGETS = (5, 18, 31, 44, 57, 9, 22, 35, 48, 61, 14, 53)
DOMAIN = 64
BUDGET = 12
SEEDS = tuple(range(12))

def reward(candidate: int, target: int) -> float:
    return max(0.0, 1.0 - abs(candidate - target) / 63.0)

def run_task(target: int, seed: int, strategy: str) -> dict:
    if strategy not in {"random", "success_only", "failure_aware"}:
        raise ValueError("Invalid strategy")
    rng=random.Random(seed)
    tested=[]
    best=None
    best_score=-1.0
    failed_or_worse=set()
    for step in range(BUDGET):
        if strategy=="random" or best is None:
            guess=rng.randrange(DOMAIN)
        elif strategy=="success_only":
            # Uses best observed value but does not prevent repeating failed trials.
            guess=min(DOMAIN-1,max(0,best+rng.choice((-12,-6,-3,-1,0,1,3,6,12))))
        else:
            # Same local search moves, plus an explicitly consulted failure/attempt
            # record. If all local moves have been seen, explore an unseen value.
            local=[min(DOMAIN-1,max(0,best+offset)) for offset in (-12,-6,-3,-1,0,1,3,6,12)]
            unseen=[v for v in local if v not in failed_or_worse and v not in tested]
            if not unseen:
                unseen=[v for v in range(DOMAIN) if v not in tested]
            guess=rng.choice(unseen) if unseen else rng.randrange(DOMAIN)
        score=reward(guess,target)
        tested.append(guess)
        if score>best_score:
            best,best_score=guess,score
        else:
            failed_or_worse.add(guess)
    return {"best_score":round(best_score,6),"best_candidate":best,
            "evaluations":len(tested),"duplicate_evaluations":len(tested)-len(set(tested)),
            "exact_match":best==target}

def benchmark() -> dict:
    rows=[]
    for task_index,target in enumerate(TASK_TARGETS):
        for seed in SEEDS:
            for policy in ("random","success_only","failure_aware"):
                outcome=run_task(target,seed,policy)
                rows.append({"task":task_index,"seed":seed,"policy":policy,**outcome})
    summary={}
    for policy in ("random","success_only","failure_aware"):
        group=[x for x in rows if x["policy"]==policy]
        n=len(group)
        summary[policy]={
            "trials":n,"evaluations":sum(x["evaluations"] for x in group),
            "mean_best_score":round(sum(x["best_score"] for x in group)/n,6),
            "exact_matches":sum(x["exact_match"] for x in group),
            "duplicate_evaluations":sum(x["duplicate_evaluations"] for x in group)
        }
    return {"schema":"scout-speculative-search-pilot-v0",
            "design":"12 synthetic 1D target-search tasks x 12 seeded repeats x 3 strategies",
            "evaluation_budget_per_trial":BUDGET,"strategies":summary,
            "rows":rows,
            "limitations":[
                "Synthetic one-dimensional reward is not scientific discovery or agent teamwork",
                "Strategies use different candidate proposal rules; any observed difference does not isolate memory as a causal variable",
                "Fixed seeds ensure reproducibility, not independent statistical validation",
                "No expensive-model navigator or persistent agent runtime was implemented",
                "No use of service credentials, installed GhostMesh workers, or real user data"],
            "production_adoption":"NOT_AUTHORIZED","publication_authorized":False,
            "outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing to overwrite trial")
    report=benchmark()
    a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report["strategies"],indent=2))
if __name__=="__main__":main()
