/*
  Community-marketplace submission — paste-ready content for the in-app form.
  This is the ACTIVE submission path. The official marketplace
  (claude-plugins-official) has no application process; see README.md.
*/

# Community submission — `claude-community`

The real public queue. Submit via the in-app form; the plugin is reviewed,
safety-screened, and SHA-pinned into
[`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community).

## Where to submit

| Form | Use when | URL |
| --- | --- | --- |
| **Console** | Individual author, no Team/Enterprise org | https://platform.claude.com/plugins/submit |
| **claude.ai** | You have a Team/Enterprise org + directory management access (Owners do by default) | https://claude.ai/admin-settings/directory/submissions/plugins/new |

Diffbot has no Team/Enterprise org wired up for this, so use the **Console** form
unless that changes.

## Before you submit

Run the same check the review pipeline runs:

```bash
claude plugin validate .
```

Expected: passes with one benign warning (root `CLAUDE.md` is maintainer docs,
intentionally not shipped as plugin context). See `validation-proof.md`.

## Form fields (paste-ready)

**Plugin name**

```
diffbot
```

**Repository / source**

```
https://github.com/diffbot/diffbot-skills.git
```

Pinned release `v1.0.0` @ `44a20a931193596243d786ffb02959c8d75a5e8f`. After
approval, CI bumps the SHA pin automatically as you push new commits.

**Plugin description**

```
Structured web knowledge for developers via Diffbot. The agent authors DQL queries against a web-scale knowledge graph of organizations, people, and articles — exploring the ontology, probing selectivity, and exporting typed JSON or CSV — plus skills to extract page content, resolve named entities, and crawl sites.
```

**Example use cases**

```
Example 1: "Find all venture-backed AI companies founded after 2020 in the Bay Area with more than 50 employees, and export their funding totals to CSV." /diffbot-dql explores the organization ontology, probes the query for selectivity, runs it against the web-scale Knowledge Graph, and exports typed rows. Structured querying, not a web search.

Example 2: "Pull the clean article text, author, and publish date from these 40 news URLs." /diffbot-extract returns structured page content (markdown or full JSON) for each URL, while /diffbot-entities resolves the people and organizations mentioned to Knowledge Graph records with confidence and salience scores.

Example 3: "Crawl this competitor's documentation site and give me the latest pricing and product pages." /diffbot-crawl runs and manages the crawler job over the site for structured content, and /diffbot-web-search backfills ranked live results — dates, snippets, and URLs — for anything not yet in the graph.
```

> Example 1 leads on DQL / Knowledge Graph querying — the capability that
> distinguishes Diffbot from generic scrape/search plugins. Keep it first.

## After approval

- The public catalog syncs nightly from the review pipeline, so expect a delay
  between approval and the plugin appearing in `marketplace.json`.
- Check installability by searching for `diffbot` in the
  [community catalog](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json).
- Once live, users install with:

  ```
  /plugin marketplace add anthropics/claude-plugins-community
  /plugin install diffbot@claude-community
  ```

- Update the project README install line to drop the "once listed" caveat.
