"""Offline Scout late-arrival ingestion and ambiguous-author experiment.

Compare high-watermark timestamps with stable source-ID + revision receipts.
Neither strategy contacts services or resolves real identities.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path

# arrival order deliberately differs from publication order; records 7 and 11
# are revisions of prior works, record 10 repeats an already seen revision.
EVENTS=(
 {"id":"paper-a","rev":"v1","published":100,"arrived":100,"author":"Alex Kim","authority":None},
 {"id":"paper-b","rev":"v1","published":110,"arrived":110,"author":"Morgan Lee","authority":None},
 {"id":"paper-c","rev":"v1","published":105,"arrived":120,"author":"Alex Kim","authority":None},
 {"id":"paper-d","rev":"v1","published":130,"arrived":130,"author":"Taylor Chen","authority":"orcid:0000-0001-0000-0001"},
 {"id":"paper-e","rev":"v1","published":115,"arrived":140,"author":"Morgan Lee","authority":None},
 {"id":"paper-f","rev":"v1","published":150,"arrived":150,"author":"Alex Kim","authority":"orcid:0000-0002-0000-0002"},
 {"id":"paper-a","rev":"v2","published":100,"arrived":160,"author":"Alex Kim","authority":None},
 {"id":"paper-g","rev":"v1","published":155,"arrived":170,"author":"Taylor Chen","authority":"orcid:0000-0001-0000-0001"},
 {"id":"paper-h","rev":"v1","published":125,"arrived":180,"author":"Alex Kim","authority":"orcid:0000-0003-0000-0003"},
 {"id":"paper-i","rev":"v1","published":190,"arrived":190,"author":"Quinn Patel","authority":None},
 {"id":"paper-c","rev":"v1","published":105,"arrived":200,"author":"Alex Kim","authority":None},
 {"id":"paper-b","rev":"v2","published":110,"arrived":210,"author":"Morgan Lee","authority":None},
)
def validate(events):
    if len(events)!=12:raise ValueError("Fixture requires twelve arrival events")
    prior=-1
    for e in events:
        if set(e)!={"id","rev","published","arrived","author","authority"}:raise ValueError("Invalid event schema")
        if type(e["arrived"]) is not int or e["arrived"]<prior:raise ValueError("Arrival sequence invalid")
        if type(e["published"]) is not int or e["published"]<0:raise ValueError("Invalid publication clock")
        if not all(isinstance(e[k],str) and e[k] for k in ("id","rev","author")):raise ValueError("Missing source identity")
        if e["authority"] is not None and not str(e["authority"]).startswith("orcid:"):raise ValueError("Untrusted authority class")
        prior=e["arrived"]

def run(events=EVENTS):
    validate(events)
    cursor=-1
    seen=set()
    timestamp_accepted=[]
    ledger_accepted=[]
    timestamp_rejected=[]
    ledger_duplicates=[]
    for e in events:
        key=e["id"]+"@"+e["rev"]
        if e["published"]>cursor:
            timestamp_accepted.append(key)
            cursor=e["published"]
        else:
            timestamp_rejected.append(key)
        if key in seen:
            ledger_duplicates.append(key)
        else:
            seen.add(key)
            ledger_accepted.append(key)
    author_claims=defaultdict(lambda:{"unresolved":set(),"explicit_authorities":defaultdict(set)})
    for e in events:
        key=e["id"]+"@"+e["rev"]
        if e["authority"]:
            author_claims[e["author"]]["explicit_authorities"][e["authority"]].add(key)
        else:author_claims[e["author"]]["unresolved"].add(key)
    disambiguation=[]
    for name,group in sorted(author_claims.items()):
        authorities=group["explicit_authorities"]
        disambiguation.append({"display_name":name,
          "unresolved_sources":sorted(group["unresolved"]),
          "explicit_authority_clusters":[{"authority":a,"source_revisions":sorted(keys)}
                                          for a,keys in sorted(authorities.items())],
          "same_name_entity_merge_performed":False,
          "status":"REQUIRES_DISAMBIGUATION" if len(authorities)>1 or group["unresolved"] else "EXPLICIT_ID_ONLY"})
    return {"schema":"scout-late-arrival-identity-pilot-v0",
        "total_events":len(events),"distinct_source_revisions":len(seen),
        "timestamp_cursor":{"accepted":timestamp_accepted,"rejected":timestamp_rejected,
                            "accepted_count":len(timestamp_accepted)},
        "source_revision_ledger":{"accepted":ledger_accepted,"duplicates":ledger_duplicates,
                                  "accepted_count":len(ledger_accepted)},
        "late_or_revised_missed_by_cursor":sorted(set(ledger_accepted)-set(timestamp_accepted)),
        "author_labels":disambiguation,
        "limits":["Synthetic ordered-arrival fixture, not live external data",
                  "ORCID-like strings are simulated identifier claims, not validated registry records",
                  "A source-ID ledger alone does not prove fetched content or authorship",
                  "Revisions are separately retained; source revisions do not establish semantic change"],
        "publication_authorized":False,"outreach_authorized":False,
        "production_adoption":"NOT_AUTHORIZED"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    x=run()
    a.out.write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"events":x["total_events"],"timestamp_accepted":x["timestamp_cursor"]["accepted_count"],
       "ledger_accepted":x["source_revision_ledger"]["accepted_count"],
       "missed":x["late_or_revised_missed_by_cursor"],
       "author_name_clusters":len(x["author_labels"])},indent=2))
if __name__=="__main__":main()
