"""Scoring and calculation helpers for all modules."""

import sys
import os

# Allow imports from project root when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.questions import QUESTIONS_BY_ID, MODULE_1_QUESTIONS, MODULE_2_QUESTIONS


# ---------------------------------------------------------------------------
# Module 1 - Business Model Classifier
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Module 2 - Value Framework Mapper
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Module 3 - Pricing Formula Generator (4 variants)
# ---------------------------------------------------------------------------

def _get_monthly_units(deal_size):
    """Map deal size to estimated monthly units."""
    if deal_size <= 5000:
        return 50
    elif deal_size <= 25000:
        return 200
    elif deal_size <= 100000:
        return 500
    else:
        return 1000


def _get_seats(customer_segment):
    """Map customer segment to estimated seat count."""
    return {"smb": 5, "mid_market": 25, "enterprise": 100}.get(customer_segment, 25)


def _empty_result():
    return {
        "model_name": "",
        "platform_fee_annual": 0,
        "platform_fee_monthly": 0,
        "included_units": 0,
        "overage_rate": 0,
        "effective_price_per_unit": 0,
        "gross_margin": 0,
        "explanation": "",
    }


def _hybrid_formula(cost, price, margin, deal_size):
    monthly_units = _get_monthly_units(deal_size)
    fee_monthly = round(cost * monthly_units * 2, 2)
    fee_annual = round(fee_monthly * 12, 2)
    included = max(1, int(fee_annual / (price * 1.5)))
    overage = round(price * 1.2, 2)

    annual_cost = cost * included
    gm = round((fee_annual - annual_cost) / fee_annual * 100, 1) if fee_annual > 0 else 0

    return {
        "model_name": "Hybrid (Base + Usage)",
        "platform_fee_annual": fee_annual,
        "platform_fee_monthly": fee_monthly,
        "included_units": included,
        "overage_rate": overage,
        "effective_price_per_unit": round(price, 2),
        "gross_margin": gm,
        "explanation": (
            f"Charge ${fee_monthly:,.0f}/mo platform fee covering "
            f"{included:,} included units/yr. "
            f"Additional units at ${overage:,.2f} each."
        ),
    }


def _outcome_formula(cost, price, margin, deal_size):
    min_commit = round(deal_size * 0.7, 2)
    estimated_outcomes = max(1, int(min_commit / price))
    fee_monthly = round(min_commit / 12, 2)

    return {
        "model_name": "Outcome-based",
        "platform_fee_annual": min_commit,
        "platform_fee_monthly": fee_monthly,
        "included_units": estimated_outcomes,
        "overage_rate": round(price, 2),
        "effective_price_per_unit": round(price, 2),
        "gross_margin": round(margin, 1),
        "explanation": (
            f"${price:,.2f} per outcome with ${min_commit:,.0f}/yr minimum "
            f"commitment (~{estimated_outcomes:,} outcomes). "
            f"Same rate for additional outcomes."
        ),
    }


def _workflow_formula(cost, price, margin, deal_size):
    monthly_tasks = _get_monthly_units(deal_size)  # reuse same mapping
    fee_monthly = round(monthly_tasks * price, 2)
    fee_annual = round(fee_monthly * 12, 2)
    annual_tasks = monthly_tasks * 12
    discounted = round(price * 0.85, 2)

    return {
        "model_name": "Workflow-based (Per Task)",
        "platform_fee_annual": fee_annual,
        "platform_fee_monthly": fee_monthly,
        "included_units": annual_tasks,
        "overage_rate": discounted,
        "effective_price_per_unit": round(price, 2),
        "gross_margin": round(margin, 1),
        "explanation": (
            f"${price:,.2f} per task \u00d7 {monthly_tasks:,} tasks/mo = "
            f"${fee_monthly:,.0f}/mo. "
            f"15% volume discount at 2\u00d7 volume (${discounted:,.2f}/task)."
        ),
    }


def _per_seat_formula(cost, price, margin, deal_size, segment):
    seats = _get_seats(segment)
    monthly_per_seat = round(deal_size / 12 / seats, 2)
    fee_monthly = round(monthly_per_seat * seats, 2)
    fee_annual = round(fee_monthly * 12, 2)
    extra_seat = round(monthly_per_seat * 1.5, 2)

    # Estimate cost per seat
    monthly_units = _get_monthly_units(deal_size)
    units_per_seat = monthly_units / seats
    cost_per_seat = cost * units_per_seat
    gm = round((monthly_per_seat - cost_per_seat) / monthly_per_seat * 100, 1) if monthly_per_seat > 0 else 0

    return {
        "model_name": "Per-seat + Feature Tiers",
        "platform_fee_annual": fee_annual,
        "platform_fee_monthly": fee_monthly,
        "included_units": seats,
        "overage_rate": extra_seat,
        "effective_price_per_unit": monthly_per_seat,
        "gross_margin": gm,
        "explanation": (
            f"${monthly_per_seat:,.0f}/seat/month \u00d7 {seats} seats = "
            f"${fee_monthly:,.0f}/mo. "
            f"Additional seats at ${extra_seat:,.0f}/mo each."
        ),
    }


