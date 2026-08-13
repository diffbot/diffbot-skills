# GitHub Copilot listing — `awesome-copilot`

Everything needed to submit `diffbot` to the `github/awesome-copilot` external
plugin marketplace.

## What to do

1. Open the **External Plugin** issue form at
   https://github.com/github/awesome-copilot — do **not** PR `plugins/external.json`
   directly.
2. Fill the form using the field values and description in
   **`copilot-intake-issue.md`**.
3. After filing, intake automation validates metadata, runs
   `skill-validator check --plugin`, and smoke-tests the Copilot install.
   - If it passes → maintainers add the `plugins/external.json` entry.
   - If it fails (`requires-submitter-fixes`) → fix the plugin and comment
     `/rerun-intake` on the issue.
4. Once approved, update the README Copilot install line to add
   `/plugin install diffbot@awesome-copilot`.

Pinned release: `v1.1.0` @ `466f802ebadd8126bb09dc9fe9e81b736a8814b6`.
