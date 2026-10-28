"""Conservative lexical review flags for claims; not a semantic reasoner."""
import re


_RULES = {
    "causal_language": (
        re.compile(r"\b(?:caused|causes|causing|led to|leads to|resulted in|results in|proves|demonstrates)\b", re.I),
        "Claim uses causal or strong evidential wording; check whether the context supports it.",
    ),
    "broad_generalization": (
        re.compile(r"\b(?:everyone|everybody|all people|always|never|in every respect|for everyone)\b", re.I),
        "Claim may generalize beyond the described sample or measure.",
    ),
    "motive_attribution": (
        re.compile(r"\b(?:because they don't care|because they do not care|doesn't care about|does not care about|intentionally|on purpose)\b", re.I),
        "Claim attributes a motive or intention that may not be established by the supplied context.",
    ),
    "certainty_language": (
        re.compile(r"\b(?:certainly|undoubtedly|without doubt|guarantees|guaranteed|definitely)\b", re.I),
        "Strong certainty wording may exceed the available evidence.",
    ),
}


def audit_claim(prompt, claim, context=""):
    """Return lexical review flags while leaving semantic validity unassessed."""
    for name, value in (("prompt", prompt), ("claim", claim), ("context", context)):
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
    if not claim.strip():
        raise ValueError("claim must not be empty")

    flags = []
    for rule, (pattern, explanation) in _RULES.items():
        match = pattern.search(claim)
        if match:
            flags.append({
                "rule": rule,
                "matched_text": match.group(0),
                "explanation": explanation,
            })

    return {
        "prompt": prompt,
        "claim": claim,
        "context": context,
        "review_flags": flags,
        "review_flag_count": len(flags),
        "semantic_assessment": {
            "evidence_support": "not_assessed",
            "inference_validity": "not_assessed",
            "reason": "Lexical flags identify passages for review; they do not determine truth or logical validity.",
        },
        "notice": "Prototype heuristic, not a verdict. A missing flag does not mean a claim is valid.",
    }
