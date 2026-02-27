"""Scoring and calculation helpers for all modules."""

import sys
import os

# Allow imports from project root when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.questions import QUESTIONS_BY_ID, MODULE_1_QUESTIONS, MODULE_2_QUESTIONS


def classify_business_model(answers):
    """Classify business model from Module 1 answers.

    Args:
        answers: dict mapping question_id -> selected value
                 e.g. {"m1_q1": "yes", "m1_q2": "partial", ...}

    Returns:
        (model_name, confidence) where confidence is a percentage (0-100).
    """
    totals = {"copilot_score": 0, "agent_score": 0, "service_score": 0}

    for q in MODULE_1_QUESTIONS:
        selected = answers.get(q["id"])
        if selected is None or q["options"] is None:
            continue
        for opt in q["options"]:
            if opt["value"] == selected:
                for dim, val in opt["scores"].items():
                    totals[dim] = totals.get(dim, 0) + val
                break

    model_map = {
        "copilot_score": "Copilot",
        "agent_score": "Agent",
        "service_score": "AI-enabled Service",
    }

    top_dim = max(totals, key=totals.get)
    top_score = totals[top_dim]
    total = sum(totals.values())
    confidence = round((top_score / total) * 100, 1) if total > 0 else 0.0

    return model_map[top_dim], confidence


def calculate_value_position(answers):
    """Calculate value framework position from Module 2 answers.

    Args:
        answers: dict mapping question_id -> selected value

    Returns:
        (x_score, y_score, quadrant_label)
        x: -1 to 1 (cost savings to revenue uplift)
        y: -1 to 1 (soft ROI to hard ROI)
    """
    x_scores = []
    y_scores = []

    for q in MODULE_2_QUESTIONS:
        selected = answers.get(q["id"])
        if selected is None or q["options"] is None:
            continue
        for opt in q["options"]:
            if opt["value"] == selected:
                x_scores.append(opt["scores"]["x_score"])
                y_scores.append(opt["scores"]["y_score"])
                break

    x = sum(x_scores) / len(x_scores) if x_scores else 0.0
    y = sum(y_scores) / len(y_scores) if y_scores else 0.0

    # Clamp to [-1, 1]
    x = max(-1.0, min(1.0, x))
    y = max(-1.0, min(1.0, y))

    if x >= 0 and y > 0:
        quadrant = "Revenue Engine"
    elif x < 0 and y > 0:
        quadrant = "Efficiency Machine"
    elif x >= 0 and y <= 0:
        quadrant = "Promise Zone"
    else:
        quadrant = "Danger Zone"

    return round(x, 3), round(y, 3), quadrant


def generate_pricing_formula(cost_per_unit, target_margin, deal_size, model_type):
    """Generate pricing formula based on BVP hybrid model.

    Args:
        cost_per_unit: float, cost to deliver one unit of value
        target_margin: float, target gross margin percentage (40-85)
        deal_size: float, target annual deal size in dollars
        model_type: "Copilot", "Agent", or "AI-enabled Service"

    Returns:
        dict with platform_fee, included_units, overage_rate, effective_price, gross_margin
    """
    if cost_per_unit <= 0 or target_margin >= 100:
        return {
            "platform_fee": 0,
            "included_units": 0,
            "overage_rate": 0,
            "effective_price": 0,
            "gross_margin": 0,
        }

    # Target price per unit to achieve desired margin
    price_per_unit = cost_per_unit / (1 - target_margin / 100)

    # Estimate monthly units from deal size
    monthly_units = deal_size / 12 / price_per_unit

    # Model-type adjustments
    if model_type == "Copilot":
        fee_multiplier = 2.0   # Standard base coverage
        unit_divisor = 1.5
        overage_multiplier = 1.2
    elif model_type == "Agent":
        fee_multiplier = 1.5   # Lower base, more outcome-aligned
        unit_divisor = 1.3
        overage_multiplier = 1.3
    else:  # AI-enabled Service
        fee_multiplier = 2.2   # Higher base, service-level commitment
        unit_divisor = 1.6
        overage_multiplier = 1.15

    # Platform fee = cost coverage * multiplier for estimated usage
    platform_fee = round(cost_per_unit * monthly_units * fee_multiplier, 2)

    # Included units in the platform fee
    included_units = max(1, int(platform_fee / (price_per_unit * unit_divisor)))

    # Overage rate for additional units
    overage_rate = round(price_per_unit * overage_multiplier, 2)

    # Effective annual price (platform fee * 12)
    effective_price = round(platform_fee * 12, 2)

    # Actual gross margin based on included units
    annual_cost = cost_per_unit * included_units * 12
    gross_margin = round(
        (effective_price - annual_cost) / effective_price * 100, 1
    ) if effective_price > 0 else 0

    return {
        "platform_fee": platform_fee,
        "included_units": included_units,
        "overage_rate": overage_rate,
        "effective_price": effective_price,
        "gross_margin": gross_margin,
    }


