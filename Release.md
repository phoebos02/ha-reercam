# Release `0.1.0-alpha.5`

## Status

This guide prepares the intended `0.1.0-alpha.5` alpha prerelease for Home Assistant 2026.8+ and the reer IP BabyCam 80300, verified with camera firmware `42.7.3.4.70`. The intended Git tag, release title, and HACS version are `v0.1.0-alpha.5`.

> [!WARNING]
> **Known tag mismatch:** `v0.1.0-alpha.3` points to code whose manifest says `0.1.0-alpha.5`. Do not install that tag or use it for rollback. No correct alpha.3 snapshot has been established, so do not recreate it.

## Pre-release review

Run these commands manually from the repository root. They are the release gate; their presence here does not mean they have been run for the release.

```bash
git status --short
git rev-parse HEAD
git rev-parse main
git rev-parse upstream/main
git ls-remote --heads upstream main
git tag --list 'v0.1.0-alpha.*' --format='%(refname:short) %(objectname)'
git ls-remote --tags upstream 'v0.1.0-alpha.*'
git show v0.1.0-alpha.3:custom_components/reer_babycam/manifest.json
git diff --stat
git diff
python3 tests/test_api.py
python3 tests/test_scaffold.py
python3 -m py_compile custom_components/reer_babycam/__init__.py custom_components/reer_babycam/api.py custom_components/reer_babycam/camera.py custom_components/reer_babycam/config_flow.py tests/test_api.py tests/test_scaffold.py
python3 -m json.tool custom_components/reer_babycam/manifest.json >/dev/null
python3 -m json.tool custom_components/reer_babycam/strings.json >/dev/null
python3 -m json.tool custom_components/reer_babycam/translations/en.json >/dev/null
python3 -c 'import json; assert json.load(open("custom_components/reer_babycam/manifest.json"))["version"] == "0.1.0-alpha.5"'
git diff --check
```

Confirm that the manifest says `0.1.0-alpha.5`. The alpha.3 tag inspection must show the mismatch described above. `upstream/main` is only the local remote-tracking reference; compare it with the read-only `git ls-remote` result.

If the worktree is clean and the intended release content is already committed on the pushed `main` commit, skip commit and push. If this guide correction or other intended files remain, inspect every path before `git add -A`, then commit and normally push. Never force-push.

```bash
git status --short
git diff
git add -A
git diff --cached --stat
git diff --cached
git diff --cached --check
git commit -m "docs: correct alpha release guide"
git push upstream main
```

### Optional manual cleanup of the mislabeled alpha.3

Deleting a published GitHub Release or tag rewrites public release metadata. This is optional and must be an explicit user decision; none of these cleanup actions are part of the release checks.

1. On GitHub, open **Releases** and check whether a `v0.1.0-alpha.3` Release object exists.
2. If you explicitly choose cleanup, open that Release, select **Delete**, and confirm deletion. Do not create a replacement alpha.3 Release.
3. Only if you also explicitly choose to delete the mislabeled tag, run:

   ```bash
   git push --delete upstream v0.1.0-alpha.3
   git tag -d v0.1.0-alpha.3
   ```

These commands are destructive instructions for manual use only. Do not run them merely to create alpha.5.

## GitHub prerelease

First confirm that `main` is clean and pushed and that alpha.5 does not already exist:

```bash
git status --short
git rev-parse HEAD
git rev-parse upstream/main
git ls-remote --heads upstream main
git tag --list v0.1.0-alpha.5
git ls-remote --tags upstream refs/tags/v0.1.0-alpha.5
```

The two alpha.5 tag commands must return no tag. Then follow the [GitHub release instructions](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository):

1. Open **Releases** and select **Draft a new release**.
2. Create tag `v0.1.0-alpha.5` from the pushed `main` commit.
3. Use title `v0.1.0-alpha.5`.
4. Paste these release notes:

   ```text
   reer IP BabyCam 0.1.0-alpha.5

   - HACS installation and README guidance
   - Home Assistant UI configuration for host and password
   - Local HTTP Digest client for the verified camera endpoints
   - Camera identity and optional firmware metadata
   - Native JPEG snapshots
   - Native live stream source using the verified ASF/H.264 stream

   Deferred: configuration-time validation, duplicate prevention,
   reauthentication, and host reconfiguration.

   Requires Home Assistant 2026.8+. This is an alpha prerelease.
   Existing older-alpha config entries must be removed and added again.
   ```

