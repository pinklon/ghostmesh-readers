"""Work-based Scout complementarity triage, using public paper abstracts, not popularity.

Outputs review prompts for work records. Names are unverified attribution labels.
"""
from __future__ import annotations
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

QUESTIONS={
 "evidence-reliability":("verification","provenance","ground truth","evaluation","uncertainty","calibration","hallucination","confidence"),
 "durable-agents":("agent memory","persistent memory","long term memory","stateful agent","recovery","checkpoint","multi-agent"),
 "model-efficient-compute":("efficient inference","small language model","tokenization","quantization","latency","serving"),
 "collaborative-epistemics":("collaborative reasoning","sensemaking","human ai","deliberation","debate","consensus"),
 "interoperability":("protocol","tool use","agentic workflow","mcp","interoperability","agent skills"),
}
def words(s):
 return " "+re.sub(r"[^a-z0-9]+"," ",s.lower())+" "
def matches(title,abstract):
 text=words(title+" "+abstract)
 out={}
 for topic,terms in QUESTIONS.items():
  hits=[term for term in terms if " "+words(term).strip()+" " in text]
  if hits:out[topic]=hits
 return out
def screen(people,feed):
 if people.get("schema")!="scout-private-work-profiles-v0":
  raise ValueError("Missing private work profiles")
 if people.get("publication_authorized") is not False or people.get("outreach_authorized") is not False:
  raise ValueError("Invalid research authority")
 if len(feed)>2500000:raise ValueError("RSS too large")
 root=ET.fromstring(feed)
 papers={}
 for item in root.findall(".//item"):
  link=item.findtext("link","").strip()
  if link.startswith("https://arxiv.org/abs/"):
   papers[link]=(item.findtext("title",""),item.findtext("description",""))
 results=[]
 for person in people["profiles"]:
  if person.get("contact_authorized") is not False or person.get("identity_verified") is not False:
   raise ValueError("Unverified identity required")
  source=person["source_work"]
  paper=papers.get(source)
  if not paper:
   results.append({"attribution_id":person["id"],"label":person["display_label"],
                   "work_url":source,"state":"SOURCE_CONTEXT_MISSING",
                   "topics":{},"collaboration_merit":"NOT_EVALUATED"})
   continue
  title,abstract=paper
  hits=matches(title,abstract)
  results.append({"attribution_id":person["id"],"label":person["display_label"],
                  "work_url":source,"work_title":title,
                  "abstract_excerpt":re.sub(r"\s+"," ",abstract).strip()[:750],
                  "state":"METADATA_REVIEW_CANDIDATE" if hits else "NO_VOCABULARY_MATCH",
                  "topics":hits,
                  "possible_ghostmesh_question":"Compare work against actual current GhostMesh gaps; do not presume missing capability" if hits else None,
                  "strongest_objection":"Abstract relevance is not originality, implementation validation or collaborator fit" if hits else None,
                  "proposed_next_step":"Read source and find disconfirming evidence" if hits else None,
                  "collaboration_merit":"NOT_EVALUATED","identity_verified":False,"contact_authorized":False})
 work_index={}\n for x in results:\n  if x["state"]=="METADATA_REVIEW_CANDIDATE":\n   item=work_index.setdefault(x["work_url"],{"work_url":x["work_url"],"title":x["work_title"],"topics":x["topics"],"attribution_count":0,"review_state":"SOURCE_REVIEW_REQUIRED"})\n   item["attribution_count"]+=1\n return {"schema":"scout-work-complementarity-v0","screened":len(results),\n         "matched_works":len(work_index),"work_review_queue":list(work_index.values()),
         "metadata_candidates":sum(x["state"]=="METADATA_REVIEW_CANDIDATE" for x in results),
         "results":results,
         "limits":["Topic match derives from titles and abstracts only",
                   "No work is ranked by followers, citation counts, stars or social visibility",
                   "Author names are not disambiguated or cross-linked to GitHub accounts",
                   "No assessments of originality, expertise or collaborator interest"],
         "publication_authorized":False,"outreach_authorized":False}
def main():
 p=argparse.ArgumentParser()
 for name in ("profiles","rss","out"):p.add_argument("--"+name,required=True,type=Path)
 a=p.parse_args()
 if a.out.exists():raise SystemExit("Refusing to overwrite")
 data=screen(json.loads(a.profiles.read_text()),a.rss.read_bytes())
 a.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({"screened":data["screened"],"metadata_candidates":data["metadata_candidates"]}))
if __name__=="__main__":main()
