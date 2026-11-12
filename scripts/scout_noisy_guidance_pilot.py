"""Noise-aware guidance and stop/escalation research, entirely synthetic and offline.

Matched proposal streams. Guidance is fallible, and proposal inspection and
feedback have explicit costs. This is not model reasoning or SpecEvo reproduction.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

TARGETS=(5,18,31,44,57,9,22,35,48,61,14,53)
SEEDS=tuple(range(12))
EVAL_LIMIT=12
SPACE=64
RATES=(0.0,0.1,0.3,0.5)
POLICIES=("ledger","always_guided","guarded")
EVAL_COST=1.0
PROPOSAL_COST=0.002
HINT_COST=0.12

def trial(target, seed, error_rate, policy):
    if target not in TARGETS or seed not in SEEDS or error_rate not in RATES or policy not in POLICIES:
        raise ValueError("Unknown experiment fixture")
    tape_rng=random.Random(target*100003+seed)
    noise_rng=random.Random(target*7117+seed*17+909)
    tape=[tape_rng.randrange(SPACE) for _ in range(1800)]
    seen=set(); low=0; high=SPACE-1
    calls=proposals=hints=incorrect=0
    scores=[];abstentions=0;range_resets=0
    # The guarded strategy disables range filtering after contradictory
    # evidence, but never pretends a noisy hint is verified. This is a simple
    # predetermined policy, not trained noise detection.
    guidance_active=policy!="ledger"
    while calls<EVAL_LIMIT and proposals<len(tape):
        guess=None
        while proposals<len(tape):
            candidate=tape[proposals];proposals+=1
            if candidate in seen:continue
            if guidance_active and not (low<=candidate<=high):continue
            guess=candidate;break
        if guess is None:
            if guidance_active and policy=="guarded":
                guidance_active=False
                low,high=0,SPACE-1
                range_resets+=1
                continue
            abstentions=EVAL_LIMIT-calls
            break
        seen.add(guess)
        calls+=1
        score=1-abs(guess-target)/63
        scores.append(score)
        if guidance_active and guess!=target:
            hints+=1
            actual="low" if guess<target else "high"
            is_wrong=noise_rng.random()<error_rate
            observed=("high" if actual=="low" else "low") if is_wrong else actual
            incorrect+=int(is_wrong)
            if observed=="low":low=max(low,guess+1)
            else: high=min(high,guess-1)
            if low>high and policy=="guarded":
                guidance_active=False;low,high=0,SPACE-1;range_resets+=1
    return {"best_reward":round(max(scores) if scores else 0.0,6),
            "exact_match":target in seen,
            "evaluations":calls,"unused_evaluations":EVAL_LIMIT-calls,
            "proposals_examined":proposals,"hints":hints,"wrong_hints":incorrect,
            "range_resets":range_resets,"stopped_without_budget":abstentions>0,
            "total_cost":round(EVAL_COST*calls+PROPOSAL_COST*proposals+HINT_COST*hints,6)}

def benchmark():
    rows=[]
    for rate in RATES:
        for target_index,target in enumerate(TARGETS):
            for seed in SEEDS:
                for policy in POLICIES:
                    rows.append({"error_rate":rate,"task":target_index,"seed":seed,
                                 "policy":policy,**trial(target,seed,rate,policy)})
    summary=[]
    for rate in RATES:
        for policy in POLICIES:
            subset=[x for x in rows if x["error_rate"]==rate and x["policy"]==policy]
            n=len(subset)
            summary.append({"error_rate":rate,"policy":policy,"trials":n,
                            "exact_matches":sum(x["exact_match"] for x in subset),
                            "mean_best_reward":round(sum(x["best_reward"] for x in subset)/n,6),
                            "evaluation_calls":sum(x["evaluations"] for x in subset),
                            "unused_evaluations":sum(x["unused_evaluations"] for x in subset),
                            "proposals_examined":sum(x["proposals_examined"] for x in subset),
                            "hints":sum(x["hints"] for x in subset),
                            "wrong_hints":sum(x["wrong_hints"] for x in subset),
                            "mean_total_cost":round(sum(x["total_cost"] for x in subset)/n,4)})
    return {"schema":"scout-noisy-guidance-pilot-v0",
      "design":"12 synthetic targets x 12 seeds x 4 oracle-error rates x 3 fixed policies",
      "cost_units":{"evaluation":EVAL_COST,"proposal_inspection":PROPOSAL_COST,"directional_hint":HINT_COST},
      "summary":summary,"trials":rows,
      "limitations":["Wrong hints are deterministic simulated flips, not realistic ambiguous criticism.",
                     "The guarded policy only detects impossible intervals, not subtle misleading feedback.",
                     "Different arms can leave evaluation budget unused. This is recorded rather than hidden.",
                     "Cost units are illustrative and are not measured GPU, latency or model token prices.",
                     "No trained models, agent orchestration, scientific discovery, or production services tested."],
      "outreach_authorized":False,"publication_authorized":False,
      "production_adoption":"NOT_AUTHORIZED"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    if a.out.exists():raise SystemExit("Refusing to overwrite")
    result=benchmark()
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],indent=2))
if __name__=="__main__":main()
