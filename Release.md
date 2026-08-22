# Release `0.1.0-alpha.3`

## Status and prerequisites

- Step 2 is implemented locally but is not committed, released, or user-verified.
- Step 1 has no GitHub release or live HACS verification; it remains started.
- The manifest version is `0.1.0-alpha.3`; use tag and release `v0.1.0-alpha.3` and mark it as a prerelease.
- Home Assistant 2026.8+ and HACS must already be installed. Make a Home Assistant backup first.

## Review, commit, and push

Run manually from the repository root:

```bash
git status --short
git diff --check
git diff
sed -n '1,220p' Release.md
python3 tests/test_scaffold.py
python3 -m py_compile custom_components/reer_babycam/*.py tests/test_scaffold.py
python3 -m json.tool custom_components/reer_babycam/manifest.json >/dev/null
python3 -m json.tool custom_components/reer_babycam/strings.json >/dev/null
python3 -m json.tool custom_components/reer_babycam/translations/en.json >/dev/null
git add custom_components/reer_babycam/config_flow.py \
  custom_components/reer_babycam/manifest.json \
  custom_components/reer_babycam/strings.json \
  custom_components/reer_babycam/translations/en.json \
  tests/test_scaffold.py Release.md
git diff --cached --check
git diff --cached --stat
git commit -m "feat: add simple camera configuration"
git push upstream main
```

## Create the GitHub prerelease

1. Open the repository's **Releases** page and select **Draft a new release**.
2. Create tag `v0.1.0-alpha.3` from `main` and use the same value as the title.
3. Paste these release notes:

   ```text
   Step 2: simple configuration lifecycle

   - Collects and stores host and password through Home Assistant's UI.
   - Masks the password field.
   - Keeps one placeholder device and one empty camera.
   - Makes no network call and does not validate the camera or credentials.

   Snapshots, streaming, device identity, reauthentication, and reconfiguration are not included.
   Existing alpha entries must be removed and added again to store host/password.
   ```

4. Select **Set as a pre-release**, then publish.

## Install or update with HACS

1. In HACS, open the top-right menu → **Custom repositories**.
2. If absent, add `https://github.com/phoebos02/ha-reercam` as **Integration**.
3. Open **reer IP BabyCam** and choose **Download**, or **Redownload** when already installed.
4. Under **Need a different version?**, select `v0.1.0-alpha.3`. If testing before the tag appears, select `main` if offered; otherwise choose **Update information** and retry.
5. Restart Home Assistant.

## Configure and verify

Existing alpha entries have no migration. Remove the old **reer IP BabyCam** entry under **Settings → Devices & services**, then add it again.

1. Select **Add integration** → **reer IP BabyCam**.
2. Confirm the form contains exactly **Host** and **Password**, both required, and the password is masked.
3. Enter arbitrary values. Setup must succeed without reaching or validating a camera.
4. Confirm exactly one placeholder device and one empty camera entity exist.
5. Confirm no snapshot or stream is available; this is expected.
6. Reload the entry, then restart Home Assistant; confirm everything returns without re-entering the values.
7. Search Home Assistant logs for the submitted password; it must not appear.
8. Delete the entry and confirm its entity/device unload cleanly.

Report the result:

```text
RESULT: PASS | FAIL
HOME ASSISTANT: <version>
INSTALLED FROM: v0.1.0-alpha.3 | main
FAILED CHECK: <number or none>
DETAILS/LOGS: <redact passwords>
```

## Roll back

In HACS, choose **Redownload** and select the previous published version, then restart Home Assistant. If no previous release is available, restore the pre-update Home Assistant backup. Re-add any removed integration entry as needed.

Sources: [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository), [HACS custom repositories](https://hacs.xyz/docs/faq/custom_repositories/), [HACS repository dashboard](https://hacs.xyz/docs/use/repositories/dashboard/).
