# Anima multi-agent council

## What it enables

`agent_council.py` lets Anima send one research question to 2–4 explicitly configured AI agents using OpenAI-compatible Chat Completions APIs. Agents respond independently; an optional configured synthesizer receives the other completed responses and compares their arguments.

This is a connector framework, not automatic discovery of agents. It contacts only the endpoints named in the local JSON config. Different providers may require provider-specific endpoint/model settings.

## Configure locally

Create a private local file such as `agents.local.json` (do not commit it):

```json
{
  "agents": [
    {
      "name": "Researcher",
      "role": "find relevant evidence and explain limitations",
      "endpoint": "https://YOUR-PROVIDER/v1/chat/completions",
      "model": "YOUR-MODEL",
      "api_key_env": "ANIMA_RESEARCHER_API_KEY"
    },
    {
      "name": "Skeptic",
      "role": "challenge assumptions and identify alternative explanations",
      "endpoint": "https://YOUR-OTHER-PROVIDER/v1/chat/completions",
      "model": "YOUR-OTHER-MODEL",
      "api_key_env": "ANIMA_SKEPTIC_API_KEY"
    },
    {
      "name": "Synthesizer",
      "role": "compare arguments and report agreement, disagreement, and uncertainty",
      "endpoint": "https://YOUR-PROVIDER/v1/chat/completions",
      "model": "YOUR-MODEL",
      "api_key_env": "ANIMA_SYNTH_API_KEY"
    }
  ],
  "synthesizer": "Synthesizer"
}
```

Set the named environment variables to API keys without putting keys in source code, config files, logs, or GitHub commits. Run:

```bash
python agent_council.py --config agents.local.json --question "What evidence supports this claim?" --output council-report.json
```

The endpoint and model names above are placeholders, not working credentials. Each provider may charge for requests. Start with a small question and low request limits. Do not send sensitive or confidential data to external providers unless you have checked their data handling terms and have permission.

## Safety and limitations

- Supports 2–4 configured agents and a bounded question/response size.
- Remote endpoints must use HTTPS; HTTP is allowed only for localhost testing.
- API keys are read from environment variables and never intentionally included in the report.
- Agent responses and consensus are not proof. The synthesizer is another model and can also be wrong.
- Provider output is treated as untrusted text; it is never executed.
- Reports are written only when the operator specifies an output path. The council does not silently write conversations into Anima's long-term memory.
- GitHub Actions is not configured to call paid model APIs. This avoids unexpectedly spending money or requiring API secrets in the repository. Add provider secrets and a reviewed workflow only if scheduled agent conversations are later desired.
- Only OpenAI-compatible Chat Completions APIs are supported by this first adapter; other agent platforms need their own adapters.
