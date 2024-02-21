from dash import dcc

from ai_leads.ui.dash_app.Config.param import COLOR_DICT_STATUS

# Dropdown component for selecting contact status
attributed_status_dropdown = dcc.Dropdown(
    id="filter-status-dropdown",
    options=list(COLOR_DICT_STATUS.keys()),
    multi=True,
    placeholder="Status des prospect",
    style={"border-color": "#ECECEC"},
)
