"""Offline three-way stop/continue/bounded-probe comparison.

At a predeclared step-10 checkpoint: STOP, CONTINUE, or PROBE up to four
further evaluations, then continue only if observed improvement warrants it.
Probe is simulated extra work, *not* a model or an oracle forecasting outcomes.
No decisions inspect reward observations from the future.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from scout_heldout_stop_stress import REGIMES, TEST_SEEDS, BUDGET, trajectory

CHECKPOINT=10
PROBE_STEPS=4
EVAL_COST=.00305
PROBE_REVIEW_COST=.008
IMPROVEMENT_GATE=.003
ACTIONS=("stop","continue","probe_then_decide")

def evaluate_path(values,action):
    if action not in ACTIONS or len(values)!=BUDGET:raise ValueError("Invalid fixture")
    pre=values[:CHECKPOINT]
    best_pre=max(pre)
    if action=="stop":
        used=CHECKPOINT
        probe=False
        decision="STOP"
    elif action=="continue":
        used=BUDGET
        probe=False
        decision="CONTINUE"
    else:
        # Probe sees four actual incremental observations. The continuation
        # decision depends ONLY on the new observations, never on steps 15-20.
        observed=values[CHECKPOINT:CHECKPOINT+PROBE_STEPS]
        improved=max(observed)>best_pre+IMPROVEMENT_GATE
        used=BUDGET if improved else CHECKPOINT+PROBE_STEPS
        probe=True
        decision="PROBE_THEN_CONTINUE" if improved else "PROBE_THEN_STOP"
    achieved=max(values[:used])
    return {"action":action,"decision":decision,"steps_used":used,
            "probe_review_charged":probe,
            "reward":round(achieved,6),
            "total_cost":round(used*EVAL_COST+int(probe)*PROBE_REVIEW_COST,6),
            "net_utility":round(achieved-used*EVAL_COST-int(probe)*PROBE_REVIEW_COST,6)}

def benchmark():
    rows=[]
    for regime in REGIMES:
        for seed in TEST_SEEDS:
            stream=trajectory(regime,seed)
            full=max(stream)
            outcomes={action:evaluate_path(stream,action) for action in ACTIONS}
            for action,out in outcomes.items():
                rows.append({"regime":regime,"seed":seed,**out,
                             "regret_vs_full":round(full-out["reward"],6),
                             "utility_delta_vs_continue":round(out["net_utility"]-outcomes["continue"]["net_utility"],6)})
    summary=[]
    for regime in REGIMES:
        for action in ACTIONS:
            subset=[r for r in rows if r["regime"]==regime and r["action"]==action]
            n=len(subset)
            summary.append({"regime":regime,"action":action,"trials":n,
                            "mean_reward":round(sum(r["reward"] for r in subset)/n,6),
                            "mean_total_cost":round(sum(r["total_cost"] for r in subset)/n,6),
                            "mean_utility_delta_vs_continue":round(sum(r["utility_delta_vs_continue"] for r in subset)/n,6),
                            "premature_terminals":sum(r["regret_vs_full"]>.001 for r in subset),
                            "mean_regret_vs_full":round(sum(r["regret_vs_full"] for r in subset)/n,6),
                            "mean_steps_used":round(sum(r["steps_used"] for r in subset)/n,2)})
    return {"schema":"scout-three-way-extra-work-v0",
            "design":"Four deliberately adversarial synthetic trajectory families, 20 held-out seeds each, checkpoint step 10; probe observes four extra outcomes and incurs an explicit surcharge.",
            "checkpoint":CHECKPOINT,"probe_steps":PROBE_STEPS,
            "costs":{"evaluation":EVAL_COST,"probe_review_surcharge":PROBE_REVIEW_COST},
            "gate":"After four probes, continue only when best observed probe reward exceeds checkpoint best by 0.003.",
            "summary":summary,"rows":rows,
            "limitations":["Probe is four real simulated evaluations plus a fee, NOT a capable model, privileged oracle, or independent reasoning.",
                           "Every arm has identical available full synthetic reward stream, but incurs different observation costs.",
                           "The probe can miss breakthroughs occurring after its four-step window; its decisions use only observed rewards.",
                           "Reward values and cost units are synthetic and not calibrated to GhostMesh models or infrastructure.",
                           "The outcomes measure this fixed protocol; they do not justify model dispatch, spending or deployment."],
            "model_invocation_authorized":False,"production_adoption":"NOT_AUTHORIZED",
            "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    result=benchmark()
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],indent=2))
if __name__=="__main__":main()
