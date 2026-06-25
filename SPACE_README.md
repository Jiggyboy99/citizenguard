---
title: CitizenGuard
emoji: 🌍
colorFrom: green
colorTo: indigo
sdk: gradio
sdk_version: 6.19.0
app_file: app.py
pinned: false
license: mit
---

# CitizenGuard

**AI-verified citizen air-quality reports, hardened against prompt injection.**

Type a report about local air quality, pick a location, and CitizenGuard checks
it against **real public sensor data** (OpenAQ), returning a verdict —
verified / unverified / unclear — that must cite a real reading. A **Guardian**
layer screens every report for prompt-injection attempts before it reaches the
model, and validates every verdict against the real data afterwards.

Try the examples, including the last one — it's an attack, and the Guardian
blocks it.

Source, security assessment, and red-team suite:
https://github.com/Jiggyboy99/citizenguard
