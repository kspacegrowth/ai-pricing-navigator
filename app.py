import streamlit as st

from modules.classifier import render_classifier
from modules.value_mapper import render_value_mapper
from modules.pricing_rec import render_pricing_rec
from modules.unit_economics import render_unit_economics

st.set_page_config(
    page_title="AI Pricing Navigator",
    page_icon="\U0001f4b0",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_defaults = {
    "classifier_answers": {},
    "business_model": "",
    "model_confidence": 0.0,
    "value_answers": {},
    "x_score": 0.0,
    "y_score": 0.0,
    "quadrant": "",
    "pricing_answers": {},
    "recommended_model": "",
    "pricing_recommendation": {},
    "pricing_formula": {},
    "health_scores": {},
    "overall_score": 0.0,
    "priority_areas": [],
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------------------------------------------------------------------------
# Sidebar — navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("\U0001f4b0 AI Pricing Navigator")
    st.caption("Design your AI pricing strategy in minutes")
    st.divider()

    module = st.radio(
        "Navigate",
        [
            "1. Business Model",
            "2. Value Framework",
            "3. Pricing Recommendation",
            "4. Health Check",
        ],
        label_visibility="collapsed",
    )

    st.divider()

# Sidebar — unit economics calculator
render_unit_economics()

# Sidebar — footer
with st.sidebar:
    st.divider()
    st.markdown("[Built by K-Space](#)")
    st.caption(
        "Framework based on Bessemer Venture Partners\u2019 "
        "AI Pricing Playbook (2026)"
    )

# ---------------------------------------------------------------------------
# Module routing
# ---------------------------------------------------------------------------
if module == "1. Business Model":
    render_classifier()
elif module == "2. Value Framework":
    render_value_mapper()
elif module == "3. Pricing Recommendation":
    render_pricing_rec()
elif module == "4. Health Check":
    st.info("\U0001f6a7 Health Check Scorecard \u2014 coming in Phase 4")
