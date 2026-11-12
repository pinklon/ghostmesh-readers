"""Offline per-step Scout decision traces and paired policy replay.

All decisions are made from past observations. Target and simulated wrong-hint
labels are used by the environment and AFTER replay only, never as policy inputs.
This is toy search, not evidence of real agent autonomy or SpecEvo replication.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

TARGETS=(5,18,31,44,57,9,22,35,48,61,14,53)
SEEDS=range(12)
RATES=(0.0,0.1,0.3,0.5)
BUDGET=12
SPACE=64
POLICIES=("ledger","adaptive")

def replay(target:int,seed:int,error_rate:float,policy:str)->dict:
    if target not in TARGETS or seed not in SEEDS or error_rate not in RATES or policy not in POLICIES:
        raise ValueError("Unsupported fixture")
    proposal_rng=random.Random(target*100003+seed)
    noise_rng=random.Random(target*7117+seed*17+909)
    tape=[proposal_rng.randrange(SPACE) for _ in range(1800)]
    cursor=0
    tested=set()
    low,high=0,SPACE-1
    guidance_enabled=policy=="adaptive"
    contradiction_count=0
    previous_best=-1
    trace=[]
    hints=0
    wrong_hints=0
    for step in range(BUDGET):
        # Before decision state: never include target, future candidate, correctness,
        # injected noise rate, or unobserved rewards.
        prior={"step":step,"best_reward_so_far":round(previous_best,6),
               "evaluations_used":step,"proposal_inspections":cursor,
               "hints_received":hints,"detected_contradictions":contradiction_count,
               "remaining_budget":BUDGET-step}
        if policy=="adaptive" and contradiction_count>0:
            guidance_enabled=False
        action="GUIDED_EXPLORE" if guidance_enabled else "INDEPENDENT_EXPLORE"
        guess=None
        while cursor<len(tape):
            value=tape[cursor];cursor+=1
            if value in tested:continue
            if guidance_enabled and not low<=value<=high:continue
            guess=value;break
        if guess is None and guidance_enabled:
            # Observable empty search region: fall back, do not invent a result.
            contradiction_count+=1
            guidance_enabled=False
            action="FALLBACK_AND_EXPLORE"
            while cursor<len(tape):
                value=tape[cursor];cursor+=1
                if value not in tested:
                    guess=value;break
        if guess is None:break
        tested.add(guess)
        score=1-abs(guess-target)/63
        previous_best=max(previous_best,score)
        observed_hint=None
        actual_wrong=None
        if guidance_enabled and guess!=target:
            hints+=1
            actual="low" if guess<target else "high"
            actual_wrong=noise_rng.random()<error_rate
            observed_hint=("high" if actual=="low" else "low") if actual_wrong else actual
            wrong_hints+=int(actual_wrong)
            if observed_hint=="low":low=max(low,guess+1)
            else:high=min(high,guess-1)
            if low>high:
                contradiction_count+=1
                guidance_enabled=False
        trace.append({"before_decision":prior,"action":action,
                      "observed_candidate":guess,"observed_reward":round(score,6),
                      "observed_hint":observed_hint,
                      "best_reward_after":round(previous_best,6),
                      "observed_contradiction_after":low>high,
                      "proposals_examined_after":cursor})
    return {"task":TARGETS.index(target),"seed":seed,"policy":policy,
            "injected_noise_for_audit_only":error_rate,"trace":trace,
            "final":{"evaluations":len(trace),"best_reward":round(previous_best,6),
                     "exact_match":target in tested,"proposal_inspections":cursor,
                     "hints":hints,"wrong_hints_for_audit_only":wrong_hints,
                     "cost_units":round(len(trace)+.002*cursor+.12*hints,5)}}

def run()->dict:
    pairs=[]
    for target in TARGETS:
        for seed in SEEDS:
            for rate in RATES:
                pairs.append({"task":TARGETS.index(target),"seed":seed,"injected_noise":rate,
                              "ledger":replay(target,seed,rate,"ledger"),
                              "adaptive":replay(target,seed,rate,"adaptive")})
    grouped=[]
    for rate in RATES:
        items=[x for x in pairs if x["injected_noise"]==rate]
        for policy in POLICIES:
            subset=[x[policy]["final"] for x in items]
            grouped.append({"error_rate":rate,"policy":policy,"trials":len(subset),
                            "exact_matches":sum(x["exact_match"] for x in subset),
                            "mean_best_reward":round(sum(x["best_reward"] for x in subset)/len(subset),6),
                            "mean_cost_units":round(sum(x["cost_units"] for x in subset)/len(subset),4),
                            "mean_proposals":round(sum(x["proposal_inspections"] for x in subset)/len(subset),3)})
    return {"schema":"scout-stepwise-counterfactual-v0","pairs":pairs,"summary":grouped,
            "evaluation_design":"Frozen seeded proposal streams, paired baseline/adaptive histories, same maximum 12 evaluations; action affects which candidate from common tape is evaluated.",
            "limitations":["The target is used by simulated evaluator, not by decision policy",
                           "Adaptive arm's guidance is privileged noisy directional truth; ledger baseline has no equivalent hint information",
                           "Outcome replay is synthetic environmental simulation, not off-policy inference from logged real agent trajectories",
                           "An agent policy has no verified access to truth about hints; wrong-hint counts appear only in retrospective final audit",
                           "Policy does not yet decide optimal stop or stronger-model escalation; those remain review-only proposals",
                           "Toy cost units exclude model runtime, operational risk, and authority requirements"],
            "model_invocation_authorized":False,"production_adoption":"NOT_AUTHORIZED",
            "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    result=run()
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],indent=2))
if __name__=="__main__":main()