def generate_pricing_formula(cost_per_unit, target_margin, deal_size,
                             formula_type, customer_segment="mid_market"):
    """Generate pricing formula using one of 4 BVP-derived variants.

    Args:
        cost_per_unit: float, cost to deliver one unit of value
        target_margin: float, target gross margin percentage (40-85)
        deal_size: float, target annual deal size in dollars
        formula_type: "hybrid", "outcome", "workflow", or "per_seat"
        customer_segment: "smb", "mid_market", or "enterprise"

    Returns:
        dict with model_name, platform_fee_annual, platform_fee_monthly,
        included_units, overage_rate, effective_price_per_unit,
        gross_margin, explanation.
    """
    if cost_per_unit <= 0 or target_margin >= 100:
        return _empty_result()

    price = cost_per_unit / (1 - target_margin / 100)

    if formula_type == "per_seat":
        return _per_seat_formula(cost_per_unit, price, target_margin, deal_size, customer_segment)
    elif formula_type == "outcome":
        return _outcome_formula(cost_per_unit, price, target_margin, deal_size)
    elif formula_type == "workflow":
        return _workflow_formula(cost_per_unit, price, target_margin, deal_size)
    else:  # hybrid (default)
        return _hybrid_formula(cost_per_unit, price, target_margin, deal_size)


