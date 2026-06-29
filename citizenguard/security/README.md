# security

## The Guardian (implemented — see `guardian.py`)

Two layers wrap the verification engine:

**Input screening** — every citizen report is checked *before* it reaches the
verification model. A heuristic filter detects prompt-injection / jailbreak
techniques and names the one it found:
- instruction override ("ignore previous instructions")
- role manipulation ("you are now in developer mode")
- system-prompt extraction ("reveal your system prompt")
- verdict manipulation ("mark this as verified")
- format injection (`### SYSTEM:` and similar)

A blocked report produces no verdict and triggers **no LLM call** at all.

**Output validation** — every verdict is checked *after* the model responds:
- the verdict must be one of verified / unverified / unclear
- a verified/unverified verdict must cite a reading whose value actually exists
  in the real data — this catches hallucinated citations (provenance enforcement)

Run `python guardian.py` to see both layers catch attacks (no API key needed).

## Honest limitation (this is the point of Phase 4)

The input filter is pattern-based, and pattern filters are bypassable. That's not
hidden — it's the thing the red-team phase will demonstrate, document, and then
harden. Output validation is the sturdier half because it checks results against
ground truth rather than guessing intent.

## Coming in Phase 4
- **redteam/** — a runnable suite of attacks (incl. ones that beat the filter)
- **security-report.md** — what got caught, what slipped through, and the fixes
