"""Module 2 — Value Framework Mapper."""

import streamlit as st

from data.questions import MODULE_2_QUESTIONS
from data.recommendations import QUADRANTS
from utils.scoring import calculate_value_position
from utils.charts import create_value_framework_chart


def _collect_answers():
    """Read current radio selections and map labels back to option values."""
    answers = {}
    for q in MODULE_2_QUESTIONS:
        selected_label = st.session_state.get(f"radio_{q['id']}")
        if selected_label is None:
            continue
        for opt in q["options"]:
            if opt["label"] == selected_label:
                answers[q["id"]] = opt["value"]
                break
    return answers


def render_value_mapper():
    st.header("Where does your product sit on the AI Value Framework?")
    st.markdown(
        "This 2\u00d72 framework maps your pricing power and renewal risk. "
        "Products with hard ROI and clear revenue impact command the "
        "strongest pricing."
    )

    if not st.session_state.business_model:
        st.warning(
            "Complete Step 1 first to get the most accurate results."
        )

    # ---- Questions --------------------------------------------------------
    for q in MODULE_2_QUESTIONS:
        st.radio(
            q["text"],
            options=[opt["label"] for opt in q["options"]],
            key=f"radio_{q['id']}",
            index=None,
            help=q["help_text"],
        )

    # ---- Map button -------------------------------------------------------
    if st.button("Map My Position \u2192", type="primary"):
        answers = _collect_answers()
        if not answers:
            st.warning("Please answer at least one question.")
        else:
            x, y, quadrant = calculate_value_position(answers)
            st.session_state.value_answers = answers
            st.session_state.x_score = x
            st.session_state.y_score = y
            st.session_state.quadrant = quadrant

    # ---- Results ----------------------------------------------------------
    if st.session_state.quadrant:
        _show_results()


def _show_results():
    x = st.session_state.x_score
    y = st.session_state.y_score
    quadrant = st.session_state.quadrant
    quad_data = QUADRANTS[quadrant]

    st.divider()

    # Plotly chart
    fig = create_value_framework_chart(x, y)
    st.plotly_chart(fig, use_container_width=True)

    # Quadrant interpretation
    with st.container(border=True):
        st.subheader(quad_data["label"])
        st.markdown(quad_data["description"])
        st.info(f"**Pricing implication:** {quad_data['pricing_implication']}")

    # Renewal risk warning for soft-ROI quadrants
    if y <= 0:
        st.warning(
            "\u26a0\ufe0f Products in this quadrant face the highest renewal risk as "
            "2025-era AI pilots hit their first renewal cycles. Consider: Can you "
            "move toward harder ROI by closing the loop on outcomes?"
        )
