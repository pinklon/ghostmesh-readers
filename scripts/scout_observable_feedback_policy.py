"""Observable-only Scout decision triage for offline receipts.

Never reads oracle-only wrong_hints or the injected error_rate in decisions.
Labels are non-executable, and empirical utility is not established.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

ACTIONS={"CONTINUE","FALLBACK","STOP","REQUEST_ESCALATION_REVIEW"}
def decide_observable(row:dict)->dict:
    # Intentionally narrow allowlist. Wrong-hint oracle labels and injected
    # noise-rate must not contribute to an action.
    keys=("policy","evaluations","unused_evaluations","proposals_examined",
          "hints","range_resets","best_reward","exact_match")
    if any(k not in row for k in keys):raise ValueError("Missing observable input")
    policy=row["policy"]
    if policy not in {"ledger","always_guided","guarded"}:raise ValueError("Unknown source policy")
    calls,unused,examined,hints,resets=(row[k] for k in keys[1:6])
    if any(type(x)!=int or x<0 for x in (calls,unused,examined,hints,resets)):raise ValueError("Malformed counters")
    if calls+unused!=12 or examined<calls:raise ValueError("Inconsistent observation")
    best=row["best_reward"]
    if type(best) not in (float,int) or not 0<=best<=1:raise ValueError("Invalid observed reward")
    if type(row["exact_match"]) is not bool:raise ValueError("Invalid completion witness")
    overhead=examined/max(1,calls)
    if row["exact_match"]:
        action,reason="STOP","OBSERVED_TARGET_SUCCESS"
    elif policy!="ledger" and resets>0:
        action,reason="FALLBACK","OBSERVED_RANGE_CONTRADICTION"
    elif policy!="ledger" and examined>=120 and overhead>=10:
        action,reason="FALLBACK","HIGH_PROPOSAL_INSPECTION_OVERHEAD"
    elif unused==0:
        action,reason="REQUEST_ESCALATION_REVIEW","EVALUATION_BUDGET_EXHAUSTED"
    elif calls>=4 and best<0.9:
        action,reason="REQUEST_ESCALATION_REVIEW","LOW_OBSERVED_REWARD"
    else:
        action,reason="CONTINUE","NO_OBSERVABLE_TRIGGER"
    return {"action":action,"reason":reason,"observed_overhead_ratio":round(overhead,3),
            "feedback_quality":"UNVERIFIED","real_world_calibration":"NONE",
            "escalation_executed":False,"production_authorized":False}

def summarize(experiment:dict)->dict:
    if experiment.get("schema")!="scout-noisy-guidance-pilot-v0" or experiment.get("production_adoption")!="NOT_AUTHORIZED":
        raise ValueError("Only the offline noisy pilot is accepted")
    if experiment.get("publication_authorized") is not False or experiment.get("outreach_authorized") is not False:
        raise ValueError("No publication or outreach authority")
    results=[];actions=Counter()
    by_group={}
    for row in experiment["trials"]:
        d=decide_observable(row)
        # Hindsight uses injected truth solely for evaluation AFTER decision.
        # This label is deliberately withheld from decide_observable.
        truth=row["wrong_hints"]
        actual_rate=truth/row["hints"] if row["hints"] else None
        bad=(actual_rate is not None and actual_rate>=.25)
        grp=f'{row["policy"]}@{int(row["error_rate"]*100)}pct'
        actions[d["action"]]+=1
        stat=by_group.setdefault(grp,{"trials":0,"action_counts":Counter(),"fallback_with_bad_hints":0,
                                      "fallback_without_bad_hints":0,"bad_hints_without_fallback":0})
        stat["trials"]+=1;stat["action_counts"][d["action"]]+=1
        if d["action"]=="FALLBACK":
            stat["fallback_with_bad_hints"]+=int(bad)
            stat["fallback_without_bad_hints"]+=int(not bad)
        elif bad:stat["bad_hints_without_fallback"]+=1
        results.append({"task":row["task"],"seed":row["seed"],"source_policy":row["policy"],
                        "injected_error_rate_for_audit_only":row["error_rate"],**d})
    for stat in by_group.values():stat["action_counts"]=dict(stat["action_counts"])
    return {"schema":"scout-observable-policy-evaluation-v0","cases":len(results),
            "overall_actions":dict(actions),"cohorts":by_group,"actions":results,
            "hindsight_threshold_for_audit_only":.25,
            "limitations":["Oracle wrong-hint labels are used ONLY in retrospective evaluation, never policy inputs",
                           "The available receipts lack time-series reward and individual hint consistency checks; no real stagnation or independent contradiction assessment is possible",
                           "Failure to flag hidden misinformation is expected; count bad-hint cases missed, not just flagged",
                           "Comparing action labels is not measuring gains from taking actions; no model was escalated or halted",
                           "Cost and thresholds are fixed research heuristics, not calibrated economics"],
            "model_invocation_authorized":False,"publication_authorized":False,
            "outreach_authorized":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--experiment",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    x=summarize(json.loads(a.experiment.read_text(encoding="utf-8")))
    a.out.write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":x["cases"],"actions":x["overall_actions"],"cohorts":x["cohorts"]},indent=2))
if __name__=="__main__":main()
