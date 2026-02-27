"""Recommendation data: business models, quadrants, pricing logic, health check actions."""

BUSINESS_MODELS = {
    "Copilot": {
        "description": (
            "Your AI works alongside a human user in real-time, augmenting their "
            "capabilities rather than replacing them. The user remains in the driver's "
            "seat while your AI suggests, drafts, and recommends. Value scales with "
            "how many people adopt the tool across an organization."
        ),
        "examples": [
            "GitHub Copilot - AI pair programmer that suggests code in-editor",
            "Grammarly - AI writing assistant that improves text as you type",
            "Notion AI - drafts, summarizes, and edits within the user's workflow",
        ],
        "pricing_implications": (
            "Per-seat pricing works well because value is tied to individual users. "
            "Consider feature tiers to capture different willingness-to-pay across segments."
        ),
    },
    "Agent": {
        "description": (
            "Your AI operates autonomously or semi-autonomously, completing entire "
            "tasks or workflows with minimal human intervention. The user defines the "
            "goal and the AI executes, sometimes with a human review step. Value is "
            "measured in outcomes delivered, not time spent using the product."
        ),
        "examples": [
            "Intercom Fin - AI agent that resolves customer support tickets autonomously",
            "Devin - AI software engineer that completes coding tasks end-to-end",
            "Resolve AI - autonomous incident response and uptime management",
        ],
        "pricing_implications": (
            "Outcome-based or per-task pricing aligns cost with value delivered. "
            "Customers pay for results, not access, which de-risks the purchase decision."
        ),
    },
    "AI-enabled Service": {
        "description": (
            "Your AI delivers a finished output or service result, often replacing "
            "work previously done by agencies, consultants, or service providers. "
            "There may be a human QA layer, but the AI does the heavy lifting. "
            "Customers evaluate you against the cost of the service you replace."
        ),
        "examples": [
            "EvenUp - AI-generated legal demand packages replacing paralegal work",
            "Pepper Content - AI content creation replacing freelance writers",
            "Jasper - AI marketing content replacing agency copywriting",
        ],
        "pricing_implications": (
            "Price anchored to the cost of the service you replace, typically at a "
            "discount. Per-deliverable pricing makes the value proposition concrete."
        ),
    },
}

QUADRANTS = {
    "Revenue Engine": {
        "label": "Revenue Engine",
        "description": (
            "Your product delivers measurable, hard-to-argue-with ROI that directly "
            "drives revenue growth. Customers can point to concrete revenue gains."
        ),
        "pricing_implication": (
            "You have pricing power. Anchor to the revenue you generate and consider "
            "value-based or outcome-based pricing with confidence."
        ),
        "renewal_risk": False,
    },
    "Efficiency Machine": {
        "label": "Efficiency Machine",
        "description": (
            "Your product delivers hard, measurable ROI through cost reduction. "
            "Customers can calculate exactly what they save by using you."
        ),
        "pricing_implication": (
            "Price as a fraction of documented savings. Budget replacement framing "
            "makes procurement straightforward, but watch for deflationary pressure."
        ),
        "renewal_risk": False,
    },
    "Promise Zone": {
        "label": "Promise Zone",
        "description": (
            "Your product enables revenue upside but the ROI is hard to quantify. "
            "Customers believe in the value but can't easily prove it with data."
        ),
        "pricing_implication": (
            "Build measurement into your product to move toward hard ROI. In the "
            "meantime, use hybrid pricing with a low base to reduce purchase friction."
        ),
        "renewal_risk": True,
    },
    "Danger Zone": {
        "label": "Danger Zone",
        "description": (
            "Your product saves costs but the ROI is hard to prove. This is the "
            "hardest position to price from - you're competing for budget without "
            "concrete evidence of impact."
        ),
        "pricing_implication": (
            "Prioritize building ROI dashboards and concrete metrics. Keep pricing "
            "low and simple to minimize purchase friction while you build proof points."
        ),
        "renewal_risk": True,
    },
}


