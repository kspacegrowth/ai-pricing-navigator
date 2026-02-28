"""Unit Cost Calculator - helps founders figure out their cost per unit."""

import streamlit as st
import plotly.graph_objects as go


# Blended cost per 1K tokens (approximate averages of input + output pricing)
_LLM_PRESETS = {
    "OpenAI (GPT-4o)": 0.01,
    "OpenAI (GPT-4o mini)": 0.0004,
    "Anthropic (Claude Sonnet)": 0.009,
    "Anthropic (Claude Haiku)": 0.002,
    "Open source / self-hosted": 0.001,
    "Other / custom": None,
}


def render_unit_cost_calc():
    """Render the full Unit Cost Calculator page."""
    st.header("Unit Cost Calculator")
    st.markdown(
        "What does it actually cost you to deliver one unit of value? "
        "Let's figure it out."
    )

    # -- Define the unit ----------------------------------------------------
    st.info(
        "A 'unit' is one complete piece of value your AI delivers to a "
        "customer. This depends on your product."
    )
    st.caption(
        "Examples of a unit: one support ticket resolved, one document "
        "generated, one lead qualified, one image created, one code review "
        "completed, one invoice processed, one meeting summarized, "
        "one translation delivered"
    )
    unit_description = st.text_input(
        "Describe your unit of value",
        placeholder="e.g., one support ticket resolved",
        help=(
            "What's the discrete thing your customer would say they "
            "'got' from your product?"
        ),
        key="ucc_unit_desc",
    )

    # -- Section 1: AI / Inference Costs -----------------------------------
    inference_cost = 0.0
    with st.expander("AI / Inference Costs", expanded=True, icon="\U0001f916"):
        st.caption("The compute cost each time your AI does work.")

        calc_method = st.radio(
            "How would you like to calculate this?",
            ["I know my token usage", "I know my monthly API bill"],
            key="ucc_calc_method",
            horizontal=True,
        )

        if calc_method == "I know my token usage":
            provider = st.selectbox(
                "LLM Provider",
                list(_LLM_PRESETS.keys()),
                key="ucc_provider",
            )

            preset = _LLM_PRESETS[provider]
            default_cost = preset if preset is not None else 0.005

            cost_per_1k = st.number_input(
                "Blended cost per 1K tokens ($)",
                min_value=0.0001,
                value=default_cost,
                step=0.001,
                format="%.4f",
                key="ucc_cost_per_1k",
            )
            if preset is not None:
                st.caption(
                    "This is a blended average of input and output token "
                    "costs. Override if you have more precise numbers."
                )

            tokens = st.number_input(
                "Tokens per interaction",
                min_value=1,
                value=2000,
                step=500,
                key="ucc_tokens",
                help=(
                    "Typical ranges: Simple Q&A ~500 tokens, "
                    "Document analysis ~2,000, Complex generation ~5,000, "
                    "Multi-step agent ~8,000+"
                ),
            )

            calls = st.number_input(
                "LLM calls per unit",
                min_value=1,
                value=1,
                step=1,
                key="ucc_calls",
                help=(
                    "How many separate LLM calls does it take to complete "
                    "one unit? Examples: A chatbot resolution might average "
                    "3 back-and-forth calls. A document generator might need "
                    "1 call for drafting + 1 for review = 2. A research "
                    "agent might chain 5-10 calls together."
                ),
            )

            inference_cost = (tokens / 1000) * cost_per_1k * calls
            st.metric("Inference cost per unit", f"${inference_cost:.4f}")

        else:  # monthly bill approach
            monthly_spend = st.number_input(
                "Monthly API/compute spend ($)",
                min_value=0.0,
                value=500.0,
                step=50.0,
                format="%.2f",
                key="ucc_monthly_spend",
                help=(
                    "Your total monthly bill from your LLM provider or GPU "
                    "costs. Check your OpenAI/Anthropic/AWS billing dashboard."
                ),
            )

            units_per_month = st.number_input(
                "Estimated units processed per month",
                min_value=1,
                value=5000,
                step=500,
                key="ucc_units_month",
                help=(
                    "How many units does your product complete in a month? "
                    "Examples: A support bot might resolve 5,000 "
                    "tickets/month. A document tool might process 500 "
                    "documents/month. A lead qualifier might evaluate "
                    "2,000 leads/month."
                ),
            )

            inference_cost = monthly_spend / units_per_month
            st.metric("Inference cost per unit", f"${inference_cost:.4f}")

    # -- Section 2: Human-in-the-Loop Costs --------------------------------
    human_cost = 0.0
    with st.expander("Human-in-the-Loop Costs", expanded=True, icon="\U0001f464"):
        st.caption(
            "If a human reviews, edits, or approves AI output before it "
            "reaches the customer."
        )

        has_human = st.checkbox(
            "My product involves human review",
            value=False,
            key="ucc_has_human",
        )

        if has_human:
            st.text_input(
                "What does the human do?",
                placeholder=(
                    "e.g., reviews AI-drafted legal letter for accuracy"
                ),
                help=(
                    "Examples: QA checks AI output, edits generated content, "
                    "approves automated decisions, handles escalated cases "
                    "the AI can't resolve"
                ),
                key="ucc_human_task",
            )

            review_pct = st.slider(
                "Percentage of units requiring human review",
                min_value=0,
                max_value=100,
                value=20,
                key="ucc_review_pct",
                help=(
                    "Examples: A mature AI support bot might need human "
                    "review on 10% of tickets. An AI legal drafting tool "
                    "might require lawyer review on 80% of outputs. "
                    "An image generation tool might need human QA on 30% "
                    "of outputs."
                ),
            )

            minutes = st.number_input(
                "Average minutes per review",
                min_value=1,
                value=5,
                step=1,
                key="ucc_review_mins",
                help=(
                    "Examples: Quick QA glance = 1-2 min. Editing a draft "
                    "= 5-10 min. Deep review of complex output = 15-30 min."
                ),
            )

            hourly_cost = st.number_input(
                "Loaded hourly cost of reviewer ($)",
                min_value=1.0,
                value=50.0,
                step=5.0,
                format="%.2f",
                key="ucc_hourly_cost",
                help=(
                    "Include salary + benefits + overhead, not just base "
                    "pay. Examples: Junior ops person ~$30/hr loaded. "
                    "Senior engineer ~$80/hr. Lawyer or domain expert "
                    "~$150/hr. Rule of thumb: multiply base salary hourly "
                    "rate by 1.3-1.5 for loaded cost."
                ),
            )

            human_cost = (review_pct / 100) * (minutes / 60) * hourly_cost
            st.metric("Human cost per unit", f"${human_cost:.2f}")
        else:
            st.caption(
                "No human review cost -- fully automated. Nice!"
            )

    # -- Section 3: Infrastructure Overhead --------------------------------
    infra_cost = 0.0
    with st.expander("Infrastructure Overhead", expanded=True, icon="\U0001f3d7\ufe0f"):
        st.caption(
            "Fixed costs you'd incur even if you processed one unit or one "
            "million -- amortized per unit."
        )

        monthly_infra = st.number_input(
            "Monthly infrastructure costs ($)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            format="%.2f",
            key="ucc_monthly_infra",
            help=(
                "Include: hosting (AWS/GCP/etc), databases, monitoring, "
                "vector DBs, file storage, queues, logging services, "
                "CI/CD, etc. Examples: Simple Streamlit app on free tier "
                "= $0. Basic AWS setup with RDS + EC2 = $100-300/month. "
                "Production setup with multiple services = $500-2000/month."
            ),
        )

        monthly_units = st.number_input(
            "Monthly units processed",
            min_value=1,
            value=1000,
            step=100,
            key="ucc_monthly_units",
            help=(
                "Same number from Section 1 if you used the monthly bill "
                "approach. If you're pre-launch, estimate your first 3 "
                "months of expected volume."
            ),
        )

        infra_cost = monthly_infra / monthly_units
        st.metric("Infrastructure cost per unit", f"${infra_cost:.4f}")

    # -- Total Cost Summary ------------------------------------------------
    total_cost = inference_cost + human_cost + infra_cost

    st.divider()
    st.subheader("Your Cost Per Unit")

    c1, c2, c3 = st.columns(3)
    c1.metric("AI/Inference", f"${inference_cost:.4f}")
    c2.metric("Human Review", f"${human_cost:.4f}")
    c3.metric("Infrastructure", f"${infra_cost:.4f}")

    st.metric(
        "Total Cost Per Unit",
        f"${total_cost:.4f}",
        help="This is your fully-loaded cost to deliver one unit of value.",
    )

    # Cost breakdown bar chart
    if total_cost > 0:
        pcts = [
            inference_cost / total_cost * 100,
            human_cost / total_cost * 100,
            infra_cost / total_cost * 100,
        ]
        fig = go.Figure()
        colors = ["#0EA5E9", "#8B5CF6", "#64748B"]
        names = ["AI/Inference", "Human Review", "Infrastructure"]
        for name, pct, color in zip(names, pcts, colors):
            fig.add_trace(
                go.Bar(
                    y=["Cost Breakdown"],
                    x=[pct],
                    orientation="h",
                    name=name,
                    marker_color=color,
                    text=f"{pct:.0f}%" if pct >= 5 else "",
                    textposition="inside",
                    textfont=dict(size=11, color="#fff"),
                    hovertemplate=f"{name}: {pct:.1f}%<extra></extra>",
                )
            )
        fig.update_layout(
            barmode="stack",
            height=80,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(range=[0, 100], visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            legend=dict(orientation="h", yanchor="top", y=-0.3),
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    unit_label = unit_description or "unit"
    st.caption(f"Your unit: {unit_label}")

    if total_cost > 0:
        min_price = total_cost / (1 - 0.65)
        st.info(
            f"At a 65% gross margin target, you'd need to charge at least "
            f"${min_price:.2f} per {unit_label}."
        )

    # Use in Step 3 button
    def _use_in_step3():
        st.session_state.calculated_unit_cost = total_cost
        st.session_state.nav_module = "3. Pricing Model"

    st.button(
        "Use this in Step 3 \u2192",
        type="primary",
        on_click=_use_in_step3,
    )

    if st.session_state.get("calculated_unit_cost") is not None:
        st.success(
            "Cost per unit saved! Head to Step 3 to get your pricing "
            "recommendation."
        )
