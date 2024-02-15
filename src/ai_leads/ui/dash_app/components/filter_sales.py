from dash import dcc
from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE

# Dropdown component for selecting contact status
contact_dropdown = dcc.Dropdown(
    id="contact-dropdown",
    options=list(COLOR_DICT_ATTRIBUTED_SALE.keys()),
    multi=True,
    placeholder="Mes prospects",
    style={"border-color": "#ECECEC"},
)
