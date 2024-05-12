from dash import dcc

from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE

# Dropdown component
past_interactions_dropdown = dcc.Dropdown(
    id="filter-past-interaction-dropdown",
    options=["Oui", "Non"],
    multi=False,
    placeholder="Interactions passées ?",
    style={"border-color": "#ECECEC"},
)
