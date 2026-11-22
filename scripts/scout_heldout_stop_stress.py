"""Held-out premature-stop stress test with delayed rewards and explicit regret.

No model calls, no production actions. Rules are fixed before evaluation.
Generated trajectories are synthetic; test seeds are disjoint from development seeds.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

BUDGET=20
TEST_SEEDS=tuple(range(100,120))
REGIMES=("late_breakthrough","false_plateau","steady_progress","flat_noise")
RULES=("continue_all","stop_on_plateau","cautious_plateau")
EVAL_COST=.003
PROPOSAL_COST=.00005

def trajectory(regime,seed):
    if regime not in REGIMES or seed not in TEST_SEEDS:raise ValueError("Unknown held-out fixture")
    rng=random.Random(seed*941+REGIMES.index(regime)*10009)
    values=[]
    for step in range(BUDGET):
        jitter=rng.uniform(-.003,.003)
        if regime=="late_breakthrough":
            val=.79+step*.011 if step<5 else .845 if step<14 else .845+(step-13)*.022
        elif regime=="false_plateau":
            val=.94+step*.006 if step<6 else .970 if step<16 else .970+(step-15)*.006
        elif regime=="steady_progress":
            val=.75+step*.012
        else:
            val=.84+jitter*.8
        values.append(max(0,min(1,round(val+jitter,6))))
    return values

def decision(prefix,rule):
    if rule=="continue_all":return False
    if len(prefix)<5:return False
    recent=prefix[-4:]
    best=max(prefix)
    plateau=max(recent)-min(recent)<.008
    if rule=="stop_on_plateau":return plateau and best>=.83
    if rule=="cautious_plateau":return len(prefix)>=10 and plateau and best>=.97
    raise ValueError("Unknown policy")

def apply(values,rule):
    if len(values)!=BUDGET:raise ValueError("Invalid reward trajectory")
    step=BUDGET
    for i in range(1,BUDGET+1):
        if decision(values[:i],rule):step=i;break
    chosen=max(values[:step]);full=max(values)
    saved=(BUDGET-step)*(EVAL_COST+PROPOSAL_COST)
    missed=full-chosen
    return {"stop_step":step,"stopped_early":step<BUDGET,
            "best_at_stop":round(chosen,6),"best_full":round(full,6),
            "missed_gain":round(missed,6),"saved_cost":round(saved,6),
            "net_vs_continue":round(saved-missed,6)}

def benchmark():
    rows=[]
    for regime in REGIMES:
        for seed in TEST_SEEDS:
            values=trajectory(regime,seed)
            for rule in RULES:
                rows.append({"regime":regime,"seed":seed,"rule":rule,**apply(values,rule)})
    summary=[]
    for regime in REGIMES:
        for rule in RULES:
            group=[x for x in rows if x["regime"]==regime and x["rule"]==rule]
            summary.append({"regime":regime,"rule":rule,"trials":len(group),
                            "early_stops":sum(x["stopped_early"] for x in group),
                            "premature_stops":sum(x["missed_gain"]>.001 for x in group),
                            "mean_missed_gain":round(sum(x["missed_gain"] for x in group)/len(group),6),
                            "mean_saved_cost":round(sum(x["saved_cost"] for x in group)/len(group),6),
                            "mean_net_vs_continue":round(sum(x["net_vs_continue"] for x in group)/len(group),6)})
    return {"schema":"scout-heldout-stop-stress-v0",
        "design":"Four synthetic trajectory families; 20 held-out seeds (100..119) each; 20 observed steps; three fixed rules.",
        "rules":{"continue_all":"never stop","stop_on_plateau":"from step 5, best >= .83 and last-four reward spread < .008",
                 "cautious_plateau":"from step 10, best >= .97 and last-four reward spread < .008"},
        "cost_per_step":EVAL_COST+PROPOSAL_COST,
        "summary":summary,"rows":rows,
        "limitations":["Held-out seeds are disjoint, but trajectory families and rules were deliberately hand-designed for stress testing",
                       "Hindsight continuation measures regret after rules act, never feeds future outcomes to them",
                       "Not a statistically representative sample of GhostMesh workloads",
                       "Missed reward and saved expense share arbitrary normalized toy units",
                       "No actual stronger-model computation or causal evaluation of escalations"],
        "model_dispatch_authorized":False,"publication_authorized":False,
        "outreach_authorized":False,"production_adoption":"NOT_AUTHORIZED"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    b=benchmark()
    a.out.write_text(json.dumps(b,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(b["summary"],indent=2))
if __name__=="__main__":main()