def calculate_health_score(scores):
    """Calculate health check score from Module 4 answers.

    Args:
        scores: dict mapping question_id -> score (1-5)
                e.g. {"m4_q1": 4, "m4_q2": 2, ...}

    Returns:
        (percentage, label, top_3_priority_ids)
    """
    total = sum(scores.values())
    max_possible = len(scores) * 5
    percentage = round((total / max_possible) * 100, 1) if max_possible > 0 else 0

    if percentage >= 85:
        label = "Advanced"
    elif percentage >= 70:
        label = "Strong"
    elif percentage >= 50:
        label = "Developing"
    else:
        label = "Early Stage"

    # Top 3 priorities = questions with lowest scores
    sorted_ids = sorted(scores, key=scores.get)
    top_3 = sorted_ids[:3]

    return percentage, label, top_3


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Running scoring tests...\n")

    # --- Test classify_business_model ---
    # All copilot-heavy answers
    copilot_answers = {
        "m1_q1": "yes",       # copilot: 3
        "m1_q2": "no",        # copilot: 3
        "m1_q3": "partial",   # copilot: 2
        "m1_q4": "chat",      # copilot: 3
        "m1_q5": "advisor",   # copilot: 3
    }
    model, conf = classify_business_model(copilot_answers)
    assert model == "Copilot", f"Expected Copilot, got {model}"
    assert conf > 50, f"Expected confidence > 50, got {conf}"
    print(f"  Copilot classification: {model} ({conf}%) - PASS")

    # All agent-heavy answers
    agent_answers = {
        "m1_q1": "no",        # agent: 2
        "m1_q2": "yes",       # agent: 3
        "m1_q3": "no",        # agent: 2
        "m1_q4": "automation", # agent: 3
        "m1_q5": "executor",  # agent: 3
    }
    model, conf = classify_business_model(agent_answers)
    assert model == "Agent", f"Expected Agent, got {model}"
    assert conf > 50, f"Expected confidence > 50, got {conf}"
    print(f"  Agent classification: {model} ({conf}%) - PASS")

    # All service-heavy answers
    service_answers = {
        "m1_q1": "no",        # service: 2
        "m1_q2": "partial",   # service: 2
        "m1_q3": "yes",       # service: 3
        "m1_q4": "output",    # service: 3
        "m1_q5": "service_provider",  # service: 3
    }
    model, conf = classify_business_model(service_answers)
    assert model == "AI-enabled Service", f"Expected AI-enabled Service, got {model}"
    assert conf > 40, f"Expected confidence > 40, got {conf}"
    print(f"  Service classification: {model} ({conf}%) - PASS")

    # --- Test calculate_value_position ---
    # Revenue + hard ROI
    revenue_hard = {
        "m2_q1": "revenue",       # x: 1.0, y: 0.5
        "m2_q2": "yes",           # x: 0.0, y: 1.0
        "m2_q3": "lose_revenue",  # x: 0.5, y: 1.0
        "m2_q4": "dashboard",     # x: 0.0, y: 1.0
        "m2_q5": "no",            # x: 0.5, y: -0.5
    }
    x, y, quad = calculate_value_position(revenue_hard)
    assert quad == "Revenue Engine", f"Expected Revenue Engine, got {quad}"
    assert x > 0, f"Expected x > 0, got {x}"
    assert y > 0, f"Expected y > 0, got {y}"
    print(f"  Revenue Engine: x={x}, y={y}, quad={quad} - PASS")

    # Cost savings + hard ROI
    cost_hard = {
        "m2_q1": "cost_reduction",  # x: -1.0, y: 0.5
        "m2_q2": "yes",            # x: 0.0, y: 1.0
        "m2_q3": "slower",         # x: -0.5, y: 0.5
        "m2_q4": "dashboard",      # x: 0.0, y: 1.0
        "m2_q5": "yes",            # x: -0.5, y: 1.0
    }
    x, y, quad = calculate_value_position(cost_hard)
    assert quad == "Efficiency Machine", f"Expected Efficiency Machine, got {quad}"
    assert x < 0, f"Expected x < 0, got {x}"
    assert y > 0, f"Expected y > 0, got {y}"
    print(f"  Efficiency Machine: x={x}, y={y}, quad={quad} - PASS")

    # Soft ROI + cost savings
    soft_cost = {
        "m2_q1": "time_savings",    # x: -0.5, y: -0.5
        "m2_q2": "no",             # x: 0.0, y: -1.0
        "m2_q3": "no_pain",        # x: 0.0, y: -1.0
        "m2_q4": "qualitative",    # x: 0.0, y: -1.0
        "m2_q5": "partial",        # x: -0.25, y: 0.5
    }
    x, y, quad = calculate_value_position(soft_cost)
    assert quad == "Danger Zone", f"Expected Danger Zone, got {quad}"
    assert y < 0, f"Expected y < 0, got {y}"
    print(f"  Danger Zone: x={x}, y={y}, quad={quad} - PASS")

    # --- Test generate_pricing_formula ---
    result = generate_pricing_formula(
        cost_per_unit=0.50,
        target_margin=65,
        deal_size=15000,
        model_type="Copilot",
    )
    assert result["platform_fee"] > 0, f"Expected positive platform_fee"
    assert result["included_units"] >= 1, f"Expected at least 1 included unit"
    assert result["overage_rate"] > 0, f"Expected positive overage_rate"
    assert result["effective_price"] > 0, f"Expected positive effective_price"
    assert 0 < result["gross_margin"] < 100, f"Expected margin 0-100, got {result['gross_margin']}"
    print(f"  Pricing formula: fee=${result['platform_fee']}/mo, "
          f"{result['included_units']} units, "
          f"overage=${result['overage_rate']}, "
          f"annual=${result['effective_price']}, "
          f"margin={result['gross_margin']}% - PASS")

    # Edge case: zero cost
    result_zero = generate_pricing_formula(0, 65, 15000, "Agent")
    assert result_zero["platform_fee"] == 0, "Zero cost should produce zero fee"
    print(f"  Zero cost edge case - PASS")

    # --- Test calculate_health_score ---
    # All 5s = 100% = Advanced
    all_high = {f"m4_q{i}": 5 for i in range(1, 11)}
    pct, label, priorities = calculate_health_score(all_high)
    assert pct == 100.0, f"Expected 100%, got {pct}"
    assert label == "Advanced", f"Expected Advanced, got {label}"
    print(f"  All 5s: {pct}% {label} - PASS")

    # All 1s = 20% = Early Stage
    all_low = {f"m4_q{i}": 1 for i in range(1, 11)}
    pct, label, priorities = calculate_health_score(all_low)
    assert pct == 20.0, f"Expected 20%, got {pct}"
    assert label == "Early Stage", f"Expected Early Stage, got {label}"
    assert len(priorities) == 3, f"Expected 3 priorities, got {len(priorities)}"
    print(f"  All 1s: {pct}% {label} - PASS")

    # Mixed scores
    mixed = {
        "m4_q1": 4, "m4_q2": 2, "m4_q3": 5, "m4_q4": 1,
        "m4_q5": 3, "m4_q6": 3, "m4_q7": 2, "m4_q8": 4,
        "m4_q9": 3, "m4_q10": 5,
    }
    pct, label, priorities = calculate_health_score(mixed)
    assert priorities[0] == "m4_q4", f"Expected m4_q4 as top priority, got {priorities[0]}"
    assert "m4_q2" in priorities, f"Expected m4_q2 in priorities"
    assert "m4_q7" in priorities, f"Expected m4_q7 in priorities"
    print(f"  Mixed: {pct}% {label}, priorities={priorities} - PASS")

    # --- Test recommendation lookup ---
    from data.recommendations import get_pricing_recommendation

    rec = get_pricing_recommendation("Copilot", "Revenue Engine", "low")
    assert rec["model_name"] == "Per-seat + Feature Tiers", f"Got {rec['model_name']}"
    print(f"  Copilot+hard+low -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("Agent", "Efficiency Machine", "moderate")
    assert rec["model_name"] == "Outcome-based", f"Got {rec['model_name']}"
    print(f"  Agent+hard+moderate -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("Agent", "Promise Zone", "low")
    assert rec["model_name"] == "Workflow-based (Per Task)", f"Got {rec['model_name']}"
    print(f"  Agent+soft+low -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("AI-enabled Service", "Revenue Engine", "high")
    assert rec["model_name"] == "Outcome-based (Per Deliverable)", f"Got {rec['model_name']}"
    print(f"  Service+hard+high -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("AI-enabled Service", "Danger Zone", "moderate")
    assert rec["model_name"] == "Workflow-based + SLA Tiers", f"Got {rec['model_name']}"
    print(f"  Service+soft+moderate -> {rec['model_name']} - PASS")

    # --- Test comp table ---
    from data.comp_table import get_comps_by_model

    copilot_comps = get_comps_by_model("Copilot")
    assert len(copilot_comps) == 1, f"Expected 1 Copilot comp, got {len(copilot_comps)}"
    assert copilot_comps[0]["name"] == "DeepL"
    print(f"  Copilot comps: {[c['name'] for c in copilot_comps]} - PASS")

    agent_comps = get_comps_by_model("Agent")
    assert len(agent_comps) == 4, f"Expected 4 Agent comps, got {len(agent_comps)}"
    print(f"  Agent comps: {[c['name'] for c in agent_comps]} - PASS")

    service_comps = get_comps_by_model("AI-enabled Service")
    assert len(service_comps) == 4, f"Expected 4 Service comps, got {len(service_comps)}"
    print(f"  Service comps: {[c['name'] for c in service_comps]} - PASS")

    print("\nAll tests passed.")
