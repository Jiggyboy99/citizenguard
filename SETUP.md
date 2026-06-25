# CitizenGuard — Setup, Step by Step

This walks you from a fresh machine to a working verdict on screen. Don't skip
steps. After each step there's an **Expected result** — if you don't see it, stop
and check the Troubleshooting table at the bottom before moving on.

Where commands differ between operating systems, you'll see a **Windows** line
and a **Mac/Linux** line. Run the one for your machine.

---

## Step 0 — Prerequisites (check these first)

You need three things installed: **Python 3.9+**, **git**, and a terminal.

**Check Python:**
```
python --version
```
If that fails, try:
```
python3 --version
```
- **Expected result:** something like `Python 3.11.x` (any 3.9 or higher is fine).
- If neither works, install Python from https://www.python.org/downloads/ — and
  on Windows, **tick "Add Python to PATH"** on the first install screen.

**Check git:**
```
git --version
```
- **Expected result:** `git version 2.x.x`.
- If missing, install from https://git-scm.com/downloads.

> Note on the `python` vs `python3` command: on Mac/Linux it's usually `python3`.
> On Windows it's usually `python`. Use whichever one printed a version above.
> The rest of this guide writes `python` — swap in `python3` if that's yours.

---

## Step 1 — Get the code into a folder

You already downloaded `citizenguard.zip`. Unzip it somewhere you'll find it
(e.g. your Desktop or a `projects` folder). You should end up with a folder
called `citizenguard` containing `verify.py`, `requirements.txt`, and the
sub-folders.

Add this `SETUP.md` file into that `citizenguard` folder if it isn't there
already.

---

## Step 2 — Open a terminal *inside* that folder

This is the step people get wrong. The terminal has to be "pointed at" the
project folder.

- **Windows:** open the `citizenguard` folder in File Explorer, click the address
  bar, type `cmd`, press Enter. (Or: right-click inside the folder →
  "Open in Terminal".)
- **Mac:** right-click the folder → Services → "New Terminal at Folder". Or open
  Terminal and type `cd ` (with a space) then drag the folder onto the window,
  then Enter.
- **Linux:** right-click inside the folder → "Open Terminal Here".

**Confirm you're in the right place:**
```
dir          (Windows)
ls           (Mac/Linux)
```
- **Expected result:** you see `verify.py`, `requirements.txt`, `prompts`, etc.
  If you don't, you're in the wrong folder — `cd` into the right one.

---

## Step 3 — Create a virtual environment

A virtual environment ("venv") keeps this project's packages separate from the
rest of your system. Always do this for Python projects — it's a habit recruiters
notice the absence of.

