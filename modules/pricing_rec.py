"""Module 3 \u2014 Pricing Model Recommender."""

import streamlit as st
import pandas as pd

from data.questions import MODULE_3_QUESTIONS
from data.recommendations import get_pricing_recommendation
from data.comp_table import get_comps_by_model
from utils.scoring import generate_pricing_formula


# BVP-derived principles per model type
_BVP_PRINCIPLES = {
    "Copilot": [
        "**Price for adoption:** Copilots succeed when every user activates. "
        "Keep per-seat prices accessible enough for org-wide rollout.",
        "**Feature-gate, don\u2019t usage-gate:** Copilot value is continuous. "
        "Users shouldn\u2019t worry about running out of interactions.",
        "**Track seats \u00d7 engagement:** Revenue scales with both headcount "
        "and daily active usage.",
    ],
    "Agent": [
        "**Charge for outcomes, not effort:** Agents replace work. Price the "
        "result, not the compute behind it.",
        "**Cap your downside:** Use minimum commitments to protect against "
        "usage variance while keeping the outcome promise.",
        "**Build trust with transparency:** Show customers what the agent did "
        "and how much it saved \u2014 this drives upsell.",
    ],
    "AI-enabled Service": [
        "**Anchor to what you replace:** Your pricing ceiling is the cost of "
        "the human service you displace, minus a discount for switching risk.",
        "**Per-deliverable makes ROI obvious:** When customers pay per output, "
        "they can directly compare cost vs. the alternative.",
        "**Add SLA tiers for premium capture:** Speed, quality guarantees, and "
        "dedicated support justify 2\u20133x pricing for enterprise.",
    ],
}

_MODEL_ICONS = {
    "Per-seat + Feature Tiers": "\U0001f4ba",
    "Hybrid (Base + Usage Tiers)": "\U0001f504",
    "Hybrid (Base + Outcome Credits)": "\U0001f504",
    "Outcome-based": "\U0001f3af",
    "Outcome-based (Per Deliverable)": "\U0001f3af",
    "Workflow-based (Per Task)": "\u2699\ufe0f",
    "Workflow-based + SLA Tiers": "\u2699\ufe0f",
}


def _collect_answers():
    """Read current widget selections for Module 3 questions."""
    answers = {}
    for q in MODULE_3_QUESTIONS:
        if q["type"] in ("number", "slider"):
            val = st.session_state.get(f"input_{q['id']}")
            if val is not None:
                answers[q["id"]] = val
        elif q["type"] == "radio" and q["options"]:
            selected_label = st.session_state.get(f"radio_{q['id']}")
            if selected_label is not None:
                for opt in q["options"]:
                    if opt["label"] == selected_label:
                        answers[q["id"]] = opt["value"]
                        break
    return answers


def render_pricing_rec():
    st.header("Your Pricing Model Recommendation")

    business_model = st.session_state.business_model
    quadrant = st.session_state.quadrant

    # Gate on Modules 1 & 2
    if not business_model or not quadrant:
        st.warning(
            "Complete Steps 1 and 2 first for a personalized recommendation."
        )
        return

    st.info(
        f"Based on your inputs: **{business_model}** in the "
        f"**{quadrant}** quadrant"
    )

    # ---- Questions --------------------------------------------------------
    for q in MODULE_3_QUESTIONS:
        if q["type"] == "number":
            st.number_input(
                q["text"],
                min_value=0.01,
                value=1.00,
                step=0.50,
                format="%.2f",
                key=f"input_{q['id']}",
                help=q["help_text"],
            )
        elif q["type"] == "slider":
            st.slider(
                q["text"],
                min_value=q["min"],
                max_value=q["max"],
                value=q["default"],
                key=f"input_{q['id']}",
                help=q["help_text"],
            )
        elif q["type"] == "radio" and q["options"]:
            st.radio(
                q["text"],
                options=[opt["label"] for opt in q["options"]],
                key=f"radio_{q['id']}",
                index=None,
                help=q["help_text"],
            )

    # ---- Generate button --------------------------------------------------
    if st.button("Generate My Pricing Model \u2192", type="primary"):
        answers = _collect_answers()

        cost = answers.get("m3_q1", 1.0)
        customer_segment = answers.get("m3_q2", "mid_market")
        deal_size = answers.get("m3_q3", 15000)
        target_margin = answers.get("m3_q4", 65)
        cost_variance = answers.get("m3_q5", "moderate")

        rec = get_pricing_recommendation(business_model, quadrant, cost_variance)
        formula = generate_pricing_formula(
            cost_per_unit=cost,
            target_margin=target_margin,
            deal_size=deal_size,
            formula_type=rec["formula_type"],
            customer_segment=customer_segment,
        )

        st.session_state.pricing_answers = answers
        st.session_state.recommended_model = rec["model_name"]
        st.session_state.pricing_recommendation = rec
        st.session_state.pricing_formula = formula

    # ---- Results ----------------------------------------------------------
    if st.session_state.recommended_model:
        _show_results()


def _show_results():
    rec = st.session_state.pricing_recommendation
    formula = st.session_state.pricing_formula
    business_model = st.session_state.business_model
    model_name = rec.get("model_name", "")
    icon = _MODEL_ICONS.get(model_name, "\U0001f4ca")

    st.divider()

    # -- Recommendation card ------------------------------------------------
    with st.container(border=True):
        st.subheader(f"{icon} {model_name}")
        st.markdown(f"**Why this model?** {rec.get('rationale', '')}")

    # -- Pricing formula card -----------------------------------------------
    with st.container(border=True):
        st.subheader("Pricing Formula")

        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Platform Fee",
            f"${formula.get('platform_fee_annual', 0):,.0f}/yr",
            f"${formula.get('platform_fee_monthly', 0):,.0f}/mo",
        )
        c2.metric("Included Units/yr", f"{formula.get('included_units', 0):,}")
        c3.metric(
            "Overage Rate",
            f"${formula.get('overage_rate', 0):,.2f}/unit",
        )

        c4, c5 = st.columns(2)
        c4.metric(
            "Effective Price/Unit",
            f"${formula.get('effective_price_per_unit', 0):,.2f}",
        )

        margin = formula.get("gross_margin", 0)
        delta = margin - 55
        c5.metric(
            "Gross Margin",
            f"{margin:.0f}%",
            delta=f"{delta:+.0f}% vs AI avg",
        )

        if formula.get("explanation"):
            st.caption(formula["explanation"])

        st.caption(
            "*These are starting points. Use the friction test: "
            "raise prices until customers pause.*"
        )

    # -- Comp table ---------------------------------------------------------
    with st.container(border=True):
        st.subheader("How others do it")
        comps = get_comps_by_model(business_model)[:3]
        if comps:
            df = pd.DataFrame(comps).drop(columns=["model_type"])
            df.columns = ["Company", "Pricing Model", "Detail", "Value Driver"]
            st.dataframe(df, hide_index=True, use_container_width=True)

    # -- BVP principles -----------------------------------------------------
    principles = _BVP_PRINCIPLES.get(business_model, [])
    if principles:
        lines = "\n".join(f"- {p}" for p in principles)
        st.info(f"**BVP Pricing Principles for {business_model}s:**\n\n{lines}")