5. Select **Set as a pre-release** and publish.

Do not continue until GitHub shows the new `v0.1.0-alpha.5` release; this guide does not establish that it exists remotely.

## Install or update with HACS

Create and download a Home Assistant [backup](https://www.home-assistant.io/common-tasks/general/#backups) first.

Use the [one-click HACS repository button](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoebos02&repository=ha-reercam&category=integration), or add the repository manually:

1. In HACS, open the three-dot menu → **Custom repositories**.
2. Enter `https://github.com/phoebos02/ha-reercam`, choose **Integration**, then **Add**.
3. Open **reer IP BabyCam** and select **Download**, or **Redownload** if already installed.
4. Under **Need a different version?**, select `v0.1.0-alpha.5` after it is published.
5. Restart Home Assistant.

See the official [custom repository](https://hacs.xyz/docs/faq/custom_repositories/), [repository dashboard](https://hacs.xyz/docs/use/repositories/dashboard/), and [update](https://hacs.xyz/docs/use/update/) instructions if the expected version is not shown.

## Configure Home Assistant

There is no migration for older alpha config entries. Remove the existing **reer IP BabyCam** entry and add it again:

1. Go to **Settings → Devices & services** and remove the old integration entry.
2. Select **Add integration → reer IP BabyCam**.
3. Enter the camera's bare IP address or hostname, without `http://`, and its password.
4. Submit the form.

The form stores the values without contacting the camera. Entry setup then contacts the camera and must succeed before the device and entity appear.

## Manual verification

With Home Assistant and the physical camera on the same trusted local network, verify:

- [ ] HACS reports `0.1.0-alpha.5` after restart and Home Assistant reports no integration startup errors.
- [ ] Exactly one reer device and one camera entity exist.
- [ ] The device identifier matches the camera ID; manufacturer, model, serial, and firmware metadata are correct.
- [ ] Opening the camera returns a non-empty JPEG snapshot.
- [ ] Live view starts from the verified ASF/H.264 `stream=1` source.
- [ ] Reloading the entry and restarting Home Assistant restore the same device and entity.
- [ ] Deleting the entry unloads and removes its device/entity cleanly.
- [ ] Logs and displayed errors contain no password, credential-bearing URL, Digest authorization material, or raw CGI body.

Expected alpha limitations:

- The config form does not validate before creating the entry.
- A wrong password leaves setup failed; reauthentication is not implemented.
- An unreachable camera leaves setup waiting for Home Assistant's retry behavior.
- Duplicate prevention and host reconfiguration are not implemented.

Report the result without secrets:

```text
RESULT: PASS | FAIL
HOME ASSISTANT: <version>
INTEGRATION: 0.1.0-alpha.5
CAMERA FIRMWARE: <version>
HACS INSTALL/UPDATE: PASS | FAIL
SETUP: PASS | FAIL
SNAPSHOT: PASS | FAIL
STREAM: PASS | FAIL
RELOAD/RESTART: PASS | FAIL
UNLOAD/DELETE: PASS | FAIL
SANITIZED LOGS: <none or relevant lines; redact passwords and credential URLs>
```

## Roll back

Back up Home Assistant before rollback. Never select `v0.1.0-alpha.3`; it contains mislabeled alpha.5 code. Use HACS **Redownload** to select another previous version only if HACS actually lists one, then restart Home Assistant.

If no previous version is listed, remove the integration entry using Home Assistant's [standard removal steps](https://www.home-assistant.io/common-tasks/general/#removing-an-integration-instance), remove the HACS repository, and restore the backup or known-good manually saved integration files. Deleting the integration entry removes its device and entities; removing only the HACS repository does not remove its Home Assistant data.
