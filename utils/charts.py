"""Plotly chart builders."""

import plotly.graph_objects as go


def create_value_framework_chart(x_score, y_score):
    """Build the 2x2 Value Framework scatter chart.

    Args:
        x_score: float -1 to 1 (cost savings to revenue uplift)
        y_score: float -1 to 1 (soft ROI to hard ROI)

    Returns:
        plotly Figure
    """
    fig = go.Figure()

    # User position marker
    fig.add_trace(
        go.Scatter(
            x=[x_score],
            y=[y_score],
            mode="markers",
            marker=dict(size=20, color="#0EA5E9", line=dict(width=2, color="#fff")),
            name="Your Position",
            showlegend=False,
            hovertemplate="x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
        )
    )

    # Quadrant background rectangles
    quadrant_shapes = [
        # Revenue Engine — top-right (green)
        dict(
            type="rect", x0=0, x1=1.3, y0=0, y1=1.3,
            fillcolor="rgba(34, 197, 94, 0.10)", line=dict(width=0), layer="below",
        ),
        # Efficiency Machine — top-left (blue)
        dict(
            type="rect", x0=-1.3, x1=0, y0=0, y1=1.3,
            fillcolor="rgba(59, 130, 246, 0.10)", line=dict(width=0), layer="below",
        ),
        # Promise Zone — bottom-right (yellow)
        dict(
            type="rect", x0=0, x1=1.3, y0=-1.3, y1=0,
            fillcolor="rgba(234, 179, 8, 0.10)", line=dict(width=0), layer="below",
        ),
        # Danger Zone — bottom-left (red)
        dict(
            type="rect", x0=-1.3, x1=0, y0=-1.3, y1=0,
            fillcolor="rgba(239, 68, 68, 0.10)", line=dict(width=0), layer="below",
        ),
        # Dashed zero-lines
        dict(
            type="line", x0=-1.3, x1=1.3, y0=0, y1=0,
            line=dict(color="rgba(148,163,184,0.5)", width=1, dash="dash"),
        ),
        dict(
            type="line", x0=0, x1=0, y0=-1.3, y1=1.3,
            line=dict(color="rgba(148,163,184,0.5)", width=1, dash="dash"),
        ),
    ]

    # Quadrant label annotations
    annotations = [
        dict(
            x=0.85, y=1.15, text="Revenue Engine", showarrow=False,
            font=dict(size=13, color="rgba(34, 197, 94, 0.85)"),
        ),
        dict(
            x=-0.85, y=1.15, text="Efficiency Machine", showarrow=False,
            font=dict(size=13, color="rgba(59, 130, 246, 0.85)"),
        ),
        dict(
            x=0.85, y=-1.15, text="Promise Zone", showarrow=False,
            font=dict(size=13, color="rgba(234, 179, 8, 0.85)"),
        ),
        dict(
            x=-0.85, y=-1.15, text="Danger Zone", showarrow=False,
            font=dict(size=13, color="rgba(239, 68, 68, 0.85)"),
        ),
    ]

    fig.update_layout(
        shapes=quadrant_shapes,
        annotations=annotations,
        xaxis=dict(
            range=[-1.3, 1.3],
            title="Cost Savings \u2190 \u2192 Revenue Uplift",
            zeroline=False,
            showgrid=False,
        ),
        yaxis=dict(
            range=[-1.3, 1.3],
            title="Soft ROI \u2190 \u2192 Hard ROI",
            zeroline=False,
            showgrid=False,
        ),
        height=500,
        margin=dict(l=60, r=60, t=30, b=60),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
    )

    return fig
