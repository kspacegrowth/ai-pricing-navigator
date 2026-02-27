"""Module 4 \u2014 Pricing Strategy Health Check."""

import streamlit as st

from data.questions import MODULE_4_QUESTIONS
from data.recommendations import HEALTH_CHECK_ACTIONS
from utils.scoring import calculate_health_score
from utils.charts import create_radar_chart

_RADAR_LABELS = [
    "AI Economics", "Model Fit", "Price Clarity", "Cost Management",
    "Free\u2192Paid", "AI Metrics", "Unit Economics", "Pricing Moat",
    "Sustainability", "Scalability",
]

_SCORE_BADGES = {
    "Early Stage": "\U0001f534 Early Stage \u2014 Focus on the fundamentals before scaling",
    "Developing": "\U0001f7e1 Developing \u2014 Good foundation, key gaps to address",
    "Strong": "\U0001f7e2 Strong \u2014 Well-positioned, fine-tune the details",
    "Advanced": "\U0001f31f Advanced \u2014 Pricing is a competitive advantage",
}


def render_health_check():
    st.header("Pricing Strategy Health Check")
    st.markdown(
        "Rate your confidence on each of these critical pricing dimensions. "
        "Be honest \u2014 this tool is most useful when you are."
    )
    st.caption("(1 = not at all confident, 5 = fully confident)")

    # ---- Questions --------------------------------------------------------
    for q in MODULE_4_QUESTIONS:
        st.slider(
            q["text"],
            min_value=q["min"],
            max_value=q["max"],
            value=q["default"],
            key=f"slider_{q['id']}",
        )

    # ---- Score button -----------------------------------------------------
    if st.button("Score My Pricing Readiness \u2192", type="primary"):
        scores = {}
        for q in MODULE_4_QUESTIONS:
            scores[q["id"]] = st.session_state.get(f"slider_{q['id']}", 3)

        pct, label, priorities = calculate_health_score(scores)
        st.session_state.health_scores = scores
        st.session_state.overall_score = pct
        st.session_state.health_label = label
        st.session_state.priority_areas = priorities

    # ---- Results ----------------------------------------------------------
    if st.session_state.health_scores:
        _show_results()


def _show_results():
    scores = st.session_state.health_scores
    pct = st.session_state.overall_score
    label = st.session_state.get("health_label", "Developing")
    priorities = st.session_state.priority_areas

    st.divider()

    # Score values in question order for the radar chart
    score_values = [scores.get(f"m4_q{i}", 3) for i in range(1, 11)]

    # Two-column layout: radar chart + score badge
    col_chart, col_score = st.columns([2, 1])

    with col_chart:
        fig = create_radar_chart(score_values, _RADAR_LABELS)
        st.plotly_chart(fig, use_container_width=True)

    with col_score:
        st.metric("Overall Score", f"{pct:.0f}%")
        badge = _SCORE_BADGES.get(label, label)
        st.markdown(f"### {badge}")

    # ---- Priority actions -------------------------------------------------
    all_high = all(v >= 4 for v in scores.values())

    if all_high:
        st.success(
            "No critical gaps identified. Consider stress-testing your "
            "pricing with real customer conversations."
        )
    else:
        st.subheader("\U0001f3af Your Top 3 Priority Areas")
        for q_id in priorities:
            q_text = next(
                (q["text"] for q in MODULE_4_QUESTIONS if q["id"] == q_id), ""
            )
            score = scores.get(q_id, 0)
            stars = "\u2b50" * score
            action = HEALTH_CHECK_ACTIONS.get(q_id, "")

            with st.container(border=True):
                st.markdown(f"**{q_text}**")
                st.markdown(f"Your score: {stars} ({score}/5)")
                st.info(action)
