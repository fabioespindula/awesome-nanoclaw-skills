# Category Taxonomy

Assign one or more tags. Use `general` when no specific category applies. Do not force personalization.

## Project-Specific Tags

Before using the default tags below, check whether the current conversation, `AGENTS.md`, `CLAUDE.md`, or another available project instruction defines local categories, business units, companies, or project tags.

If local tags are clearly defined, use them. Do not invent private company tags in the public skill.

Examples:

- If local context defines `acme-growth`, use it for links directly relevant to Acme's growth work.
- If local context defines `portfolio-company-a`, use it for links directly relevant to that portfolio company.
- If no local tags exist, use only the default tags below.

## `business`

Use when content relates to:

- company operations, strategy, hiring, pricing, sales, partnerships
- industry news that affects an operating business
- customer acquisition or retention beyond pure marketing tactics
- business-unit decisions or executive priorities

## `investing`

Use when content relates to:

- venture capital, private investments, public markets, M&A, fundraising
- company analysis, investment theses, market maps
- portfolio strategy or operating insights relevant across multiple companies

Do not use for generic startup news unless it informs an investment, market, or portfolio operating decision.

## `ai-tools`

Use when content relates to:

- AI agents, LLMs, model releases, evals, benchmarks
- coding assistants, agent workflows, prompt engineering, RAG, MCP, tool use
- automation platforms and developer tools using AI

Do not use when AI is only a buzzword and not central to the content.

Examples:

- Claude Code adds Skills -> `ai-tools` `personal-dev`
- Gstack open-sources agent workflow skills -> `ai-tools` `product` `personal-dev`
- New browser automation protocol for agents -> `ai-tools` `product`

## `marketing`

Use when content relates to:

- SEO, paid media, attribution, analytics, landing pages, conversion
- content marketing, lifecycle marketing, social, brand, growth
- lead quality, CAC, LTV, funnel optimization

Examples:

- Google update affects programmatic landing pages -> `marketing`
- Meta improves lead form quality controls -> `marketing`

## `product`

Use when content relates to:

- product strategy, UX, onboarding, activation, retention
- feature design, user research, roadmap tradeoffs
- pricing/packaging when discussed as product behavior, not only finance

## `personal-dev`

Use when content relates to:

- open source projects, side projects, learning, personal tooling
- developer productivity, skill-building, personal workflows
- creator/operator habits that apply to the user's own craft

## `general`

Use when the content is interesting but has no direct known business, project, investment, marketing, product, AI tooling, or personal-development connection.

## Relevance Calibration

- `3`: A known project or business should plausibly change a task, decision, audit, roadmap item, or experiment.
- `2`: Useful strategic signal, but action is not urgent or direct.
- `1`: Background context.
- `0`: No direct connection to known priorities.

Only recommend `Save as to-do` for relevance `3`.
