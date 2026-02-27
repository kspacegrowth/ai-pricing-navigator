"""Module 1 - Business Model Classifier."""

import streamlit as st
import pandas as pd

from data.questions import MODULE_1_QUESTIONS
from data.recommendations import BUSINESS_MODELS
from data.comp_table import get_comps_by_model
from utils.scoring import classify_business_model


_MODEL_ICONS = {
    "Copilot": "\U0001f9d1\u200d\u2708\ufe0f",
    "Agent": "\U0001f916",
    "AI-enabled Service": "\U0001f3e2",
}


def _collect_answers():
    """Read current radio selections and map labels back to option values."""
    answers = {}
    for q in MODULE_1_QUESTIONS:
        selected_label = st.session_state.get(f"radio_{q['id']}")
        if selected_label is None:
            continue
        for opt in q["options"]:
            if opt["label"] == selected_label:
                answers[q["id"]] = opt["value"]
                break
    return answers


def render_classifier():
    st.header("What type of AI business are you building?")
    st.markdown(
        "Your AI business model determines which pricing structures make sense. "
        "Answer these questions to classify your product."
    )

    # ---- Questions --------------------------------------------------------
    for q in MODULE_1_QUESTIONS:
        selected = st.radio(
            q["text"],
            options=[opt["label"] for opt in q["options"]],
            key=f"radio_{q['id']}",
            index=None,
            help=q["help_text"],
        )
        # Show example for the selected option
        if selected and q.get("options"):
            for opt in q["options"]:
                if opt["label"] == selected and opt.get("example"):
                    st.caption(f"*{opt['example']}*")
                    break

    # ---- Classify button --------------------------------------------------
    if st.button("Classify My Business \u2192", type="primary"):
        answers = _collect_answers()
        if not answers:
            st.warning("Please answer at least one question before classifying.")
        else:
            model, confidence = classify_business_model(answers)
            st.session_state.classifier_answers = answers
            st.session_state.business_model = model
            st.session_state.model_confidence = confidence

    # ---- Results (persist after classification) ---------------------------
    if st.session_state.business_model:
        _show_results()


def _show_results():
    model = st.session_state.business_model
    confidence = st.session_state.model_confidence
    model_data = BUSINESS_MODELS[model]
    icon = _MODEL_ICONS.get(model, "")

    st.divider()

    with st.container(border=True):
        st.subheader(f"{icon} {model} - {confidence}% confidence")
        st.markdown(model_data["description"])
        st.caption(model_data["pricing_implications"])
        with st.expander("See example companies"):
            for ex in model_data["examples"]:
                st.markdown(f"- {ex}")

    st.subheader("Companies with similar models")
    comps = get_comps_by_model(model)
    if comps:
        df = pd.DataFrame(comps).drop(columns=["model_type"])
        df.columns = ["Company", "Pricing Model", "Detail", "Value Driver"]
        st.dataframe(df, hide_index=True, use_container_width=True)
