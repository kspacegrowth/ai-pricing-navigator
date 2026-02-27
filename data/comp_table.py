"""Comparable company pricing examples."""

COMP_TABLE = [
    {
        "name": "DeepL",
        "model_type": "Copilot",
        "pricing_model": "Hybrid",
        "pricing_detail": "Per user + per editable file",
        "value_driver": "Accuracy & customization",
    },
    {
        "name": "EvenUp",
        "model_type": "AI-enabled Service",
        "pricing_model": "Outcome-based",
        "pricing_detail": "Per AI-generated demand package",
        "value_driver": "Legal time saved",
    },
    {
        "name": "Graph AI",
        "model_type": "AI-enabled Service",
        "pricing_model": "Outcome-based",
        "pricing_detail": "Per case processed",
        "value_driver": "Regulatory compliance",
    },
    {
        "name": "Intercom (Fin)",
        "model_type": "Agent",
        "pricing_model": "Outcome-based",
        "pricing_detail": "$0.99 per AI resolution",
        "value_driver": "Support efficiency",
    },
    {
        "name": "Leena AI",
        "model_type": "Agent",
        "pricing_model": "Outcome-based",
        "pricing_detail": "ROI-basis, ticket threshold",
        "value_driver": "Back office automation",
    },
    {
        "name": "Pepper Content",
        "model_type": "AI-enabled Service",
        "pricing_model": "Outcome-based",
        "pricing_detail": "Per word/graphic/content piece",
        "value_driver": "Assets created",
    },
    {
        "name": "Resolve AI",
        "model_type": "Agent",
        "pricing_model": "Outcome-based",
        "pricing_detail": "Pay when AI ensures uptime",
        "value_driver": "Reliability",
    },
    {
        "name": "Sett.ai",
        "model_type": "Agent",
        "pricing_model": "Hybrid",
        "pricing_detail": "Per module + share of ad spend",
        "value_driver": "Campaign performance",
    },
    {
        "name": "Zenskar",
        "model_type": "AI-enabled Service",
        "pricing_model": "Hybrid",
        "pricing_detail": "Annual subscription + usage fees",
        "value_driver": "Billing automation",
    },
]


def get_comps_by_model(model_type):
    """Return comp table entries matching the given model type.

    Args:
        model_type: "Copilot", "Agent", or "AI-enabled Service"

    Returns:
        List of matching company dicts.
    """
    return [c for c in COMP_TABLE if c["model_type"] == model_type]
