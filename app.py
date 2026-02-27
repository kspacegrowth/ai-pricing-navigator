import streamlit as st

from modules.classifier import render_classifier
from modules.value_mapper import render_value_mapper
from modules.pricing_rec import render_pricing_rec
from modules.health_check import render_health_check
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
    "health_label": "",
    "overall_score": 0.0,
    "priority_areas": [],
    "confirm_reset": False,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

_NAV_OPTIONS = [
    "\U0001f3e0 Welcome",
    "1. Classify Business",
    "2. Map Value",
    "3. Pricing Model",
    "4. Health Check",
]

# ---------------------------------------------------------------------------
# Sidebar - navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("\U0001f4b0 AI Pricing Navigator")
    st.caption("Design your AI pricing strategy in minutes")
    st.divider()

    module = st.radio(
        "Navigate",
        _NAV_OPTIONS,
        key="nav_module",
        label_visibility="collapsed",
    )

    st.divider()

    # Reset button
    if st.button("\U0001f504 Start Over"):
        st.session_state.confirm_reset = True

    if st.session_state.confirm_reset:
        st.warning("This will clear all your answers.")
        c1, c2 = st.columns(2)
        if c1.button("Yes, reset"):
            keys = [k for k in st.session_state.keys()]
            for k in keys:
                del st.session_state[k]
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_reset = False
            st.rerun()

    st.divider()

# Sidebar - unit economics calculator
render_unit_economics()

# Sidebar - about + footer
with st.sidebar:
    st.divider()

    with st.expander("About this tool"):
        st.markdown(
            "AI Pricing Navigator helps AI founders design their pricing "
            "strategy using frameworks from Bessemer Venture Partners\u2019 "
            "AI Pricing Playbook. Answer questions about your business and "
            "get a tailored pricing model recommendation."
        )
        st.markdown("This tool is free and does not store any data.")
        st.markdown(
            "[Read the full BVP playbook \u2192]"
            "(https://www.bvp.com/atlas/the-ai-pricing-and-monetization-playbook)"
        )

    st.markdown("[Built by K-Space](#)")
    st.caption(
        "Framework based on Bessemer Venture Partners\u2019 "
        "AI Pricing Playbook (2026)"
    )


# ---------------------------------------------------------------------------
# Welcome page
# ---------------------------------------------------------------------------
def _render_welcome():
    st.title("AI Pricing Navigator")
    st.markdown("### Design your AI pricing strategy in minutes - not months.")
    st.markdown(
        "This tool walks you through a 3-step process to help you choose the "
        "right pricing model for your AI product. You\u2019ll classify your "
        "business, map your value, and get a concrete pricing recommendation "
        "with real numbers."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("\U0001f50d **Step 1: Classify**")
            st.caption("What type of AI business are you?")
    with c2:
        with st.container(border=True):
            st.markdown("\U0001f4ca **Step 2: Map Value**")
            st.caption("Where\u2019s your pricing power?")
    with c3:
        with st.container(border=True):
            st.markdown("\U0001f4b0 **Step 3: Get Your Model**")
            st.caption("Concrete pricing formula")

    st.markdown(
        "**Plus:** Take the Pricing Health Check - a standalone self-assessment "
        "to find blind spots in your pricing strategy."
    )

    def _go_to_classify():
        st.session_state.nav_module = "1. Classify Business"

    st.button("Get Started \u2192", type="primary", on_click=_go_to_classify)


# ---------------------------------------------------------------------------
# Module routing
# ---------------------------------------------------------------------------
if module == "\U0001f3e0 Welcome":
    _render_welcome()
elif module == "1. Classify Business":
    render_classifier()
elif module == "2. Map Value":
    render_value_mapper()
elif module == "3. Pricing Model":
    render_pricing_rec()
elif module == "4. Health Check":
    render_health_check()

# ---------------------------------------------------------------------------
# Main area footer
# ---------------------------------------------------------------------------
st.divider()
st.caption("Built by K-Space | AI-powered business development tools")
st.caption(
    "Framework based on Bessemer Venture Partners\u2019 "
    "AI Pricing Playbook (2026)"
)
