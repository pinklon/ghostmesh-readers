# Anthropic API and SDK changes introduced on October 21

## Release scope

Anthropic released API version `2026-10-21` alongside major client SDK and CLI releases on October 21, 2026. The first versions in this release are Python 2.0.0, TypeScript 1.0.0, C# 13.0.0, Go 2.0.0, Java 3.0.0, PHP 1.0.0, Ruby 2.0.0, and ant CLI 2.0.0. These changes were observed in the published documentation and source on October 27, 2026; they are not an October 27 announcement. [Official release notes](https://platform.claude.com/docs/en/release-notes/overview)

The useful operational distinction is between API-version changes and independent SDK changes. Pinning an API date alone is not a complete SDK-upgrade compatibility strategy.

## API contract changes

For `2026-10-21`, the official version history specifies:

| Surface | Change |
| --- | --- |
| Messages | Direct assistant-message document blocks return 400. |
| Messages | Non-empty citations on user-message text blocks return 400, including text inside search results. |
| Messages | `temperature`, `top_p`, and `top_k` return 400 on every model. |
| RBAC groups | `roles` becomes `role_ids`. |
| RBAC group members | `group_id` becomes `rbac_group_id`. |
| RBAC roles | `name` becomes `display_name`. |
| Rate-limit entries | `group_type` becomes `group.type`. |
| API-key responses | `workspace_id` becomes `scope`; workspace-bound keys identify the real workspace, while organization-wide scope has no workspace ID. |
| Enterprise per-user reports | `actor.email` becomes `actor.email_address`. |
| Enterprise activity summaries | `summaries` becomes `data`. |

On Bedrock, this API version is available only for Claude 4.7 and later. [API version history](https://platform.claude.com/docs/en/api/versioning)

## Independent SDK changes

The migration guide also identifies role-specific message unions; constants replacing single-value enums in C#, Go, Java, PHP and Ruby; removal of TypeScript/Ruby client-side tool-runner compaction; removal of legacy Text Completions from TypeScript, Go, Java, Ruby and CLI; moving Models beta arguments to beta methods; changed authentication headers and credential selection; and language-specific changes. The CLI removes credential-value command-line flags. These are separate from the API-date switch. Foundry's SDK API-key header is an explicit exception to the general bearer-header change. The service still accepts API keys in either header. [SDK and CLI migration sections](https://platform.claude.com/docs/en/api/migration-2026-10-21#sdk-and-cli-changes)

## Tagged Python source and license changes

Python's tagged source supplies a concrete before-and-after pair. In [v1.17.0 `_client.py`](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/v1.17.0/src/anthropic/_client.py), API-key authentication emits `X-Api-Key`; in [v2.0.0 `_client.py`](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/v2.0.0/src/anthropic/_client.py), it emits `Authorization: Bearer`. The latter documents mutually exclusive explicit credential inputs and selection of the API key when both static credential environment variables exist. Its [tagged constants](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/v2.0.0/src/anthropic/_constants.py) set the API date to `2026-10-21`.

Python [v1.17.0 LICENSE](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/v1.17.0/LICENSE) contains MIT license text; [v2.0.0 LICENSE](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/v2.0.0/LICENSE) contains Apache License 2.0. The [v2.0.0 release commit](https://github.com/anthropics/anthropic-sdk-python/commit/ecfee6cd504cfbf634919bdbd058fb74afdbd533) records Apache-2.0 package metadata. The official guide says earlier versions retain MIT and separately scopes platform-package releases. This is a package/source fact, not an interpretation of legal obligations or service access. [License migration section](https://platform.claude.com/docs/en/api/migration-2026-10-21#the-license-is-apache-20)

## Integration impact remains conditional

An upstream change does not establish that a particular integration is affected. That depends on its manifest, lockfile, deployed package, request serializer, proxy, and logging implementation. A pinned older SDK or an integration without these assumptions may be unaffected. A gateway or log filter that recognizes only the old API-key header is a plausible compatibility or redaction concern, not an established defect. No particular deployment has been inspected or runtime-tested for this assessment.

The documentation distinguishes general API SDKs from Claude Code, Claude Agent SDK, and Managed Agents. The license finding must not be generalized across those products. [Official tooling scope](https://platform.claude.com/docs/en/cli-sdks-libraries/overview)

## A read-only compatibility check

For an integration repository you are authorized to inspect, identify the exact locked Anthropic package and review tracked source and tests for `X-Api-Key`, `Authorization`, explicit API-version overrides, and sampling-parameter serialization. Record file and line references and whether matches affect gateway forwarding, redaction, or request construction; do not inspect secret values. Stop once the package version and relevant call sites are classified as affected, unaffected, or unknown. This produces a disposable local findings note without an installation, API call, environment-variable read, credential change, dependency edit, or publication. It is a proposed static check, not a completed compatibility test.
