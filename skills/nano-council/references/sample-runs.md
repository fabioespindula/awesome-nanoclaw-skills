# Sample Runs

## Portuguese Trigger

User:

```text
/council Devo adaptar o LLM Council para NanoClaw agora ou primeiro criar um PRD?
```

Expected behavior:

- Run the full council.
- Answer in Portuguese.
- Treat this as a product/implementation planning question.
- End with a practical recommendation and first action.

## English Trigger

User:

```text
pressure-test this: we should replace our queue with direct synchronous calls.
```

Expected behavior:

- Run the full council.
- Answer in English.
- Surface reliability, coupling, and operational tradeoffs.
- Recommend a reversible test if the decision is not obvious.

## Non-Trigger

User:

```text
What file defines the queue worker?
```

Expected behavior:

- Do not run the council.
- Answer as a normal codebase question.

## Mixed Language

User:

```text
/council Quero decidir se fazemos launch agora ou wait for better onboarding.
```

Expected behavior:

- Portuguese output with technical English terms preserved where useful.

## This Reference

Previous user message:

```text
We should cut onboarding scope and launch tomorrow.
```

Current user message:

```text
pressure-test this
```

Expected behavior:

- Use the previous message as the council question.
- Do not ask what "this" means unless no previous target exists.
