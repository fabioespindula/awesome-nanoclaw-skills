# Sample Runs

These examples are public, fictional, and safe for documentation or validation. They should feel realistic enough to inspire use, but must not include private user data.

## Launch Timing

Visible conversation context:

```text
We are preparing a marketplace for AI agents. A few beta users are asking for access this week. The onboarding still has rough edges, especially the first-run setup and trust explanation.
```

User:

```text
/rethink Devemos lancar agora?
```

Expected behavior:

- Identify the decision object as launch timing for the agent marketplace.
- Treat this as `clarify + pressure + decide`.
- Compare a controlled beta launch against waiting for better onboarding.
- Recommend a reversible launch to a small cohort when learning speed matters.
- Include rollback criteria, onboarding risk, trust risk, and a first next move.

## Product Versus Service

Visible conversation context:

```text
A large enterprise customer wants to pay for the product, but only if we add several custom workflows. The work could fund the team, but it may pull the roadmap toward consulting.
```

User:

```text
/rethink aceito esse cliente?
```

Expected behavior:

- Identify the decision object as accepting revenue with custom scope.
- Treat this as `pressure + simplify + decide`.
- Separate immediate cash from roadmap drift and support burden.
- Recommend accepting only if the work becomes reusable product capability or is contractually isolated as paid services.
- Include a clear "do not do yet" boundary around bespoke product commitments.

## Architecture Tradeoff

Visible conversation context:

```text
The skills package can auto-update managed skills by default. It also creates backups and validates source folders before replacement.
```

User:

```text
/rethink isso protege usuarios ou cria risco operacional?
```

Expected behavior:

- Identify the decision object as default-on auto-update behavior.
- Treat this as a technical trust and operations decision.
- Compare security fixes, user control, rollback, transparency, and failure blast radius.
- Recommend a default that preserves safety while making rollback and opt-out obvious.
- Include tests or validation as part of the next move.

## Broad Theme Boundary

User:

```text
think-big sobre o futuro dos marketplaces de agentes
```

Expected behavior:

- Do not treat this as a concrete `rethink` decision.
- Route conceptually to `think-big` or answer with a future-exploration frame.
- Do not force a recommendation before the user gives a concrete commitment.

## Help Mode

User:

```text
/rethink help
```

Expected behavior:

- Explain what Rethink does.
- Show when to use it and when not to use it.
- Include command forms and curated examples.
- Include contextual examples only when the visible conversation gives a concrete decision.
