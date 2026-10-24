# Scout synthetic stopping replay receipt

Date: 2026-10-23
Scope: read-only, deterministic source replay for editorial evidence review.
Repository: pinklon/ghostmesh-readers
Source ref: research/scout-connection-thesis-v0
Publication status: NOT AUTHORIZED. Not a production experiment or model benchmark.

## Exact historical source blobs

| Program | Path | Git blob SHA |
| --- | --- | --- |
| Proposal-policy fixture | scripts/scout_speculative_search_pilot.py | 265d75d392b79e986c2afe957982f275ea833f91 |
| Held-out stopping stress | scripts/scout_heldout_stop_stress.py | c807e3b5d92efe7800d22d533b92c6608bb8a046 |
| Three-way probe | scripts/scout_three_way_extra_work.py | 2753367dcedf3d3b17f3f9151a3c2e1d7766c3a9 |
| Held-out source test | tests/test_scout_heldout_stop_stress.py | 153188da52fff33d0c6662fb3e782091cbbe7f1b |

These are Git blob identifiers obtained from the GitHub contents API. They are not SHA-256 checksums of newly copied files.

## Execution witness

The source text for the three programs was fetched from the exact historical ref, inspected, then passed to the existing local Python 3 interpreter using `python3 -B -c`. Each module's `benchmark()` function was called in memory. The two dependent programs were linked through a temporary in-process Python module namespace. The experiment CLI `--out` paths were not invoked. No source was installed, no files were written, and no model API, credential, network retrieval or GhostMesh service was used by the programs.

This is a **same-implementation replay of deterministic fixtures**, not an independent implementation, new empirical sample, or validation of the original research design. Environment version, CPU, and runtime timing were not qualified as performance variables.

## Exact observed comparisons

### Speculative one-dimensional search

Each strategy completed 144 trials and 1,728 synthetic evaluations.

| Policy | Mean best score | Exact matches | Repeated evaluations |
| --- | ---: | ---: | ---: |
| Random | 0.964286 | 20 | 132 |
| Success-only | 0.891314 | 40 | 513 |
| Failure-aware | 0.956680 | 75 | 0 |

All values matched the published `The Plateau That Lied` account.

### Held-out stopping stress

Four generated regimes, twenty seeds each, three rules, 240 rule-result rows.

| Regime | Basic premature stops | Cautious premature stops | Basic mean missed gain | Basic mean net versus continuing |
| --- | ---: | ---: | ---: | ---: |
| Late breakthrough | 20/20 | 0/20 | 0.129851 | -0.096300 |
| False plateau | 20/20 | 20/20 | 0.022025 | +0.012897 |
| Steady progress | 0/20 | 0/20 | 0 | 0 |
| Flat noise | 8/20 | 0/20 | 0.001160 | +0.042912 |

The late-breakthrough basic rule's mean saved cost was 0.033550. All values matched the retained research result description.

### Three-way stop / continue / probe

At step ten, the probe observed four more synthetic evaluations and charged an additional 0.008 review-cost unit. The probe used only observations available through its step-fourteen decision.

| Regime | Stop mean utility delta | Probe mean utility delta |
| --- | ---: | ---: |
| Late breakthrough | -0.099211 | -0.119110 |
| False plateau | +0.008640 | -0.011048 |
| Steady progress | -0.089656 | -0.008000 |
| Flat noise | +0.030262 | +0.010170 |

All values matched the retained research description. The probe did not outperform the better of stopping and continuing in these four designed regimes.

## Reviewer reproduction recipe

The historical research tip is pinned to commit `d46047390869ff372aa6239053ef882bd1b60a65` (open draft PR #65). At that commit, the three script blobs above match exactly. On an isolated local machine with Git and Python 3, run these commands in a disposable checkout:

```bash
git clone https://github.com/pinklon/ghostmesh-readers.git
cd ghostmesh-readers
git checkout --detach d46047390869ff372aa6239053ef882bd1b60a65
git hash-object scripts/scout_speculative_search_pilot.py scripts/scout_heldout_stop_stress.py scripts/scout_three_way_extra_work.py
python3 -B -c '
import sys
sys.path.insert(0, "scripts")
from scout_speculative_search_pilot import benchmark as search
from scout_heldout_stop_stress import benchmark as stopping
from scout_three_way_extra_work import benchmark as probe
s, h, p = search(), stopping(), probe()
assert len(s["rows"]) == 432 and s["strategies"]["failure_aware"]["exact_matches"] == 75
assert s["strategies"]["failure_aware"]["duplicate_evaluations"] == 0
assert len(h["rows"]) == 240
assert next(x for x in h["summary"] if x["regime"] == "late_breakthrough" and x["rule"] == "stop_on_plateau")["mean_net_vs_continue"] == -.096300
assert len(p["rows"]) == 240
assert next(x for x in p["summary"] if x["regime"] == "late_breakthrough" and x["action"] == "probe_then_decide")["mean_utility_delta_vs_continue"] == -.119110
print("PASS: three pinned synthetic benchmark summaries")
'
```

The `git hash-object` output must be, in path order:
```text
265d75d392b79e986c2afe957982f275ea833f91
c807e3b5d92efe7800d22d533b92c6608bb8a046
2753367dcedf3d3b17f3f9151a3c2e1d7766c3a9
```

The commands above are a proposed reviewer recipe, **not** a separately witnessed clean-clone execution. They import only standard-library Python modules, call deterministic `benchmark()` functions, avoid the scripts' file-writing `--out` modes, and neither contact a model nor access installed GhostMesh services. Git cloning requires network access and writes only to the reviewer's chosen checkout. Review the pinned source before executing it. Run from a disposable directory because the clone step creates a new folder.

## Qualification boundary

PASS: deterministic recomputation of the original fixture summaries and correspondence with retained public editorial values.

NOT TESTED: a separately implemented algorithm, archived raw result-file hashes, blind cohort review, real workload traces, confidence intervals over a representative population, causal isolation of failure memory, stronger-model escalation, operational cost estimates or production policy.

The source scripts explicitly mark model dispatch and production adoption unauthorized. Their generated trajectories and toy costs cannot establish real-world stopping reliability. A public reproducibility companion should preserve these limits and include separately reviewed executable source/fixtures before a new publication release.
