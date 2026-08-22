# Architecture Findings

This is the persistent findings ledger for `architecture-v2.md`. Keep it
updated whenever implementation or verification opens, changes, resolves, or
defers a finding. `PLAN.md` is the corresponding implementation plan.

By user decision, `0.1.0` will release the tested current scope after Step 6;
the remaining architecture-v2 findings target the `0.2.0` line.

Status values are `open` and `resolved`. Related original findings are grouped
under their existing IDs so earlier references remain traceable.

| Original IDs | Status | Planned step | Consolidated finding |
|---:|---|---|---|
| 1, 2, 5 | open | 7 | Config flow does not normalize/validate the host, contact the camera before entry creation, or map failures to the required safe errors. |
| 3, 4 | open | 7 | Camera ID is not the config-entry unique ID and duplicate physical cameras are not prevented. |
| 6, 7, 10 | open | 7 | Setup does not enforce identity, trigger proper reauthentication, or implement single-reload update behavior. |
| 8 | open | 7 | Password reauthentication for the same physical camera is missing. |
| 9 | open | 7 | Host reconfiguration for the same physical camera is missing. |
| 11 | open | 7 | Error, reauthentication, reconfiguration, success, duplicate, and wrong-device translations must accompany the lifecycle implementation. |
| 12, 17 | open | 6 | No reproducible real Home Assistant test environment exists; current checks use hand-written module stubs. |
| 13, 16 | open | 6, 8 | API coverage lacks a real Digest exchange and complete real-aiohttp edge cases. |
| 14, 15 | open | 7, 8 | Config-flow, device-registry, camera, reload, and unload behavior lack complete real Home Assistant coverage. |
| 18 | open | 6 | CI has no lint/static gate. |
| 19 | resolved | 6a | Deleted duplicate `ci.yml`; retained per-check reporting in `test.yml`. |
| 21, 22 | open | 8 | The false placeholder statement is corrected; README still omits most architecture section 22 requirements. |
| 23 | resolved | 6a | Deleted stale alpha.5-specific `Release.md`; GitHub and `PLAN.md` own release state. |
| 25 | open | 7a, 9 | No persisted HACS/physical-camera verification report exists for a final or architecture-complete release. |
| 26 | open | 6a | Release `374950984` and local/remote `v0.1.0-alpha.3` tags still exist at mislabeled commit `fffcd04`; authenticated cleanup and immediate user approval are required. |
| 27 | resolved | 6a | Deleted unrelated `.vscode/settings.json` command auto-approval settings. |
| 28 | open | 8 | Brand assets are absent and HACS validation suppresses the `brands` check. |
| 29 | open | 6 | GitHub Actions use mutable references; pin full commit SHAs and use Dependabot for `github-actions` updates. |

Removed by the accepted Ponytail review:

- Original finding 20: pull-request triggers are YAGNI until the repository
  actually uses a pull-request workflow.
- Original finding 24: never moving an existing release tag is a release
  invariant recorded in `PLAN.md`, not an implementation finding.

## Current acceptance summary

Implemented in code:

- Host/password-only stored data model.
- Narrow verified HTTP paths and Digest middleware.
- Camera identity and optional firmware extraction.
- One device and one camera entity.
- JPEG snapshot and verified ASF/H.264 stream source.
- Raw CGI bodies are not persisted.

Validated on current `main`:

- Local stub-based runnable checks.
- CI and Test workflows.
- HACS validation.
- Hassfest validation.

Missing or not yet proven:

- Validated UI setup and config-entry identity.
- Duplicate prevention.
- Reauthentication and reconfiguration.
- Real Home Assistant/aiohttp automated coverage.
- Complete documentation, branding, and lint/static validation.
- Reproducibly pinned GitHub Actions with automated update proposals.
- HACS installation and physical-camera acceptance report for an
  architecture-complete release.
