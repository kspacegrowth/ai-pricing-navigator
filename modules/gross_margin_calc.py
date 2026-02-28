"""Gross Margin Calculator - quick scratch pad for margin math."""

import streamlit as st
import plotly.graph_objects as go


def render_gross_margin_calc():
    """Render the Gross Margin Calculator on the Tools page."""
    st.header("Gross Margin Calculator")
    st.markdown(
        "Quick scratch pad to test your margin math at different price points."
    )
    st.caption(
        "Plug in numbers to see how price and volume affect your margins. "
        "Benchmark: SaaS companies target 80%+ gross margins. AI companies "
        "typically run 50-65%."
    )

    cost = st.number_input(
        "Cost per unit ($)",
        min_value=0.01,
        value=1.00,
        step=0.25,
        format="%.2f",
        key="gmc_cost",
        help=(
            "From the Unit Cost Calculator, or your best estimate. "
            "Examples: $0.05 per API call, $2.50 per document, "
            "$15 per human-reviewed output"
        ),
    )
    price = st.number_input(
        "Price per unit ($)",
        min_value=0.01,
        value=3.00,
        step=0.50,
        format="%.2f",
        key="gmc_price",
        help=(
            "What you charge the customer per unit. Examples: $0.99 per "
            "resolution (Intercom), $50 per demand letter, $5 per "
            "qualified lead"
        ),
    )
    units = st.number_input(
        "Units/customer/month",
        min_value=1,
        value=100,
        step=10,
        key="gmc_units",
        help=(
            "Examples: A support bot might handle 500 tickets/month per "
            "customer. A document tool might process 50 docs/month."
        ),
    )
    customers = st.number_input(
        "Number of customers",
        min_value=1,
        value=10,
        step=5,
        key="gmc_customers",
        help="Current or projected customer count",
    )

    # Calculations
    margin = (price - cost) / price * 100 if price > 0 else 0.0
    profit_per_cust = (price - cost) * units
    total_profit = profit_per_cust * customers

    # Display
    c1, c2, c3 = st.columns(3)
    c1.metric("Gross Margin", f"{margin:.0f}%")
    c2.metric("Monthly Profit/Customer", f"${profit_per_cust:,.0f}")
    c3.metric("Monthly Total Profit", f"${total_profit:,.0f}")

    # Benchmark bar chart
    if margin > 65:
        bar_color = "#22C55E"
    elif margin >= 50:
        bar_color = "#EAB308"
    else:
        bar_color = "#EF4444"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=["SaaS Benchmark", "AI Average", "Your Margin"],
            x=[80, 55, margin],
            orientation="h",
            marker_color=["#64748B", "#64748B", bar_color],
            text=["80%", "55%", f"{margin:.0f}%"],
            textposition="outside",
            textfont=dict(size=13),
        )
    )
    fig.update_layout(
        height=150,
        margin=dict(l=0, r=35, t=0, b=0),
        xaxis=dict(range=[0, 105], visible=False),
        yaxis=dict(autorange="reversed", tickfont=dict(size=13)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
