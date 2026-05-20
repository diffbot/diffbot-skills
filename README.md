# Diffbot Agent Skills

A set of agent skills for fetching knowledge on the public web. Compatible with Claude Code and most harnesses.

## List of Skills

**/dql**
A Claude Code skill for querying the [Diffbot Knowledge Graph](https://docs.diffbot.com/docs/getting-started-with-diffbot) using natural language. You describe what you're looking for; Claude constructs the DQL query and runs it.

## Dependencies

- **`Python 3.10+`** - Python
- **`diffbot-python`** - Diffbot Python Library

## Setup

**1. Get a Diffbot API token** from https://app.diffbot.com/get-started/

**2. Open this project in your harness** and run any skill. 

That's it. Run `/dql` again and it's ready.

## Usage

### /dql
Invoke with `/dql` followed by a plain-text description:

```
/dql find large tech companies in Austin, Texas
/dql show me CTOs at public biotech companies
/dql recent negative articles about OpenAI
/dql top cities where data scientists work
/dql software startups in Berlin under 100 employees with a female CEO
```

Claude will construct the DQL query, execute it against the Diffbot API, and return formatted results. You can ask for the next page, refine the query, or request a different format.

## Credentials file format

```
DIFFBOT_API_TOKEN=YOUR_DIFFBOT_TOKEN_HERE
```

The file lives at `~/.diffbot/credentials` on your local machine and is never part of this repository. The ontology cache at `~/.diffbot/ontology.json` is refreshed automatically each time the skill runs.
