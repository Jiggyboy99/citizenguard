# CitizenGuard

**AI-verified citizen environmental reports, hardened against prompt injection.**

![License](https://img.shields.io/badge/license-MIT-356859)
![Python](https://img.shields.io/badge/python-3.9%2B-33291E)
![UI](https://img.shields.io/badge/UI-Gradio-B85C36)
![Status](https://img.shields.io/badge/version-1.0-C99A3C)
![Demo](https://img.shields.io/badge/demo-live-356859)

> **Live demo:** https://huggingface.co/spaces/Pluvino/citizenguard
> **Source:** https://github.com/Jiggyboy99/citizenguard

CitizenGuard lets ordinary people report a local environmental problem — *"the air
near the factory smells bad today"* — and checks whether that report is actually
supported by **real public sensor data** before anyone acts on it. Every answer is
either backed by a specific real reading or honestly marked *unclear*. And because
the report box accepts untrusted text from the public, a **Guardian** security
layer defends the system against people trying to manipulate it.

This is an **AI-security project first** and an environmental project second: it
verifies untrusted public input and is built to survive attacks on that input.

## Screenshots

| A verified report, with its cited reading | An attack, blocked by the Guardian |
|---|---|
| ![Verdict](assets/screenshot-verdict.png) | ![Blocked](assets/screenshot-blocked.png) |

---

## Why it matters

Citizen environmental reporting has a trust problem. A single alarming message
can spread before anyone checks it, and a system that simply trusts user input is
both unreliable and trivially manipulated. CitizenGuard shows a pattern for
fixing that: **verify claims against ground truth, force every verdict to cite its
evidence, and treat all user input as hostile until screened.** The same pattern
applies far beyond air quality — to any system that turns public reports into
decisions.

It also runs entirely on free, lightweight infrastructure, which means communities
that can't afford enterprise monitoring contracts can still run something like it.
More on that in [docs/small-models-in-local-environments.md](docs/small-models-in-local-environments.md).

---

## What it does

- **Verifies** a citizen air-quality report against live readings from nearby
  government/reference sensors (OpenAQ).
- **Returns a verdict** — `verified` / `unverified` / `unclear` — with a one-line
  reason and a **citation to the exact reading** it relied on.
- **Refuses to guess.** If no real reading supports a verdict, it returns
  `unclear`. This is the anti-hallucination rule.
- **Defends itself.** The Guardian screens every report for prompt-injection
  attempts *before* the model sees it, and validates every verdict *after*.
- **Shows its work.** A live chart plots PM2.5 across nearby stations against the
  WHO guideline, so the verdict sits in visible context.

---

## Architecture

![System architecture](assets/architecture.svg)

Untrusted input enters through the web console, passes the Guardian's input
screening, is verified by an LLM against real readings retrieved from OpenAQ
(retrieval-augmented generation), is re-checked by the Guardian's output
validation, and only then becomes a verdict. Full detail in
[ARCHITECTURE.md](ARCHITECTURE.md).

### How a single request flows

![Request lifecycle](assets/dataflow.svg)

There are two points where a request can be stopped: a malicious report is
**blocked** before any model call, and an unprovable verdict is **downgraded to
unclear** before it reaches the user.

---

## The Guardian (security layer)

![Guardian defense in depth](assets/guardian-layers.svg)

No single layer is trusted. An attack has to pass all of them, and the model sits
protected in the middle.

The Guardian was red-teamed against its own attack suite. The first version
(keyword patterns only) caught 62% of malicious cases; adding input normalization
(de-leetspeak, un-spacing, base64 decoding) raised that to **85%**, with no new
false positives on legitimate reports.

| Version | Input defense | Detection |
|--------|----------------|-----------|
| v1 | keyword patterns only | 62% |
| v2 | + input normalization | **85%** |

The remaining gaps are documented honestly rather than hidden: semantic
paraphrase needs an LLM intent classifier (planned), and indirect data injection
is handled downstream by the output provenance check. Full assessment:
[security/security-report.md](security/security-report.md) ·
threat mapping: [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

Run the red-team suite yourself (no API key needed):

```bash
python security/redteam.py
```

---

## Quickstart

```bash
# 1. clone and enter
git clone https://github.com/Jiggyboy99/citizenguard.git
cd citizenguard

# 2. create + activate a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# 3. install
pip install -r requirements.txt

# 4. add your free API keys
cp .env.example .env        # then paste your keys into .env

# 5. run
python app.py               # open the local URL it prints
```

Free API keys: **OpenAQ** → https://explore.openaq.org · **Groq** → https://console.groq.com

Detailed, beginner-friendly setup with troubleshooting: [SETUP.md](SETUP.md).

---

## Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| Verification model | LLM via Groq (free tier) | fast, free, swappable |
| Ground-truth data | OpenAQ v3 API | real government/reference sensors |
| Retrieval | direct sensor query (RAG) | grounds every verdict in real data |
| Security | custom Guardian module | input screening + output validation |
| UI | Gradio | one-file app, deploys to Spaces |
| Charts | Plotly | interactive PM2.5 visualization |
| Hosting | Hugging Face Spaces (free) | public link, secrets management |

Everything runs on free tiers by design.

---

## Project structure

```
citizenguard/
├── app.py                 # web console (Gradio UI)
├── verify.py              # core engine: OpenAQ fetch + LLM verification
├── guardian.py            # security layer: input screening + output validation
├── prompts/
│   └── verify_v1.txt      # versioned verification prompt
├── security/
│   ├── redteam.py         # red-team suite (attacks the Guardian)
│   └── security-report.md # generated security assessment
├── docs/
│   ├── THREAT_MODEL.md    # OWASP LLM Top 10 + MITRE ATLAS mapping
│   └── small-models-in-local-environments.md
├── assets/                # diagrams + screenshots
├── ARCHITECTURE.md        # design deep-dive
├── SETUP.md               # step-by-step setup guide
└── requirements.txt
```

---

## Roadmap

This is **V1** — a deliberately tight, working slice. Planned next:

- **LLM-based injection classifier** — close the semantic-paraphrase gap (Layer 3).
- **Recency filtering** — drop stale sensor readings before verifying.
- **Multi-agent "consensus"** — several prompt variants vote on a verdict.
- **More data sources** — regulations and satellite summaries via document RAG.
- **Expanded red-team corpus** — broaden beyond the current demonstration set.

---

## A note on scope

CitizenGuard is a demonstration of a pattern, not a production safety system. The
red-team suite is a demonstration harness, not an exhaustive audit. The honest
framing is the point: it shows how to verify untrusted input, ground answers in
real data, and defend an LLM application — and where the current limits are.

## License

MIT — see [LICENSE](LICENSE).
