# Public source aspect evidence

Checked: 2026-10-18T23:49:08.601355+00:00. This is a read-only public metadata check using `yt-dlp --dump-single-json --skip-download --no-playlist --no-warnings --no-cache-dir` on each catalog source URL. Only source ID and reported dimensions were retained; signed format URLs, media bytes, transcripts and private cookies were not saved. The dimensions agree with the explicit `source.mediaAspect` declaration for every current Reader. This does not independently validate the video's claims.

| Reader | Public source ID | Reported dimensions | Declared frame |
| --- | --- | ---: | --- |
| `a-challenge-is-not-a-verdict` | `DeUnZhWgPKd` | 1080 × 1920 | 9:16 |
| `ask-for-the-outcome-keep-the-boundary` | `NarezKh3w4o` | 1920 × 1080 | 16:9 |
| `autonomy-needs-an-interface` | `DdbCtAScTsk` | 3840 × 2160 | 16:9 |
| `make-good-work-inspectable` | `Z8lf5oWKfj0` | 3840 × 2160 | 16:9 |
| `the-agent-a-company-owns` | `HQXi4snP36I` | 3840 × 2160 | 16:9 |
| `the-funnel-is-not-the-frontier` | `BjO_JC6ujXs` | 1920 × 1080 | 16:9 |
| `the-inbox-was-a-boundary` | `rb4CTZjHCNg` | 1920 × 1080 | 16:9 |
| `the-fleet-does-not-prove-the-forecast` | `btUxMt_tssA` | 1920 × 1080 | 16:9 |
| `the-key-was-the-boundary` | `YaK6cnET2IE` | 3840 × 2160 | 16:9 |
| `the-microscope-is-not-a-soul` | `2oH1NACBgS4` | 1920 × 1080 | 16:9 |
| `the-scan-never-reached-the-login` | `8DKqcbEy-HM` | 1920 × 1080 | 16:9 |
| `the-score-is-not-the-system` | `ZhM29Ds-mBg` | 1920 × 1080 | 16:9 |
| `when-agents-become-the-customer` | `2DmP5etgh4U` | 3840 × 2160 | 16:9 |
| `when-software-becomes-legible` | `PseF3LyXQ04` | 1920 × 1080 | 16:9 |

The shared player uses the declared aspect, not the platform name. An unknown future source aspect requires a link-only fallback until its intrinsic dimensions are checked. A square frame requires 1:1 source evidence; portrait content remains portrait. Readers retain opt-in loading, external source links and timestamp navigation.

October 30 exception for Reader `the-model-is-not-the-demonstration`: Tony explicitly requested the existing opt-in YouTube viewer in the compact preview and article. The audio-only source capture does not establish intrinsic video dimensions; the source record therefore remains `mediaAspect: unknown`. Its approved player uses a 16:9 *viewing box*, not a claim about the video's native aspect. Both viewing surfaces retain the direct YouTube link and load the iframe only after a click. The article continues to disclose that video frames, exact speech and demonstrations were not verified. The metadata-only `yt-dlp` check attempted October 30 returned a DNS error and supplied no aspect evidence. Other unknown-aspect sources remain link-only unless separately approved.

The `btUxMt_tssA` row was added 2026-10-19 from the active ReasonPack public inspector's reported 1920 × 1080 dimensions, also confirmed by the private normalized pack's ffprobe record. It is a source-shape check, not a claim verification.
