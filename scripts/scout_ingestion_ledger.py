"""Source-and-revision ledger shared by Scout's existing reconciliation pipeline.

A stable source identity and an explicitly observed revision are separate.
Unknown revisions never become invented version numbers. Every ingestion
attempt returns a receipt, including deferred or duplicate observations.
"""
from __future__ import annotations
import hashlib
import re
from urllib.parse import urlsplit
from scout_signal_reconcile import canonical_url

ARXIV=re.compile(r"^/abs/(\d{4}\.\d{4,5})(?:v(\d+))?/?$")
GITHUB_REPO=re.compile(r"^/([^/]+)/([^/]+)/?$")
GITHUB_REV=re.compile(r"^/([^/]+)/([^/]+)/(?:tree|commit)/([0-9a-fA-F]{40})/?$")
def identity_revision(url, explicit_revision=None):
    url=canonical_url(url)
    u=urlsplit(url)
    revision=None
    source=url
    if u.hostname=="arxiv.org":
        m=ARXIV.fullmatch(u.path)
        if m:
            source="arxiv:"+m[1]
            revision="v"+m[2] if m[2] else None
    elif u.hostname=="github.com":
        match=GITHUB_REV.fullmatch(u.path)
        if match:
            source="github:"+match[1].lower()+"/"+match[2].lower()
            revision=match[3].lower()
        else:
            match=GITHUB_REPO.fullmatch(u.path)
            if match:source="github:"+match[1].lower()+"/"+match[2].lower()
    if explicit_revision is not None:
        if not isinstance(explicit_revision,str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}",explicit_revision):
            raise ValueError("Invalid explicit revision")
        if revision is not None and revision!=explicit_revision:
            raise ValueError("Conflicting revision witnesses")
        revision=explicit_revision
    return source, revision

def record_ledger(observations, previously_seen=()):
    """Return immutable-style receipts; source ID and revision are the dedupe key.

    No timestamp-only drops. No speculation about current-version or deletion.
    """
    seen=set()
    for pair in previously_seen:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2 or not all(isinstance(x,str) for x in pair):
            raise ValueError("Invalid prior source-revision entry")
        seen.add(tuple(pair))
    receipts=[]
    for index,obs in enumerate(observations):
        if not isinstance(obs,dict):raise ValueError("Invalid observation")
        source,revision=identity_revision(obs["url"],obs.get("revision"))
        # Unknown revisions may be recognized as repeats, but their underlying
        # content is not proven unchanged. A content digest can be treated as a
        # separate observed revision only if actual captured bytes are provided.
        if revision is None and obs.get("capture_sha256") is not None:
            digest=obs["capture_sha256"]
            if not isinstance(digest,str) or not re.fullmatch(r"[0-9a-fA-F]{64}",digest):
                raise ValueError("Invalid captured payload hash")
            revision="sha256:"+digest.lower()
        key=(source,revision or "UNVERIFIED")
        state="SEEN_AGAIN_UNVERIFIED" if key in seen and revision is None else "DUPLICATE_REVISION" if key in seen else "ACCEPTED"
        seen.add(key)
        label=obs.get("author_name") or obs.get("label")
        if label is not None and (not isinstance(label,str) or not label.strip()):raise ValueError("Malformed author label")
        receipts.append({"index":index,"source_identity":source,"revision":revision,
             "state":state,"source_url":obs["url"],"author_label":label,
             "person_identity":"UNRESOLVED" if label else "NOT_PROVIDED",
             "source_content_verified":bool(obs.get("capture_sha256")),
             "outreach_authorized":False})
    return {"schema":"scout-ingestion-receipts-v0","receipts":receipts,
        "seen_keys":[list(x) for x in sorted(seen)],
        "accepted":sum(r["state"]=="ACCEPTED" for r in receipts),
        "duplicates":sum(r["state"]=="DUPLICATE_REVISION" for r in receipts),
        "unverified_reobservations":sum(r["state"]=="SEEN_AGAIN_UNVERIFIED" for r in receipts),
        "limitations":["An unversioned reobservation may contain changed content; do not silently claim equality",
                       "Author name labels are not resolved identities",
                       "A content hash witnesses bytes, not the truth of a source",
                       "Ordering timestamps are not used to discard arrivals"],
        "publication_authorized":False,"outreach_authorized":False}
