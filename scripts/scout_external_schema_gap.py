"""Read-only Scout-to-InspectorRAGet field-loss audit, not a compatible importer.

Create candidate JSON task skeletons and explicitly identify GhostMesh semantics
that the external README's documented task fields do not automatically preserve.
No external code is installed or executed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

TASK_FIELDS={"task_id","task_type","input","contexts","targets"}
SCOUT_FIELDS={"source_url","source_kind","source_status","work_basis","ghostmesh_problem","complementarity","counterevidence","experiment","disposition","review_status"}
def audit(shortlist,comparison):
    if shortlist.get("schema")!="scout-connection-theses-v1" or comparison.get("schema")!="scout-external-capability-comparison-v0":
        raise ValueError("Wrong evidence schemas")
    for x in (shortlist,comparison):
        if x.get("outreach_authorized") is not False or x.get("publication_authorized") is not False:
            raise ValueError("Owner-private only")
    if not {x["id"] for x in comparison["candidates"]}=={"bottleneck","inspectorraget"}:
        raise ValueError("Missing source pair")
    tasks=[];loss={}
    for item in shortlist.get("theses",[]):
        if not SCOUT_FIELDS.issubset(item):raise ValueError("Missing Scout case field")
        # Only documented general task skeleton fields; claims about mapping
        # vendor-specific review state or annotations would be unverified.
        task={"task_id":item["id"],"task_type":"qa",
              "input":[{"role":"user","content":item["ghostmesh_problem"]}],
              "contexts":[],"targets":[{"type":"text","value":item["work_basis"]}]}
        if not set(task).issubset(TASK_FIELDS):raise ValueError("Undocumented key")
        tasks.append(task)
        loss[item["id"]]=sorted(SCOUT_FIELDS-{"work_basis","ghostmesh_problem"})
    return {"schema":"scout-external-schema-gap-audit-v0",
        "task_skeletons":tasks,"unmapped_fields_by_case":loss,
        "case_count":len(tasks),
        "externally_validated_import":False,"external_application_invoked":False,
        "claims":["Documented generic task layout can represent prompt and target text",
                  "Source revision, counterargument, review decision and authority semantics require deliberate extensions or separate representation"],
        "caveats":["Not a valid complete InspectorRAGet import document: metrics, models, results and other schema sections are absent",
                   "Task targets are evidence excerpts, not ground-truth answers",
                   "Read-only static schema exercise does not benchmark user workflows",
                   "No claim about external app support for arbitrary metadata fields"],
        "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser()
    for flag in ("shortlist","comparison","out"):p.add_argument("--"+flag,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    read=lambda p:json.loads(p.read_text(encoding="utf-8"))
    result=audit(read(a.shortlist),read(a.comparison))
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":result["case_count"],"distinct_unmapped_fields":sorted(set().union(*result["unmapped_fields_by_case"].values()))},indent=2))
if __name__=="__main__":main()
