# Scout capability evidence intake

Issue [#69](https://github.com/pinklon/ghostmesh-readers/issues/69) needs a bridge from a changed feed item or page heading to a reviewable first-party source. `scripts/scout_provider_evidence.py` provides that bridge inside the existing daily Scout Provider Release Watch workflow. It creates a third, 30-day, review-only artifact named `scout-provider-evidence-<run-id>`.

The script binds each candidate to the same run's observation and the six-source registry. RSS entry URLs must stay on the registered source host. A changed HTML heading is tied to the observed heading-window digest; a later change in the page bytes becomes `STALE_SOURCE`. It fetches at most the observer's existing two-megabyte limit and retains up to 2,000 characters of visible official context near the observed title or heading. The artifact also carries the entire six-source health matrix, including unknown sources. It does not retain full third-party pages.

```sh
python3 scripts/scout_provider_evidence.py \
  --candidates scout-provider-candidates.json \
  --observations scout-provider-observations.json \
  --registry content/scout/provider-sources.json \
  --output scout-provider-evidence.json
python3 -m unittest discover -s tests -p 'test_scout_provider*.py'
```

## Human assessment boundary

1. Open the linked original source. Check the exact product, date, claim, scope and whether the source is a first-party announcement, documentation revision or merely a feed/title change. Keep the Decisions API GA announcement and Agents API DevDay announcement distinct. Record a stable capability identity only after that reading; a heading window has no such identity.
2. Separate provider-reported status from independently tested behavior. Record announcement, preview, GA, changed terms, deprecation, region, plan and account entitlement only where the specific evidence supports each. Preserve `UNKNOWN` for missing evidence, outages or stale capture. Public provider documentation cannot prove entitlement in Tony's account.
3. Compare the incumbent option, GhostMesh/Hyperion/SharePlane fit, cost and prerequisites, strongest counterevidence and smallest reversible test. Do not infer a price from a label or perform paid, credentialed or production tests from this workflow.
4. Send an original, sanitized assessment through the existing independent editorial and owner approval path. Only an approved record may enter the unified public Research Library and a release event; source artifacts never become public capability posts automatically.

This increment makes source-grounded review possible, but **does not complete** semantic assessment, account verification, the approved capability record type in the #68 library, or a production report. GitHub Actions artifacts in this public repository may be accessible to repository readers, so do not put private account evidence or internal research in this lane.
