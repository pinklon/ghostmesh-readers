"""Offline synthetic directional-failure feedback pilot.

Controlled matched candidate tapes, identical scoring budget. The information
treatment (directional failure labels) differs deliberately and is accounted for.
Not a reproduction of SpecEvo, a model test, or production agent evidence.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

TARGETS=(5,18,31,44,57,9,22,35,48,61,14,53)
SEEDS=tuple(range(16))
BUDGET=12
SPACE=64

def evaluate(target,candidate):
    # The "direction" below is privileged evaluator guidance, not an inference
    # discovered by the model. Treat it as potentially costly extra information.
    if candidate<target: direction="too_low"
    elif candidate>target: direction="too_high"
    else: direction="correct"
    return 1-abs(candidate-target)/63, direction

def trial(target, seed, guidance=False):
    if target not in TARGETS or seed not in SEEDS:raise ValueError("Unconfigured fixture")
    rng=random.Random(target*100003+seed)
    tape=[rng.randrange(SPACE) for _ in range(1200)]
    tested=set()
    low,high=0,SPACE-1
    scores=[]
    candidates=[]
    proposals_read=0
    hint_count=0
    for _ in range(BUDGET):
        guess=None
        while proposals_read<len(tape):
            candidate=tape[proposals_read]
            proposals_read+=1
            if candidate in tested:continue
            if guidance and not (low<=candidate<=high):continue
            guess=candidate
            break
        if guess is None:raise ValueError("Candidate stream exhausted")
        tested.add(guess)
        score,direction=evaluate(target,guess)
        scores.append(score);candidates.append(guess)
        if guidance and direction!="correct":
            hint_count+=1
            if direction=="too_low":low=max(low,guess+1)
            else:high=min(high,guess-1)
    return {"best_reward":round(max(scores),6),
            "exact_match":target in tested,
            "evaluations":len(scores),
            "proposals_examined":proposals_read,
            "directional_hints_used":hint_count,
            "duplicate_evaluations":len(candidates)-len(set(candidates))}

def benchmark():
    trials=[]
    for i,target in enumerate(TARGETS):
        for seed in SEEDS:
            for guidance in (False,True):
                trials.append({"task":i,"seed":seed,"arm":"directional" if guidance else "ledger_only",
                               **trial(target,seed,guidance)})
    summary={}
    for arm in ("ledger_only","directional"):
        group=[r for r in trials if r["arm"]==arm]
        summary[arm]={"trials":len(group),
                      "mean_best_reward":round(sum(r["best_reward"] for r in group)/len(group),6),
                      "exact_matches":sum(r["exact_match"] for r in group),
                      "evaluations":sum(r["evaluations"] for r in group),
                      "proposals_examined":sum(r["proposals_examined"] for r in group),
                      "directional_hints_used":sum(r["directional_hints_used"] for r in group),
                      "duplicate_evaluations":sum(r["duplicate_evaluations"] for r in group)}
    return {"schema":"scout-directional-guidance-pilot-v0",
            "design":"12 synthetic 1D targets x 16 paired seeds x 2 arms; 12 evaluations per trial",
            "treatment":"Both arms skip duplicate proposals. Directional arm also receives evaluator-provided high/low failure labels and excludes inconsistent proposals.",
            "summary":summary,"trials":trials,
            "limitations":["Directional hints reveal privileged information about synthetic target location. The baseline lacks that additional information.",
                           "Equal evaluation calls do not mean equal feedback, total compute, latency, or proposal search cost.",
                           "The guidance oracle is deterministic and noiseless, unlike real model criticism.",
                           "No agent, scientific discovery, model reasoning, or SpecEvo reproduction was tested.",
                           "Benefits do not transfer to GhostMesh without separate evidence and budget accounting"],
            "publication_authorized":False,"outreach_authorized":False,
            "production_adoption":"NOT_AUTHORIZED"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise SystemExit("Refusing overwrite")
    b=benchmark()
    args.out.write_text(json.dumps(b,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(b["summary"],indent=2))
if __name__=="__main__":main()
