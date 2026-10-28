# Anima first-run: Gemini API

This is the simplest first connection for the current multi-agent council. It uses Google's OpenAI-compatible Gemini endpoint and one environment variable for the key. The three roles are separate prompts, but they use the same model/provider, so their answers are not fully independent.

## 1. Create an API key

1. Open [Google AI Studio](https://aistudio.google.com/apikey).
2. Sign in and create an API key for a project eligible for the Gemini API free tier.
3. Keep the key private. Do not paste it into GitHub files, commits, issues, screenshots, or this chat.

Google's free tier is limited to eligible models and quotas; eligibility and limits can vary. Review [current Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) and [billing information](https://ai.google.dev/gemini-api/docs/billing) before using it. Free-tier data may be used to improve Google's products, so do not submit confidential or sensitive information.

## 2. Configure the local environment

The ready-to-edit `agents.example.json` uses the documented endpoint `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`, model `gemini-3.8-flash`, and the environment variable `ANIMA_GEMINI_API_KEY`.

On a computer with Python, set the key in your terminal environment, then run:

```bash
export ANIMA_GEMINI_API_KEY='your-key-pasted-locally'
python agent_council.py --config agents.example.json --question "Give three arguments for and against the claim that daily routines build resilience. State uncertainty." --output council-report.json
```

On Windows PowerShell, the temporary-session equivalent is:

```powershell
$env:ANIMA_GEMINI_API_KEY = "your-key-pasted-locally"
python agent_council.py --config agents.example.json --question "Give three arguments for and against the claim that daily routines build resilience. State uncertainty." --output council-report.json
```

Do not commit the key. The JSON config contains only the name of the environment variable, not the key itself.

## 3. Understand the result

Open `council-report.json`. Researcher and Skeptic answer independently first; Synthesizer then receives the other completed answers and compares them. This run makes four model requests when all three agents respond (three initial answers plus one synthesis), so check the provider's current limits. The council does not automatically save the report into long-term memory.

## Android note

The GitHub Android app can view the code but does not run the Python CLI. To execute this first test, use a trusted Python environment you control (for example, a local Termux setup or a private cloud development environment). If you use a cloud environment, store the key in its secret/environment settings, never in the repository.

## Safety and limitations

- The CLI only runs when you start it; no scheduled workflow calls this API.
- The example uses the same model/provider for all three roles. This tests the interaction flow but does not provide independent provider diversity.
- Model output is not verified fact; check important claims and sources independently.
- API usage may be restricted by account eligibility and quota. Do not enable paid billing unless you knowingly choose to.