```
python -m venv .venv
```
- **Expected result:** a new hidden folder `.venv` appears (it's already in
  `.gitignore`, so it won't get committed).

**Now activate it:**
- **Windows (cmd):**
  ```
  .venv\Scripts\activate
  ```
- **Windows (PowerShell):**
  ```
  .venv\Scripts\Activate.ps1
  ```
- **Mac/Linux:**
  ```
  source .venv/bin/activate
  ```
- **Expected result:** your terminal prompt now starts with `(.venv)`. That's how
  you know it's active. You'll re-activate it every time you come back to the
  project in a new terminal.

> PowerShell may block activation with a script-policy error. Fix it by running
> PowerShell once and entering:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` then try again.

---

## Step 4 — Install the dependencies

```
pip install -r requirements.txt
```
- **Expected result:** pip downloads and installs `requests` and `python-dotenv`,
  ending with a line like `Successfully installed ...`.

Verify it worked:
```
pip list
```
- **Expected result:** `requests` and `python-dotenv` appear in the list.

---

## Step 5 — Get your OpenAQ API key (free)

1. Go to **https://explore.openaq.org** and sign up for an account.
2. Verify your email if prompted.
3. Once logged in, find your **API key** in your account settings / profile area
   (look for "API Key").
4. Copy it. Treat it like a password.

- **Expected result:** you have a long string copied to your clipboard.

---

## Step 6 — Get your Groq API key (free)

1. Go to **https://console.groq.com** and sign up / log in.
2. Find the **API Keys** section (usually in the left-hand menu).
3. Click **Create API Key**, give it any name, and copy the key **immediately** —
   Groq only shows it once.

- **Expected result:** a second long string copied somewhere safe.

> The dashboards for both sites change their layout from time to time. If a button
> name here doesn't match exactly, look for the words "API Key" — that's what you
> want.

---

## Step 7 — Put your keys in a .env file

The repo has `.env.example` as a template. You make a real `.env` from it.

**Copy the template:**
- **Windows:**
  ```
  copy .env.example .env
  ```
- **Mac/Linux:**
  ```
  cp .env.example .env
  ```

**Now open `.env` in any text editor** (Notepad, VS Code, TextEdit) and replace
the placeholder text with your real keys. It should look like:
```
OPENAQ_API_KEY=abc123yourrealkey
GROQ_API_KEY=gsk_yourrealkey
```
- No quotes, no spaces around the `=`.
- Save the file.

- **Expected result:** a file named exactly `.env` (not `.env.txt`) with both real
  keys. On Windows, make sure Notepad didn't add `.txt` — use "Save as" → "All
  files" if needed.

> `.env` is in `.gitignore`, so your keys will **not** be uploaded to GitHub.
> That's deliberate and correct. Never commit real keys.

---

## Step 8 — Run it

Make sure your prompt still shows `(.venv)`, then:
```
python verify.py
```

- **Expected result:** something like:
  ```
  Fetching real air-quality data...
  Got 7 readings.

  - pm25 = 31.4 ug/m3 at 2026-06-25T09:00:00Z (Some Station Name)
  - pm10 = 58.0 ug/m3 at 2026-06-25T09:00:00Z (Some Station Name)
  ...

  Verifying the citizen report...

  {
    "verdict": "unverified",
    "reasoning": "Recent PM2.5 readings are moderate, not hazardous...",
    "citation": "pm25 = 31.4 ug/m3 at 2026-06-25T09:00:00Z"
  }
  ```

If you got a JSON verdict with a citation — **you've shipped the core of the
product.** That's the milestone for tonight.

---

## Step 9 — Read what came back

- **verdict** — `verified` (data backs the report), `unverified` (data contradicts
  it), or `unclear` (no data to judge).
- **reasoning** — one or two sentences of why.
- **citation** — the exact real reading the model leaned on. If this says `none`,
  the verdict should be `unclear` — that's the anti-hallucination rule working.

Try changing the `sample_report` text near the bottom of `verify.py` to something
alarming ("the air is deadly, evacuate") and run again. Watch whether the verdict
matches the real data. That contrast is your demo.

---

## Troubleshooting

| What you see | What it means | Fix |
|---|---|---|
| `OPENAQ_API_KEY is missing` | `.env` not found or key not set | Confirm the file is named exactly `.env`, in the project folder, with the real key |
| `401` or `Unauthorized` from OpenAQ | bad/expired key | Re-copy the key from explore.openaq.org; no extra spaces |
| `Got 0 readings.` | no sensors near Lagos coords | Not a bug. Open `verify.py`, change `DEFAULT_LAT/LON` to Delhi (28.6139, 77.2090) or LA (34.0522, -118.2437) to confirm the pipeline, then return to Lagos |
| `model ... does not exist` / `400` from Groq | model name changed | Open `verify.py`, update `GROQ_MODEL` to a current model from console.groq.com |
| `model did not return valid JSON` | model added extra text | Re-run (temperature is 0, usually fixes itself); if persistent, tell me and we'll tighten the prompt |
| `ModuleNotFoundError: requests` | venv not active or deps not installed | Re-activate venv (Step 3), re-run Step 4 |
| `python: command not found` | wrong command for your OS | Use `python3` instead |
| SSL / connection errors | network/proxy blocking | Try another network; corporate/school wifi sometimes blocks API calls |

---

## Step 10 — Turn it into a GitHub repo

Once it runs, make it real on GitHub so you have commit history (recruiters read
this).

```
git init
git add .
git commit -m "CitizenGuard: working core verifier (OpenAQ + LLM, with citations)"
```

Then create an **empty** repo on github.com (no README, since you have one), copy
the URL it gives you, and:
```
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/citizenguard.git
git push -u origin main
```
- **Expected result:** refresh the GitHub page and your code is there — **without**
  the `.env` file (check this: your keys must not be visible).

---

## You're done for tonight when...

- `python verify.py` prints a verdict with a citation, **and**
- the code is pushed to GitHub with no keys leaked.

**Next session:** wrap this in a Gradio UI (clickable demo), then build the
Guardian security layer — the part that makes this an AI-security project.
