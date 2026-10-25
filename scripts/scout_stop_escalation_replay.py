"""Offline stop-vs-continue replay of completed, fixed synthetic traces.

At each prefix the heuristic sees only recorded history. Hindsight continuation
is used strictly to score the decision, not to decide it. An escalation request
never invokes a model, and no strong-model counterfactual is fabricated.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

EVAL_PRICE=0.003
PROPOSAL_PRICE=0.00005
HINT_PRICE=0.001
PATIENCE=4
MIN_STEPS=5
THRESHOLD=0.985

def cost(trace):
    if not trace:return 0.0
    last=trace[-1]
    return (len(trace)*EVAL_PRICE+
            last["proposals_examined_after"]*PROPOSAL_PRICE+
            sum(bool(x["observed_hint"]) for x in trace)*HINT_PRICE)

def choice(prefix):
    """Deterministic decision from observed prefix, without later rewards."""
    if not prefix:raise ValueError("No observation")
    best=max(x["observed_reward"] for x in prefix)
    if best>=1.0-1e-9:return "STOP","OBSERVED_EXACT_TARGET"
    if len(prefix)>=MIN_STEPS:
        recent=[x["best_reward_after"] for x in prefix[-PATIENCE:]]
        if max(recent)-min(recent)<1e-9 and best>=THRESHOLD:
            return "STOP","HIGH_SCORE_STAGNATION"
        if len(prefix)>=9 and best<0.90:
            return "REQUEST_ESCALATION_REVIEW","LOW_REWARD_AFTER_BUDGET"
    return "CONTINUE","FURTHER_EVIDENCE_REQUESTED"

def score_pair(trace):
    if not trace:raise ValueError("Empty trace")
    for i,x in enumerate(trace):
        if x["before_decision"]["step"]!=i:raise ValueError("Unordered trace")
        if x["proposals_examined_after"]<0:raise ValueError("Invalid inspection count")
    full_best=max(x["observed_reward"] for x in trace)
    full_cost=cost(trace)
    stop_index=len(trace)
    action="CONTINUE"
    reason="RUN_COMPLETE"
    review_count=0
    for i in range(1,len(trace)+1):
        candidate,why=choice(trace[:i])
        if candidate=="REQUEST_ESCALATION_REVIEW":
            review_count+=1
            # Never execute an escalation; ordinary search continues.
        elif candidate=="STOP":
            stop_index=i
            action=candidate
            reason=why
            break
    prefix=trace[:stop_index]
    selected_best=max(x["observed_reward"] for x in prefix)
    selected_cost=cost(prefix)
    return {"stop_step":stop_index,"full_steps":len(trace),"final_action":action,
            "stop_reason":reason,"escalation_reviews_only":review_count,
            "best_with_policy":round(selected_best,6),
            "best_continue":round(full_best,6),
            "saved_cost":round(full_cost-selected_cost,6),
            "missed_gain":round(full_best-selected_best,6),
            "net_utility_policy":round(selected_best-selected_cost,6),
            "net_utility_continue":round(full_best-full_cost,6),
            "esc_model_invoked":False}

def evaluate(dataset):
    if dataset.get("schema")!="scout-stepwise-counterfactual-v0":
        raise ValueError("Unexpected source")
    if dataset.get("production_adoption")!="NOT_AUTHORIZED" or dataset.get("publication_authorized") is not False:
        raise ValueError("Research only")
    rows=[]
    for pair in dataset["pairs"]:
        for arm in ("ledger","adaptive"):
            result=score_pair(pair[arm]["trace"])
            rows.append({"task":pair["task"],"seed":pair["seed"],"error_rate":pair["injected_noise"],"arm":arm,**result})
    aggregates=[]
    for rate in (0.0,.1,.3,.5):
        for arm in ("ledger","adaptive"):
            subset=[x for x in rows if x["error_rate"]==rate and x["arm"]==arm]
            aggregates.append({"error_rate":rate,"arm":arm,"trials":len(subset),
                "early_stops":sum(x["stop_step"]<x["full_steps"] for x in subset),
                "missed_improvements":sum(x["missed_gain"]>1e-8 for x in subset),
                "mean_saved_cost":round(sum(x["saved_cost"] for x in subset)/len(subset),6),
                "mean_missed_gain":round(sum(x["missed_gain"] for x in subset)/len(subset),6),
                "mean_net_delta":round(sum(x["net_utility_policy"]-x["net_utility_continue"] for x in subset)/len(subset),6),
                "escalation_review_requests":sum(x["escalation_reviews_only"] for x in subset)})
    return {"schema":"scout-stop-and-escalation-replay-v0",
        "decision_rule":{"minimum_steps":MIN_STEPS,"patience":PATIENCE,"high_score_threshold":THRESHOLD,
                         "review_only_low_reward_threshold":.90},
        "cost_units":{"evaluator_call":EVAL_PRICE,"proposal_inspection":PROPOSAL_PRICE,"hint":HINT_PRICE},
        "aggregates":aggregates,"rows":rows,
        "limits":["Hindsight full continuation scores regret only; future rewards are never used by the stop heuristic",
                  "Costs are illustrative toy weights, not dollars, tokens, GPU seconds or measured latency",
                  "Escalation requests are counted but no stronger-model or extra-work counterfactual exists",
                  "No action is executed on live GhostMesh systems",
                  "Decision thresholds were authored for this toy benchmark, so results are not out-of-sample validation"],
        "model_dispatch_authorized":False,"production_adoption":"NOT_AUTHORIZED",
        "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    data=evaluate(json.loads(a.source.read_text(encoding="utf-8")))
    a.out.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(data["aggregates"],indent=2))
if __name__=="__main__":main()
