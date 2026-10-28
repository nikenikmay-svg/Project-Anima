# Agent council starter guide

This starter kit helps you connect Anima to real AI services, but it does not contain credentials and will not contact any provider until you run the council yourself.

## 1. Choose compatible services

The current adapter expects an OpenAI-compatible Chat Completions endpoint. For each agent, check the provider's current documentation for:
- the exact HTTPS Chat Completions endpoint;
- the exact model identifier;
- whether it accepts a Bearer API key and supports the expected response shape;
- pricing, free-tier limits, and data-retention terms.

You can use two different services, or two models from one service. Different model names do not guarantee independent reasoning.

## 2. Prepare a private config

Copy `agents.example.json` to `agents.local.json` on the computer where Python will run, then replace the example endpoints and model names with values from your chosen provider documentation. Do not commit `agents.local.json`.

## 3. Add API keys to the environment

Set each key as an environment variable matching `api_key_env` in your config:
- `ANIMA_RESEARCHER_API_KEY`
- `ANIMA_SKEPTIC_API_KEY`
- `ANIMA_SYNTH_API_KEY`

Keep keys in your local environment or a secret manager. Never put them in a Python file, JSON config, chat message, screenshot, GitHub commit, or report. You may reuse a provider key for more than one agent if its terms allow it, but usage can still incur charges.

Example for a temporary Linux/macOS terminal session:

```bash
export ANIMA_RESEARCHER_API_KEY='paste-key-in-your-own-terminal'
export ANIMA_SKEPTIC_API_KEY='paste-key-in-your-own-terminal'
export ANIMA_SYNTH_API_KEY='paste-key-in-your-own-terminal'
python agent_council.py --config agents.local.json --question "What evidence would change our view of this claim?" --output council-report.json
```

Do not paste real keys into this guide or into the repository. The sample values above are instructional placeholders, not credentials.

## 4. Check the output

Open `council-report.json`. It records each agent's status and response, plus the synthesizer's comparison if configured. A skipped or failed agent is not evidence that the other agents are correct. Treat all responses as hypotheses until sources and claims are checked independently.

## Important limits

- This is an operator-run tool, not a background process. It does not run automatically or discover agents on the internet.
- It sends your question to each configured provider. Do not include private client, health, financial, or other confidential information unless you have permission and have checked the provider's terms.
- Provider calls may cost money. Run a short test first and check your provider's current pricing.
- The council does not automatically add its transcript to Anima's long-term memory.
- If you only have an Android phone, you will need a Python-capable environment such as a trusted cloud development environment or Termux. The GitHub mobile app alone does not run this Python CLI.
