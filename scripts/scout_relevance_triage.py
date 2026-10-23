"""Scout relevance triage v0: bounded topic tags, identity handles and source diversity.

No model inference, invented identities, automated introduction or importance scoring.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

TOPICS = {
 "agent-authority": ("authorization", "permission", "policy-as-code", "agent sandbox", "access control", "least privilege", "credential"),
 "agent-continuity": ("durable execution", "agent memory", "long term memory", "persistent memory", "checkpoint", "recovery", "continuity"),
 "evidence-and-evaluation": ("provenance", "verification", "evals", "benchmark", "reproducibility", "audit", "ground truth"),
 "model-infrastructure": ("inference", "vllm", "quantization", "model serving", "gpu", "long context", "open weights"),
 "human-ai-collaboration": ("human ai", "collaboration", "co-creation", "sensemaking", "human in the loop"),
 "agent-interoperability": ("mcp", "agent protocol", "interoperability", "agent2agent", "a2a"),
}
# Different topic labels can coexist; matches are leads to examine, not proof of relevance.
GAPS = {
 "agent-authority": "GhostMesh action authority, credential boundaries and runtime admission",
 "agent-continuity": "durable agent state, failure recovery and work ownership",
 "evidence-and-evaluation": "independently checkable claim evidence and evaluation fixtures",
 "model-infrastructure": "Hyperion local-model serving, diversity and inference efficiency",
 "human-ai-collaboration": "source-preserving collaborative reasoning and dissent",
 "agent-interoperability": "cross-system agent interfaces and model/provider interchangeability",
}
def tokens(text: str) -> str:
    return " " + re.sub(r"[^a-z0-9]+"," ",text.lower()) + " "

def classify(lead: dict) -> dict:
    title=lead.get("title") or ""
    desc=lead.get("description") or ""
    combined=tokens(title+" "+desc)
    tags=[topic for topic,needles in TOPICS.items()
          if any(" "+re.sub(r"[^a-z0-9]+"," ",needle.lower()).strip()+" " in combined for needle in needles)]
    uri=urlsplit(lead["url"])
    identity = None
    # A repository owner is an observed handle, not an independently verified person.
    if uri.hostname in {"github.com","www.github.com"}:
        parts=[x for x in uri.path.split("/") if x]
        if len(parts)>=2:
            identity={"type":"repository_owner_handle","value":parts[0],"verified_person":False}
    if not identity and lead.get("source")=="independent-builder":
        identity={"type":"source_feed_identity","value":"simonwillison.net","verified_person":False}
    return {"url":lead["url"],"title":title,"source":lead["source"],
            "topics":tags,"identity":identity,
            "ghostmesh_questions":[GAPS[t] for t in tags],
            "relevance_status":"KEYWORD_CANDIDATE" if tags else "UNKNOWN",
            "evidence_status":"SOURCE_METADATA_ONLY",
            "collaboration_status":"NOT_EVALUATED",
            "outreach_authorized":False}

def triage(intake: dict) -> dict:
    if intake.get("schema")!="scout-multisource-intake-v0":
        raise ValueError("Invalid Scout intake")
    entries=[classify(x) for x in intake["sampled_leads"]]
    by_topic=defaultdict(list); by_identity=defaultdict(list)
    for e in entries:
        for tag in e["topics"]:by_topic[tag].append(e)
        if e["identity"]:
            key=e["identity"]["type"]+":"+e["identity"]["value"].lower()
            by_identity[key].append(e)
    return {"schema":"scout-relevance-triage-v0","captured_utc":intake.get("captured_utc"),
            "total_leads":len(entries),
            "topic_groups":[{"topic":topic,"leads":len(xs),"sources":sorted(set(x["source"] for x in xs)),
                             "cross_source_topic":len(set(x["source"] for x in xs))>1,
                             "sample_titles":[x["title"] for x in xs[:5]]}
                            for topic,xs in sorted(by_topic.items())],
            "recurring_source_handles":[{"handle":key,"observations":len(xs),"source_count":len(set(x["source"] for x in xs))}
                                        for key,xs in sorted(by_identity.items()) if len(xs)>1],
            "entries":entries,
            "limits":["Topic groups share vocabulary, not established claims or common origin",
                      "Feed handle or repository owner is not verified personal identity",
                      "No ranking, measured virality, social relationships or collaboration readiness",
                      "Unmatched leads retained with UNKNOWN relevance"],
            "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--intake",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    data=triage(json.loads(a.intake.read_text(encoding="utf-8")))
    a.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"total_leads":data["total_leads"],"topic_groups":data["topic_groups"],
                      "recurring_source_handles":data["recurring_source_handles"]},indent=2))
if __name__=="__main__":main()
