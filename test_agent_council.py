import json
import os
import unittest
from unittest.mock import patch

from agent_council import run_council, validate_config


def agent(name, role, key_env):
    return {
        "name": name,
        "role": role,
        "endpoint": "https://example.com/v1/chat/completions",
        "model": "test-model",
        "api_key_env": key_env,
    }


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return json.dumps({"choices": [{"message": {"content": self.content}}]}).encode()


class AgentCouncilTests(unittest.TestCase):
    def test_requires_two_to_four_unique_agents(self):
        with self.assertRaises(ValueError):
            validate_config({"agents": [agent("one", "researcher", "KEY")]})
        with self.assertRaises(ValueError):
            validate_config({"agents": [agent("same", "researcher", "A"),
                                        agent("same", "skeptic", "B")]})

    def test_rejects_insecure_remote_endpoint(self):
        cfg = {"agents": [agent("a", "researcher", "A"), agent("b", "skeptic", "B")]}
        cfg["agents"][0]["endpoint"] = "http://example.com/chat"
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_missing_credentials_are_reported_without_network_call(self):
        cfg = {"agents": [agent("a", "researcher", "ANIMA_TEST_KEY_A"),
                          agent("b", "skeptic", "ANIMA_TEST_KEY_B")]}
        with patch.dict(os.environ, {}, clear=True):
            report = run_council("Is this claim supported?", cfg)
        self.assertEqual([r["status"] for r in report["responses"]], ["skipped", "skipped"])

    def test_synthesizer_receives_other_agents_responses(self):
        cfg = {"agents": [agent("researcher", "find evidence", "ANIMA_TEST_KEY_A"),
                          agent("skeptic", "challenge claims", "ANIMA_TEST_KEY_B"),
                          agent("synth", "compare arguments", "ANIMA_TEST_KEY_C")],
               "synthesizer": "synth"}
        def fake_opener(request, timeout=0):
            body = json.loads(request.data.decode())
            if body["model"] == "test-model" and "Original question:" in body["messages"][-1]["content"]:
                return FakeResponse("Two agents were compared; disagreement remains.")
            return FakeResponse("Initial view with uncertainty.")
        env = {"ANIMA_TEST_KEY_A": "test-a", "ANIMA_TEST_KEY_B": "test-b", "ANIMA_TEST_KEY_C": "test-c"}
        with patch.dict(os.environ, env, clear=True):
            report = run_council("What is the evidence?", cfg, opener=fake_opener)
        self.assertEqual(report["synthesis"]["status"], "completed")
        self.assertIn("disagreement remains", report["synthesis"]["response"])
        self.assertEqual(sum(r["status"] == "completed" for r in report["responses"]), 3)

    def test_rejects_blank_or_oversized_question(self):
        cfg = {"agents": [agent("a", "researcher", "A"), agent("b", "skeptic", "B")]}
        with self.assertRaises(ValueError):
            run_council("  ", cfg)
        with self.assertRaises(ValueError):
            run_council("x" * 8001, cfg)


if __name__ == "__main__":
    unittest.main()