def get_pricing_recommendation(business_model, quadrant, cost_variance):
    """Return pricing recommendation based on model, quadrant, and cost variance.

    Args:
        business_model: "Copilot", "Agent", or "AI-enabled Service"
        quadrant: "Revenue Engine", "Efficiency Machine", "Promise Zone", or "Danger Zone"
        cost_variance: "low", "moderate", or "high"

    Returns:
        dict with model_name, rationale, formula_type
    """
    hard_roi = quadrant in ("Revenue Engine", "Efficiency Machine")

    if business_model == "Copilot":
        if hard_roi and cost_variance == "low":
            return {
                "model_name": "Per-seat + Feature Tiers",
                "rationale": (
                    "Your copilot delivers measurable value with predictable costs. "
                    "Per-seat pricing captures value as adoption grows, while feature "
                    "tiers let you segment by willingness-to-pay."
                ),
                "formula_type": "per_seat",
            }
        else:
            return {
                "model_name": "Hybrid (Base + Usage Tiers)",
                "rationale": (
                    "A platform fee provides revenue predictability while usage-based "
                    "tiers align your revenue with the value users extract. This "
                    "protects margins when costs are variable or ROI is soft."
                ),
                "formula_type": "hybrid",
            }

    elif business_model == "Agent":
        if hard_roi and cost_variance in ("low", "moderate"):
            return {
                "model_name": "Outcome-based",
                "rationale": (
                    "Your agent delivers measurable results with manageable cost "
                    "variance. Charging per outcome aligns your price directly with "
                    "the value customers receive, making the ROI self-evident."
                ),
                "formula_type": "outcome",
            }
        elif hard_roi and cost_variance == "high":
            return {
                "model_name": "Hybrid (Base + Outcome Credits)",
                "rationale": (
                    "Your agent delivers hard ROI but high cost variance means pure "
                    "outcome pricing risks margin erosion. A base fee covers fixed "
                    "costs while outcome credits capture upside."
                ),
                "formula_type": "hybrid",
            }
        else:
            return {
                "model_name": "Workflow-based (Per Task)",
                "rationale": (
                    "With soft ROI, charging per task completed makes the price "
                    "concrete and predictable for buyers. It also naturally caps "
                    "your cost exposure per unit of revenue."
                ),
                "formula_type": "workflow",
            }

    else:  # AI-enabled Service
        if hard_roi:
            return {
                "model_name": "Outcome-based (Per Deliverable)",
                "rationale": (
                    "Your service delivers measurable results that replace existing "
                    "spend. Per-deliverable pricing anchors to the service you replace "
                    "and makes ROI calculation trivial for the buyer."
                ),
                "formula_type": "outcome",
            }
        else:
            return {
                "model_name": "Workflow-based + SLA Tiers",
                "rationale": (
                    "With soft ROI, workflow-based pricing keeps the unit economics "
                    "clear while SLA tiers (turnaround time, quality guarantees) let "
                    "you capture willingness-to-pay from premium customers."
                ),
                "formula_type": "workflow",
            }


HEALTH_CHECK_ACTIONS = {
    "m4_q1": (
        "Study the key differences between AI and SaaS unit economics. AI companies "
        "typically have 50-60% gross margins vs 80-90% for SaaS. Factor in inference "
        "costs, model training, and data processing when calculating your true margins."
    ),
    "m4_q2": (
        "Map your product's delivery model (copilot, agent, or service) to the pricing "
        "models that align with customer expectations. Misalignment between how value "
        "is delivered and how you charge is the #1 cause of pricing friction."
    ),
    "m4_q3": (
        "Simplify your pricing page to pass the '5-second test' - can a first-time "
        "visitor understand what they'll pay? Consider removing usage dimensions that "
        "require explanation and anchoring on a metric your buyer already tracks."
    ),
    "m4_q4": (
        "Build a cost monitoring dashboard tracking per-customer inference costs. Set "
        "up alerts for cost spikes and consider implementing usage caps, prompt caching, "
        "or model cascading to reduce cost variance."
    ),
    "m4_q5": (
        "Define specific activation signals (e.g., 3+ high-value outputs, team sharing, "
        "integration setup) that indicate a user has experienced enough value to convert. "
        "Time-based trials often underperform value-based triggers for AI products."
    ),
    "m4_q6": (
        "Start tracking AI-specific metrics: cost per AI interaction, AI resolution rate, "
        "value delivered per dollar of inference cost, and output quality scores. These "
        "supplement but don't replace traditional SaaS metrics like NRR and CAC."
    ),
    "m4_q7": (
        "Build a unit economics model that includes all hidden costs: inference API calls, "
        "fine-tuning, human review/QA time, data storage, and retraining cycles. Many AI "
        "companies underestimate true costs by 30-50%."
    ),
    "m4_q8": (
        "If you and competitors use similar foundation models, your pricing differentiation "
        "must come from proprietary data, fine-tuning, workflow integration, or domain "
        "expertise - not the AI itself. Price the outcome, not the model."
    ),
    "m4_q9": (
        "Stress-test your pricing against 3 scenarios: inference costs increase 2x, "
        "customer usage doubles, and a competitor offers a free tier. If your pricing "
        "breaks under any scenario, you have a sustainability gap to address."
    ),
    "m4_q10": (
        "Audit your pricing for scalability friction: custom quotes, manual provisioning, "
        "complex metering, or per-customer pricing exceptions. Each adds operational "
        "overhead that compounds. Design for self-serve where possible."
    ),
}