# ---------------------------------------------------------------------------
# Module 4 - Health Check Scorer
# ---------------------------------------------------------------------------

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

    # --- classify_business_model ---
    copilot_answers = {
        "m1_q1": "yes", "m1_q2": "no", "m1_q3": "partial",
        "m1_q4": "chat", "m1_q5": "advisor",
    }
    model, conf = classify_business_model(copilot_answers)
    assert model == "Copilot", f"Expected Copilot, got {model}"
    assert conf > 50
    print(f"  Copilot: {model} ({conf}%) - PASS")

    agent_answers = {
        "m1_q1": "no", "m1_q2": "yes", "m1_q3": "no",
        "m1_q4": "automation", "m1_q5": "executor",
    }
    model, conf = classify_business_model(agent_answers)
    assert model == "Agent"
    print(f"  Agent: {model} ({conf}%) - PASS")

    service_answers = {
        "m1_q1": "no", "m1_q2": "partial", "m1_q3": "yes",
        "m1_q4": "output", "m1_q5": "service_provider",
    }
    model, conf = classify_business_model(service_answers)
    assert model == "AI-enabled Service"
    print(f"  Service: {model} ({conf}%) - PASS")

    # --- calculate_value_position ---
    x, y, quad = calculate_value_position({
        "m2_q1": "revenue", "m2_q2": "yes", "m2_q3": "lose_revenue",
        "m2_q4": "dashboard", "m2_q5": "no",
    })
    assert quad == "Revenue Engine" and x > 0 and y > 0
    print(f"  Revenue Engine: x={x}, y={y} - PASS")

    x, y, quad = calculate_value_position({
        "m2_q1": "cost_reduction", "m2_q2": "yes", "m2_q3": "slower",
        "m2_q4": "dashboard", "m2_q5": "yes",
    })
    assert quad == "Efficiency Machine" and x < 0 and y > 0
    print(f"  Efficiency Machine: x={x}, y={y} - PASS")

    x, y, quad = calculate_value_position({
        "m2_q1": "time_savings", "m2_q2": "no", "m2_q3": "no_pain",
        "m2_q4": "qualitative", "m2_q5": "partial",
    })
    assert quad == "Danger Zone" and y < 0
    print(f"  Danger Zone: x={x}, y={y} - PASS")

    # --- generate_pricing_formula: HYBRID ---
    r = generate_pricing_formula(1.0, 65, 62500, "hybrid")
    assert r["platform_fee_annual"] > 0
    assert r["included_units"] >= 1
    assert 0 < r["gross_margin"] < 100
    print(f"  Hybrid: fee=${r['platform_fee_annual']:,.0f}/yr, "
          f"{r['included_units']} units, margin={r['gross_margin']}% - PASS")

    # Acceptance: $1 cost, 65% margin, ~$25K deal -> fee ~$4,800-$14,400/yr
    r2 = generate_pricing_formula(1.0, 65, 25000, "hybrid")
    assert 2000 <= r2["platform_fee_annual"] <= 20000, \
        f"Fee ${r2['platform_fee_annual']} outside expected range"
    print(f"  Hybrid $25K deal: fee=${r2['platform_fee_annual']:,.0f}/yr - PASS")

    # --- generate_pricing_formula: OUTCOME ---
    r = generate_pricing_formula(1.0, 65, 62500, "outcome")
    assert r["model_name"] == "Outcome-based"
    assert r["platform_fee_annual"] > 0
    assert r["gross_margin"] == 65.0
    print(f"  Outcome: commit=${r['platform_fee_annual']:,.0f}/yr, "
          f"{r['included_units']} outcomes - PASS")

    # --- generate_pricing_formula: WORKFLOW ---
    r = generate_pricing_formula(1.0, 65, 15000, "workflow")
    assert r["model_name"] == "Workflow-based (Per Task)"
    assert r["overage_rate"] < r["effective_price_per_unit"]  # discount
    print(f"  Workflow: ${r['effective_price_per_unit']:.2f}/task, "
          f"discount=${r['overage_rate']:.2f} - PASS")

    # --- generate_pricing_formula: PER_SEAT ---
    r = generate_pricing_formula(1.0, 65, 62500, "per_seat", "mid_market")
    assert r["model_name"] == "Per-seat + Feature Tiers"
    assert r["included_units"] == 25  # mid_market seats
    assert r["gross_margin"] > 0
    print(f"  Per-seat: ${r['effective_price_per_unit']:,.0f}/seat/mo, "
          f"{r['included_units']} seats, margin={r['gross_margin']}% - PASS")

    # --- Edge: zero cost ---
    r = generate_pricing_formula(0, 65, 15000, "hybrid")
    assert r["platform_fee_annual"] == 0
    print(f"  Zero cost edge case - PASS")

    # --- calculate_health_score ---
    pct, label, _ = calculate_health_score({f"m4_q{i}": 5 for i in range(1, 11)})
    assert pct == 100.0 and label == "Advanced"
    print(f"  All 5s: {pct}% {label} - PASS")

    pct, label, _ = calculate_health_score({f"m4_q{i}": 1 for i in range(1, 11)})
    assert pct == 20.0 and label == "Early Stage"
    print(f"  All 1s: {pct}% {label} - PASS")

    mixed = {
        "m4_q1": 4, "m4_q2": 2, "m4_q3": 5, "m4_q4": 1,
        "m4_q5": 3, "m4_q6": 3, "m4_q7": 2, "m4_q8": 4,
        "m4_q9": 3, "m4_q10": 5,
    }
    pct, label, pri = calculate_health_score(mixed)
    assert pri[0] == "m4_q4" and "m4_q2" in pri and "m4_q7" in pri
    print(f"  Mixed: {pct}% {label}, priorities={pri} - PASS")

    # --- Recommendation lookup ---
    from data.recommendations import get_pricing_recommendation

    rec = get_pricing_recommendation("Copilot", "Revenue Engine", "low")
    assert rec["model_name"] == "Per-seat + Feature Tiers"
    print(f"  Copilot+hard+low -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("Agent", "Efficiency Machine", "moderate")
    assert rec["model_name"] == "Outcome-based"
    print(f"  Agent+hard+mod -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("Agent", "Promise Zone", "low")
    assert rec["model_name"] == "Workflow-based (Per Task)"
    print(f"  Agent+soft+low -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("AI-enabled Service", "Revenue Engine", "high")
    assert rec["model_name"] == "Outcome-based (Per Deliverable)"
    print(f"  Service+hard+high -> {rec['model_name']} - PASS")

    rec = get_pricing_recommendation("AI-enabled Service", "Danger Zone", "moderate")
    assert rec["model_name"] == "Workflow-based + SLA Tiers"
    print(f"  Service+soft+mod -> {rec['model_name']} - PASS")

    # --- Comp table ---
    from data.comp_table import get_comps_by_model

    assert len(get_comps_by_model("Copilot")) == 1
    assert len(get_comps_by_model("Agent")) == 4
    assert len(get_comps_by_model("AI-enabled Service")) == 4
    print(f"  Comp table filters - PASS")

    print("\nAll tests passed.")
