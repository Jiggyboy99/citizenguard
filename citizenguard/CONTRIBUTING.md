# Contributing

CitizenGuard is an open demonstration project and contributions are welcome.

## Ways to help
- **Extend the red-team corpus** in `security/redteam.py` with new attack
  techniques (especially ones that beat the current Guardian — those are the
  most valuable).
- **Build Guardian Layer 3**, the LLM-based intent classifier, to close the
  semantic-paraphrase gap.
- **Add recency filtering** to drop stale sensor readings before verification.
- **Improve data coverage** with additional open environmental sources.

## Ground rules
- Keep the **citation rule** intact: no verdict without a real, cited reading.
- Treat the report field as **untrusted** in any new code path.
- If you add a defense, add a red-team case that tests it.
- Never commit secrets. Keys belong in `.env` (local) or host secrets (deployed).

## Workflow
1. Fork and branch.
2. Make your change; run `python security/redteam.py` and `python guardian.py`.
3. Open a pull request describing what you changed and why.
