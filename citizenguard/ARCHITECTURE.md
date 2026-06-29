# Architecture

This document explains how CitizenGuard is built and, more importantly, *why*
each decision was made. The guiding principle throughout: **treat all user input
as hostile, and never let the system assert something it cannot prove.**

## Overview

CitizenGuard is a pipeline with two security gates around an AI verification core.

![System architecture](assets/architecture.svg)

A citizen report enters the web console. Before the model ever sees it, the
**Guardian's input screening** inspects it for manipulation. If it passes, the
**verification engine** retrieves real sensor readings near the chosen location
and asks an LLM to judge the report against that data. The LLM's answer then
passes the **Guardian's output validation** before it is shown. Only a verdict
that is well-formed *and* backed by a real reading reaches the user.

## Components

### 1. Web console (`app.py`)
A Gradio interface: a location selector, a report box, a verify button, and a
results panel showing the verdict, the cited reading, a live PM2.5 chart, and the
Guardian's status. It is intentionally a single file so it deploys to Hugging
Face Spaces unchanged. The CSS/theme handling auto-adapts to Gradio 5 or 6 so the
same file runs locally and in the cloud.

### 2. Verification engine (`verify.py`)
Two responsibilities:
- **Retrieve** — query the OpenAQ v3 API for monitoring locations near a
  latitude/longitude, then pull the latest reading from each sensor and join it
  to its parameter name and units. This is the retrieval step of a
  retrieval-augmented generation (RAG) flow: the model is grounded in real data
  rather than its own memory.
- **Verify** — load a versioned prompt, inject the real readings and the citizen
  report, and ask the LLM for a strict-JSON verdict.

### 3. Guardian (`guardian.py`)
The security layer, covered in its own section below.

### 4. Prompts (`prompts/`)
The verification prompt lives in a versioned text file, not inline in code, so it
can be iterated and diffed like any other artifact. This is deliberate: prompt
behavior is part of the system's behavior and deserves version control.

## Request lifecycle

![Request lifecycle](assets/dataflow.svg)

1. Citizen submits a report and a location.
2. **Input screening.** If the report looks like a manipulation attempt, it is
   blocked here — no model call is made. This both protects the system and saves
   cost.
3. **Retrieval.** Real readings near the location are fetched from OpenAQ.
4. **Verification.** The LLM judges the report against those readings and returns
   a verdict, a reason, and a citation.
5. **Output validation.** If the verdict is malformed or cites a reading that
   does not exist in the real data, it is downgraded to `unclear`.
6. **Result.** A trusted verdict is shown with its citation and the chart.

## The Guardian: defense in depth

![Guardian defense in depth](assets/guardian-layers.svg)

The Guardian is built on the assumption that **any single defense will eventually
be bypassed**, so it layers several.

**Input guard**
- *Normalization* unmasks obfuscation before matching: it lowercases, collapses
  spaced-out letters (`i g n o r e`), reverses common leetspeak (`1gn0re`), and
  decodes base64 payloads. This is what raised detection from 62% to 85%.
- *Pattern detection* matches five families of injection technique — instruction
  override, role manipulation, system-prompt extraction, verdict manipulation,
  and format injection — and names the one it found, so a block is explainable.

**Output guard**
- *Schema check* — the verdict must be one of `verified` / `unverified` /
  `unclear`.
- *Provenance check* — a non-`unclear` verdict must cite a reading whose value
  actually appears in the retrieved data. This is the core anti-hallucination
  mechanism: the model cannot invent evidence.

## Key design decisions

**Forced citations.** The prompt requires the model to cite a specific real
reading or return `unclear`. Without this, "verification" would be theatre. With
it, every positive verdict is auditable.

**Two-layer security, not one.** Input screening alone can be evaded by clever
phrasing; output validation alone can't tell a malicious request from an honest
one. Together they cover each other — the output provenance check catches the
data-injection attack that slips past the input filter entirely.

**Heuristics before a model.** The input guard is pattern-based and runs with no
extra LLM call. It is fast, free, explainable, and bypassable — and that last
property is documented, not hidden. A semantic LLM classifier is the planned next
layer for the gaps heuristics can't cover.

**Free tier by design.** Every dependency has a free option so the system is
reproducible by anyone, including communities without budgets.

## Known limitations

- **Sensor recency.** "Latest per sensor" can return a stale reading if a station
  stopped reporting; recency filtering is planned.
- **Coverage.** OpenAQ sensor density varies by city; sparse areas yield
  `unclear` more often.
- **Red-team scope.** The attack corpus demonstrates the method on a small set;
  it is not an exhaustive audit.
- **Single pollutant.** V1 reasons primarily over PM2.5.

These are tracked openly because naming the edges of a system is part of building
one responsibly.
