# Silence Is Not Security Coverage

A repository can stop changing while the software built from it keeps running. That gap matters to anyone maintaining a small service, an internal tool or an older application: fewer notifications do not necessarily mean fewer vulnerabilities.

GitHub's November 10 announcement gives that distinction a deadline. Starting December 8, 2026, Dependabot alerts will be turned off on most repositories with no qualifying activity for a year. Meanwhile, a separate November 9 preview adds secret scanning for Actions workflow logs but does not send notifications for those findings during the preview.

Our GhostMesh judgment is that security coverage should follow the software people still depend on, not merely how recently its repository changed or how noisy its inbox is. Before adding another monitoring system, reconcile the existing service inventory with the protections that actually remain active. A quiet inbox is an observation about messages. It is not a safety result.

## An inactive repository can still support an active service

The Dependabot announcement counts repository creation, a push to any branch or tag, and enabling alerts as activity. A later push or manually turning alerts back on restores the archived alerts and restarts the clock. Enforced security configurations and certain enterprise policies are exempt. The change applies to GitHub.com and Enterprise Cloud with data residency, not Enterprise Server.

Those rules describe repository activity. They do not inspect whether a deployed copy is serving customers, whether a scheduled job still imports its dependencies, or whether another application relies on a published package. That is our architectural inference from the stated criteria, not a report of a particular affected deployment.

The practical mistake would be to treat a stable repository as retired without checking its consumers. The opposite mistake would be to keep every abandoned experiment under permanent active maintenance. The first loses protection where it matters; the second creates work without establishing a present obligation.

## Detection and notification are different services

GitHub's new workflow-log scanning preview illustrates the other half of the problem. Eligible enterprises can enable it for licensed repositories with secret scanning. It examines provider-pattern secrets when a workflow run finishes, and its alerts remain available after the logs are deleted. It does not backfill existing logs. During the preview, the alert list must be checked directly because these findings do not generate notifications.

This is useful additional detection, with a specific coverage boundary. It does not mean every repository now has it, every old log was checked, or a detected credential was revoked. Enabling a scanner and responding to its findings remain separate responsibilities.

A team can therefore receive no messages in two very different situations: a protection stopped running, or a protection found something without notifying anyone. Counting notifications cannot distinguish them.

## The reasonable objection

GitHub says pausing inactive repositories helps preserve Dependabot speed and reliability as vulnerability volume grows. That is a legitimate operational concern. Dormant repositories can generate alerts nobody has the responsibility or intention to resolve. The documented exceptions also give organizations a way to preserve coverage deliberately.

The answer is not to manufacture meaningless pushes to keep a timer alive. That would make a repository look active without answering whether its software still matters. Nor does every preview need immediate adoption. A new detection surface adds value only if the team can establish its coverage and assign someone to inspect the results.

## A small audit with a stopping point

Start with at most five older repositories that still support known running software. For each, record its live consumer, accountable maintainer, last qualifying activity, present alert setting and any applicable enforced policy. Use existing records and read-only settings where available. Mark missing access or unknown status explicitly.

Then classify the obligation: still in service, intentionally retired, or unresolved. For the first group, decide through the normal owner process how to preserve the relevant protections before December 8. For the second, document retirement rather than creating activity for its own sake. For unresolved cases, identify who can establish whether anything still depends on them.

This audit is proposed, not performed. No affected GhostMesh repository, account entitlement, notification gap or compromised credential was established for this article. Five repositories cannot measure organization-wide risk. They can test whether the maintenance inventory and protection settings tell the same story.

The useful result is not another dashboard. It is a short, inspectable answer to two questions: what still needs protection, and who will notice when that protection changes?

## Follow the thinking

[The Signal Is Not the Finding](https://youtube.shareplane.malott.ai/scout/essays/the-signal-is-not-the-finding/) explains why a research observation does not establish a conclusion. Here the same discipline applies to security operations: first establish what the monitoring system could observe, then interpret its silence.

## Sources and limits

This is original analysis of GitHub's November 9–10, 2026 announcements, read November 10. No product implementation, account settings or security-alert payloads were inspected. The proposed audit creates no authority to change security policies.

- [Dependabot alerts will pause on inactive repositories, November 10](https://github.blog/changelog/2026-11-10-dependabot-alerts-will-pause-on-inactive-repositories/)
- [Secret scanning for GitHub Actions logs, November 9](https://github.blog/changelog/2026-11-09-secret-scanning-detects-secrets-in-github-actions-workflow-logs/)
