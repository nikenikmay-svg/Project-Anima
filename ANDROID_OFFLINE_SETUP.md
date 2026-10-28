# Run Anima on Android without an API key

## Easiest first step: offline demo

The offline demo proves that Anima can create a structured multi-agent-style report without credentials or network access. **It uses fixed text templates, not an AI model.** It is a safe first test before setting up real local inference.

### 1. Install Termux

Install Termux from its official F-Droid page or official GitHub releases, not from an old Play Store build:
- https://f-droid.org/packages/com.termux/
- https://github.com/termux/termux-app/releases

### 2. Install Python and Git

Open Termux and enter:

```bash
pkg update
pkg install python git
```

Confirm Python works:

```bash
python --version
```

### 3. Download Anima

```bash
git clone https://github.com/nikenikmay-svg/Project-Anima.git
cd Project-Anima
```

If Git says the folder already exists, use `cd Project-Anima` instead of cloning again.

### 4. Run the no-key demo

```bash
python offline_council_demo.py --question "How could daily routines support psychological resilience?" --output offline-demo-report.json
```

Read the report:

```bash
cat offline-demo-report.json
```

You can change the question to anything non-sensitive. This demo makes no network requests, uses no API key, and does not write to Anima's long-term memory.

## Want a real AI model running locally?

That is a separate next step. A local model can avoid provider API keys, but it needs a compatible model file, storage, RAM, and CPU time. On a phone, use a small quantized model and expect slower responses; do not download a large model before checking available storage and memory. A local model's quality will vary, and installing Termux alone does not install an AI model.

## Safety

- Never paste an API key into the terminal screenshots or repository.
- Only clone the repository URL shown above.
- Do not submit confidential client or personal information to an online service.
- The offline demo is intentionally labeled as simulated; do not mistake its template responses for research findings.
