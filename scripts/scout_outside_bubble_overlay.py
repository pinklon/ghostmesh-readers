"""Add outside-bubble exploration and shadow-filter audit to existing Scout Discover view."""
from __future__ import annotations
import argparse,json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

def render(discovery_html,experiment):
    if "noindex,nofollow" not in discovery_html or "</main>" not in discovery_html:
        raise ValueError("Existing private Scout Discover page required")
    if experiment.get("schema")!="scout-outside-bubble-v0" or experiment.get("publication_authorized") is not False or experiment.get("outreach_authorized") is not False:
        raise ValueError("Private only")
    if experiment["topic_matched"]+experiment["outside_topic_vocabulary"]!=experiment["total"]:
        raise ValueError("Shadow coverage not reconciled")
    selected=experiment.get("outside_sample")
    if not isinstance(selected,list) or len(selected)!=experiment["outside_sampled"]:raise ValueError("Invalid sample")
    esc=lambda x:escape(str(x or ""),quote=True)
    h=['<section id="outside-the-bubble" class="gm-wide gm-section">',
       '<p class="gm-kicker">DISCOVERY / OUTSIDE THE BUBBLE</p>',
       '<h2>What would our topic filter miss?</h2>',
       '<p>Scout retained all ',str(experiment["total"]),' public signals. ',
       str(experiment["topic_matched"]),' matched the current topic vocabulary. ',
       str(experiment["outside_topic_vocabulary"]),' did not. A separate deterministic sample keeps ',
       str(experiment["outside_sampled"]),' visible across ',str(experiment["source_diversity"]),' source streams.</p>',
       '<p><strong>These are not verified missed discoveries.</strong> We cannot measure useful false negatives until a person reviews the underlying work. The sample rewards coverage diversity, not follower counts or popularity.</p>',
       '<div class="gm-list">']
    for item in selected:
        url=item.get("url")
        p=urlsplit(url or "")
        if p.scheme!="https" or not p.hostname or p.username or p.password:
            raise ValueError("Invalid sampled source")
        if item.get("human_review_result")!="NOT_REVIEWED" or item.get("outreach_authorized") is not False:
            raise ValueError("Premature review or contact claim")
        h.extend(['<article class="gm-item"><aside><span class="gm-meta">',
            esc(item["source"]),'</span><p>OUTSIDE TOPIC VOCABULARY</p><p>NOT REVIEWED</p></aside><div><h3><a target="_blank" rel="noopener noreferrer" href="',
            esc(url),'">',esc(item.get("title") or "Untitled work"),' ↗</a></h3>',
            '<p>Why selected: source-balanced exploration, not a claim of relevance or originality.</p>',
            '<p>Potential benefit and false-negative status: NOT EVALUATED.</p></div></article>'])
    h.extend(['</div><p class="gm-empty">Shadow-filter audit: nothing was removed from the original lead collection. Human labels are needed before evaluating precision, recall, or surprise.</p></section>'])
    return discovery_html.replace("</main>","".join(h)+"</main>",1)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ("discovery","outside","out"):ap.add_argument("--"+key,type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    a.out.write_text(render(a.discovery.read_text(encoding="utf-8"),json.loads(a.outside.read_text(encoding="utf-8"))),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
