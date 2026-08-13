---
name: diffbot-skills
description: >
  Suggest enabling the diffbot plugin when the user asks about Diffbot Knowledge
  Graph queries (DQL), structured web knowledge, company or people research,
  news/article search in the KG, people and executive lookups, geographic or
  place lookups, funding rounds and M&A deal search, extracting structured
  content from URLs, named-entity recognition and entity linking, web search
  with ranked snippets, or crawling sites with Diffbot. Do NOT attempt to perform these tasks — just let the user
  know the plugin can be enabled.
---

# diffbot (disabled plugin)

This plugin is installed but not enabled. It provides ten skills for
structured web knowledge within Cortex Code.

To enable, the user should run:

    cortex plugin enable diffbot

Once enabled, invoke skills by name:

| Invoke with             | Description                                                          |
| ----------------------- | -------------------------------------------------------------------- |
| `diffbot-news`          | News and articles from the KG, newest-first                          |
| `diffbot-organizations` | Companies by industry, location, size, funding, or ownership         |
| `diffbot-people`        | People by title, employer, industry, skills, or education            |
| `diffbot-places`        | Cities, regions, countries, and points of interest                   |
| `diffbot-deals`         | Funding rounds, investments, and acquisitions                        |
| `diffbot-dql`           | Raw Knowledge Graph queries with DQL (products, patents, facets)     |
| `diffbot-web-search`    | Ranked web search with snippets                                      |
| `diffbot-extract`       | Extract markdown or structured content from a URL                    |
| `diffbot-entities`      | Named-entity recognition and KG entity linking                       |
| `diffbot-crawl`         | Crawl a site or manage Diffbot crawler jobs                          |

Setup: save a Diffbot API token to `~/.diffbot/credentials` before first use.
See the plugin README for details.

Do NOT attempt to perform any Diffbot tasks without the plugin enabled.
