"""Offline Scout decision proposals from bounded experimental receipts.

Decision suggestions are deliberately non-executable. Feedback confidence is an
observable proxy (wrong hint rate only in a synthetic oracle test), not calibrated
probability or proof of independent model judgment.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

ACTIONS=("CONTINUE","FALLBACK","STOP","REQUEST_ESCALATION_REVIEW")

def decide(observation:dict, *, proposed_escalation_cost=4.0)->dict:
    required=("evaluations","unused_evaluations","proposals_examined","hints",
              "wrong_hints","best_reward","exact_match","total_cost")
    if any(k not in observation for k in required):
        raise ValueError("Incomplete trial receipt")
    used=observation["evaluations"]
    remaining=observation["unused_evaluations"]
    hints=observation["hints"]
    wrong=observation["wrong_hints"]
    if not all(type(observation[k]) is int and observation[k]>=0
               for k in ("evaluations","unused_evaluations","proposals_examined","hints","wrong_hints")):
        raise ValueError("Invalid counters")
    if hints<wrong or used+remaining!=12 or observation["proposals_examined"]<used:
        raise ValueError("Inconsistent trial counters")
    if proposed_escalation_cost<=0:
        raise ValueError("Escalation cost must be positive")
    confidence_proxy=(hints-wrong)/hints if hints else None
    # Only simulation receipts contain oracle truth about incorrect hints.
    # Real deployments MUST replace this with an independently calibrated signal.
    if observation["exact_match"] or observation["best_reward"]>=0.999:
        action="STOP";reason="SYNTHETIC_TARGET_SOLVED"
    elif hints>=3 and confidence_proxy is not None and confidence_proxy<0.8:
        action="FALLBACK";reason="SYNTHETIC_GUIDANCE_ERROR_ABOVE_THRESHOLD"
    elif remaining==0:
        action="REQUEST_ESCALATION_REVIEW";reason="EVALUATION_BUDGET_EXHAUSTED"
    elif remaining>0 and used>=4 and observation["best_reward"]<0.90:
        action="REQUEST_ESCALATION_REVIEW";reason="LOW_SYNTHETIC_REWARD_AFTER_MULTIPLE_EVALUATIONS"
    else:
        action="CONTINUE";reason="NO_STOP_OR_REVIEW_TRIGGER"
    return {"action":action,"reason":reason,
            "confidence_proxy":round(confidence_proxy,4) if confidence_proxy is not None else None,
            "confidence_source":"SYNTHETIC_ORACLE_WRONG_HINT_LABEL",
            "modeled_escalation_cost":proposed_escalation_cost,
            "escalation_executed":False,"contact_authorized":False,
            "note":"Review request is not authority to invoke models or spend money."}

def summarize(experiment:dict)->dict:
    if experiment.get("schema")!="scout-noisy-guidance-pilot-v0":
        raise ValueError("Unexpected experiment schema")
    if experiment.get("production_adoption")!="NOT_AUTHORIZED" or experiment.get("publication_authorized") is not False:
        raise ValueError("Requires research-only experiment")
    counts={}
    for row in experiment["trials"]:
        cohort=f'{row["policy"]}@{int(row["error_rate"]*100)}pct'
        result=decide(row)
        counts.setdefault(cohort,Counter())[result["action"]]+=1
    return {"schema":"scout-feedback-policy-review-v0",
            "cases":len(experiment["trials"]),
            "cohorts":{name:dict(c) for name,c in sorted(counts.items())},
            "policy":"Fixed heuristic demonstration, not learned or validated",
            "calibration":"NONE","real_feedback_supported":False,
            "model_invocation_authorized":False,"outreach_authorized":False,
            "publication_authorized":False,
            "limitations":["Wrong-hint counts are privileged ground truth in synthetic simulations; unavailable for real-world critiques",
                           "No calibrated escalation expected value or measured strong-model cost",
                           "Request escalation is review only, never dispatch authority",
                           "Counts describe heuristic behavior, not measured improvement from taking the suggested action"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--experiment",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    result=summarize(json.loads(a.experiment.read_text(encoding="utf-8")))
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":result["cases"],"cohorts":result["cohorts"]},indent=2))
if __name__=="__main__":main()
