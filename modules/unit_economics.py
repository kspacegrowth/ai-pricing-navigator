"""Sidebar unit economics calculator - live-updating."""

import streamlit as st
import plotly.graph_objects as go


def render_unit_economics():
    """Render the compact unit economics calculator in the sidebar."""
    st.sidebar.subheader("\U0001f4b9 Unit Economics Calculator")

    cost = st.sidebar.number_input(
        "Cost per unit ($)", min_value=0.01, value=1.00, step=0.25,
        key="ue_cost", format="%.2f",
    )
    price = st.sidebar.number_input(
        "Price per unit ($)", min_value=0.01, value=3.00, step=0.50,
        key="ue_price", format="%.2f",
    )
    units = st.sidebar.number_input(
        "Units/customer/month", min_value=1, value=100, step=10,
        key="ue_units",
    )
    customers = st.sidebar.number_input(
        "Number of customers", min_value=1, value=10, step=5,
        key="ue_customers",
    )

    # ---- Calculations (live) ----------------------------------------------
    margin = (price - cost) / price * 100 if price > 0 else 0.0
    profit_per_cust = (price - cost) * units
    total_profit = profit_per_cust * customers

    # ---- Display ----------------------------------------------------------
    st.sidebar.metric("Gross Margin", f"{margin:.0f}%")
    st.sidebar.metric("Monthly Profit/Customer", f"${profit_per_cust:,.0f}")
    st.sidebar.metric("Monthly Total Profit", f"${total_profit:,.0f}")

    # ---- Benchmark bar chart ----------------------------------------------
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
            textfont=dict(size=11),
        )
    )
    fig.update_layout(
        height=150,
        margin=dict(l=0, r=35, t=0, b=0),
        xaxis=dict(range=[0, 105], visible=False),
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        showlegend=False,
    )
    st.sidebar.plotly_chart(fig, use_container_width=True)
