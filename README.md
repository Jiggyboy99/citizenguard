# CitizenGuard

**AI-verified citizen environmental reports, hardened against prompt injection.**

Ordinary people report a local environmental problem (e.g. "the air near the
factory smells bad today"). Instead of trusting the report blindly, CitizenGuard
checks it against **real public sensor data** and returns a verdict —
*verified / unverified / unclear* — with a citation to the exact reading it used.
A **Guardian** security layer defends the system against people trying to trick
it through the report field.

This is an AI-security project first and an environmental project second: it
verifies untrusted public input and is built to survive attacks on that input.

---

## Status

| Phase | What | State |
|---|---|---|
| 1 | Repo + plumbing | done |
| 2 | Core pipeline: report -> verify against OpenAQ -> verdict + citation | **in progress** |
| 3 | Guardian: input + output guarding | planned |
| 4 | Red-team suite + security report | planned |
| 5 | Deploy + threat model | planned |

## How it works (v1)

```
citizen report ─┐
                ├─> verify.py ─> LLM verdict {verified|unverified|unclear} + citation
OpenAQ v3 data ─┘
```

- **Data:** OpenAQ v3 air-quality API (real government/reference sensors).
- **Model:** any free-tier LLM (default: Groq).
- **Provenance rule:** every verdict must cite a specific real reading, or it
  returns `unclear`. This is the anti-hallucination mechanism.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env      # paste your OpenAQ + Groq keys
python verify.py
```

Get free keys: OpenAQ → https://explore.openaq.org · Groq → https://console.groq.com

## Repo layout

```
verify.py        core engine (fetch + verify)
prompts/         versioned prompt templates
app/             Gradio UI (Phase 2)
docs/            threat model + architecture
security/        red-team suite + security report (Phase 4)
notebooks/       experiments
```

## Roadmap

- Multi-agent "Green Consensus": several prompt variants vote on a verdict.
- More data sources beyond air quality (regulations via RAG, satellite summaries).
- Low-cost compliance reporting for small/medium businesses.

## Threat model

Mapped to the OWASP LLM Top 10 (esp. LLM01 Prompt Injection, LLM09
Misinformation) and MITRE ATLAS. See `docs/threat-model.md` (coming in Phase 5).
