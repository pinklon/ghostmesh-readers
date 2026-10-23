# Scout provider release watch

Owner scope: [#69](https://github.com/pinklon/ghostmesh-readers/issues/69), integrated with unified publication library [#68](https://github.com/pinklon/ghostmesh-readers/issues/68).

The scheduled GitHub Actions workflow `.github/workflows/scout-provider-watch.yml` runs daily at **15:17 UTC** (Pacific clock time varies with daylight saving) and via manual dispatch. It reads only public first-party sources in `content/scout/provider-sources.json`.

The Python standard-library observer fetches bounded RSS/Atom feeds or page headings. It preserves the official source URL, observation time, response SHA256, and candidate headings/feed items in a **30-day GitHub Actions artifact**. Feed failures are `unknown`, never zero releases. It does not claim that a page edit is a product launch. HTML page headings are change candidates requiring manual source review.

The source registry is an intentionally small first tranche. Add another provider only after verifying an official HTTPS release-note endpoint and adding its host to the collector allowlist. Some providers have only HTML release notes. The schema is deliberately not a generic crawler, JavaScript browser, or authenticated account inspector.

## Run locally

```sh
python3 -m unittest discover -s tests -p 'test_scout_provider_watch.py'
python3 scripts/scout_provider_watch.py --output scout-provider-observations.json
```

The output is **unreviewed observation**, not validated capability intelligence. It is not a public Scout article, event, sitemap entry, RSS item, deployment, credential check, or permission to adopt a product. GitHub repository artifacts may be accessible to repository readers, so include only publicly available source evidence, never private research packets or account data.

## Review and publish

1. Review the latest artifact, compare with prior observations, and independently open each relevant first-party announcement. Determine whether it is new, a repeated announcement, preview, general availability, plan/region expansion, retirement, or only a documentation change.
2. Record explicit source date, status, limits, pricing evidence, entitlement unknowns, applicability, risks and counterevidence. Do not turn source claims into independently measured outcomes.
3. Draft original public-safe research for owner editorial approval.
4. After #68's unified manifest is available, admit only reviewed records and a dated release event through the existing static generator and CI. Preserve editorial approval and exact-head merge authorization.
5. Verify Netlify's production routes independently. The watch itself never mutates `content/scout-public.json`, `content/public-release-events.json`, `site/`, or deploy configuration.

The watch intentionally has **no token write permission**, no pull request creation, no site updates and no automatic publication. Future source coverage and historical cross-run diffing can be added after this baseline is proven reliable. The artifacts give an observable trail, not yet a persistent semantic event register.
