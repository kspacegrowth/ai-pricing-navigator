# CLAUDE.md

AI Pricing Navigator - Streamlit app helping AI founders design pricing strategy. Based on BVP AI Pricing Playbook. 4 modules: Business Model Classifier, Value Framework Mapper, Pricing Recommender, Health Check Scorecard. All state in st.session_state. No database. Plotly for charts.

## Run

```bash
streamlit run app.py
```

## Structure

- `app.py` — Main entry point
- `modules/` — Feature modules (classifier, mapper, recommender, scorecard)
- `data/` — Static data, configs, reference tables
- `utils/` — Shared helpers and utilities
