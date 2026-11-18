# Changelog

## 1.3.0 - 2026-11-17

### Changed

- Built on 1.2.3. Skills still omit `allowed-tools`, and exports stay in `.diffbot/tmp/` in the working directory.
- Install lines require `diffbot>=3.4.0rc0,<4`. 3.1.x and 3.2.x are not new enough.
- The DQL skill states `POST https://kg.diffbot.com/kg/v3/dql` with a JSON body. The token stays the `token` query parameter. GET is the low-level escape hatch. Agents keep using `~/.diffbot/venv/bin/db`.
- Plugin manifests are 1.3.0. Tag this release `v1.3.0`.

There is no npm or PyPI package. The tag-triggered workflow creates the GitHub Release only. Marketplace SHA bumps (xAI and others) stay a separate step.
