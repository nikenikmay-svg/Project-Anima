# Anima Source Comparison — 2026-11-15 (UTC)

**Input report:** roaming-2026-11-15.md
**Items compared:** 30

**Method:** compare visible titles and short snippets using fixed keyword lists. Similar terms are leads for human review, not proof that sources agree.

## Topic overlap across sources

### evidence and verification
- [11. QWED-AI/qwed-a2a](https://github.com/QWED-AI/qwed-a2a) — terms: verification
- [16. love530love/agent-evolution-protocol](https://github.com/love530love/agent-evolution-protocol) — terms: evidence

### agents and autonomy
- [1. vlv-code/meta-project](https://github.com/vlv-code/meta-project) — terms: agents
- [2. ykoh42/exaone-integrations](https://github.com/ykoh42/exaone-integrations) — terms: agent
- [3. edgespine-dev/policier_example](https://github.com/edgespine-dev/policier_example) — terms: agent, orchestration
- [4. kiazh/Machina-Harness](https://github.com/kiazh/Machina-Harness) — terms: agent, orchestration
- [5. tech-anupam/awesome-agentic-ecosystem](https://github.com/tech-anupam/awesome-agentic-ecosystem) — terms: agent, agents
- [6. openai/openai-agents-python](https://github.com/openai/openai-agents-python) — terms: agent, agents
- [7. mingqian0850/awesome_harness_agent](https://github.com/mingqian0850/awesome_harness_agent) — terms: agent
- [8. skyfireitdiy/Jarvis](https://github.com/skyfireitdiy/Jarvis) — terms: agent, agents
- [9. inbravo/agent-bench](https://github.com/inbravo/agent-bench) — terms: agent
- [10. keithdit4e/teotl](https://github.com/keithdit4e/teotl) — terms: agents, autonomous
- [11. QWED-AI/qwed-a2a](https://github.com/QWED-AI/qwed-a2a) — terms: agent
- [12. NTinkicht/OneCompany](https://github.com/NTinkicht/OneCompany) — terms: agent, autonomous
- [13. Sunnykakdiya/Multi-Agents-Travel-System](https://github.com/Sunnykakdiya/Multi-Agents-Travel-System) — terms: agents
- [14. coapis-ai/coapis-agent](https://github.com/coapis-ai/coapis-agent) — terms: agent
- [15. saumyashah0510/Multi-Agent-Research-System-Architecture](https://github.com/saumyashah0510/Multi-Agent-Research-System-Architecture) — terms: agent
- [16. love530love/agent-evolution-protocol](https://github.com/love530love/agent-evolution-protocol) — terms: agent
- [17. the-magi-system/magi](https://github.com/the-magi-system/magi) — terms: agent
- [18. weideyouni/holoaeon](https://github.com/weideyouni/holoaeon) — terms: agent
- [20. AutomatosAI/automatos-ai](https://github.com/AutomatosAI/automatos-ai) — terms: agents
- [21. AnkTechsol/Satya_AI](https://github.com/AnkTechsol/Satya_AI) — terms: agent, agents, autonomous
- [22. pine-tree111/open-longevity](https://github.com/pine-tree111/open-longevity) — terms: agent, autonomous
- [23. saccromcyes/No-Code-AGI](https://github.com/saccromcyes/No-Code-AGI) — terms: agents, autonomous
- [24. Senpi-ai/senpi-skills](https://github.com/Senpi-ai/senpi-skills) — terms: agent, autonomous
- [25. samugit83/redamon](https://github.com/samugit83/redamon) — terms: agent, tool
- [26. Tryboy869/grok-local-agent-kit](https://github.com/Tryboy869/grok-local-agent-kit) — terms: agent, agents
- [27. emam26/ReproScout](https://github.com/emam26/ReproScout) — terms: agent, autonomous
- [28. Ricardo4007/OpenPDA](https://github.com/Ricardo4007/OpenPDA) — terms: autonomous
- [29. dilliram-code/code-archaeologist](https://github.com/dilliram-code/code-archaeologist) — terms: agent, autonomous
- [30. yuklcool/agentdock](https://github.com/yuklcool/agentdock) — terms: agents, autonomous

### human oversight
- [25. samugit83/redamon](https://github.com/samugit83/redamon) — terms: human

### memory and context
- [1. vlv-code/meta-project](https://github.com/vlv-code/meta-project) — terms: knowledge, context
- [4. kiazh/Machina-Harness](https://github.com/kiazh/Machina-Harness) — terms: memory, context
- [14. coapis-ai/coapis-agent](https://github.com/coapis-ai/coapis-agent) — terms: knowledge
- [20. AutomatosAI/automatos-ai](https://github.com/AutomatosAI/automatos-ai) — terms: knowledge
- [21. AnkTechsol/Satya_AI](https://github.com/AnkTechsol/Satya_AI) — terms: knowledge
- [30. yuklcool/agentdock](https://github.com/yuklcool/agentdock) — terms: memory, persistent

## Comparison questions

- Do sources discuss the same problem, or merely use similar terminology?
- Are their datasets, tasks, baselines, and evaluation measures comparable?
- What counterexample would show that a claimed improvement is only keyword overlap?
- What limitations or contradictory findings appear in the full original sources?

## Candidate evaluator tests (drafts only)

Review these ideas manually. Do not add them to benchmark_cases.json until expected labels are justified independently.
### quoted_claim
- Example: The article quotes someone saying "evidence is irrelevant," then rejects that statement.
- Review question: Check whether quoted negation is incorrectly treated as the author's own position.
- Expected labels: **not assigned**; a human must define them after reviewing intended behavior.

### indicator_without_support
- Example: The answer says, "Evidence proves the claim because I say so."
- Review question: Check whether indicator words are mistaken for a supported argument.
- Expected labels: **not assigned**; a human must define them after reviewing intended behavior.

### uncertainty_scope
- Example: The estimate may be unreliable, while the measurement procedure is documented.
- Review question: Check whether uncertainty language contaminates a separate supported criterion.
- Expected labels: **not assigned**; a human must define them after reviewing intended behavior.

### same_word_different_meaning
- Example: The agent will review the model; the reviewer will assess the agent.
- Review question: Check whether repeated terms are treated as repeated evidence of the same claim.
- Expected labels: **not assigned**; a human must define them after reviewing intended behavior.

## Limits

- This script does not fetch or verify full articles.
- Keyword overlap does not establish agreement, causality, quality, or truth.
- Test ideas are not benchmark cases and do not alter the evaluator.
