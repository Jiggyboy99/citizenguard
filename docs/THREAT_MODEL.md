# Threat Model

A short, honest threat model for CitizenGuard, mapped to the frameworks working
AI-security engineers use: the **OWASP Top 10 for LLM Applications (2025)** and
**MITRE ATLAS**.

## What we are protecting

- **The integrity of verdicts.** A verdict must reflect real data, not attacker
  influence.
- **The verification model.** It must not be hijacked into ignoring its
  instructions.
- **System instructions.** The prompt should not be extractable.

## Trust boundaries

The single most important boundary is the **citizen report field**. It is
free-text from the public and is treated as fully untrusted. Everything an
attacker controls enters here. The OpenAQ data and the prompt template are
trusted; the model output is *semi-trusted* and re-validated before use.

## Adversaries

- A user trying to force a desired verdict ("mark this verified").
- A user trying to extract the system prompt.
- A user injecting fake data to mislead the verifier.
- A user trying to make the model misbehave for amusement (jailbreak).

## OWASP LLM Top 10 mapping

| Code | Risk | How CitizenGuard addresses it |
|------|------|-------------------------------|
| LLM01 | Prompt Injection | Input guard: normalization + pattern detection; prompt instructs the model to treat the report as data, not commands |
| LLM02 | Sensitive Information Disclosure | No personal data stored; reports are not persisted |
| LLM05 | Improper Output Handling | Output guard: strict verdict schema before display |
| LLM07 | System Prompt Leakage | Extraction patterns in the input guard; the prompt holds no secrets of value |
| LLM09 | Misinformation | Forced citations + output provenance check; unprovable claims become `unclear` |

## MITRE ATLAS techniques considered

- **LLM Prompt Injection** — primary attack surface; mitigated at input and
  reinforced by output validation.
- **LLM Jailbreak** — role-manipulation and "developer mode" patterns are
  detected.
- **Erode ML Model Integrity / data manipulation** — indirect data injection is
  caught by the output provenance check rather than the input filter.

## Residual risks (accepted, documented)

- **Semantic paraphrase** of an injection with no keywords can pass the input
  guard. Mitigation planned: an LLM-based intent classifier (Guardian Layer 3).
- **Heuristic bypasses** generally — pattern filters are inherently incomplete;
  defense in depth and output validation are the compensating controls.
- **Stale data** can ground a verdict in an old reading until recency filtering
  lands.

## Why document residual risk

A threat model that claims zero residual risk is not credible. Naming what still
gets through — and why each remaining gap is acceptable or has a planned fix — is
what distinguishes an assessment from a marketing page.
