import base64
import os
from io import BytesIO

import dash_bootstrap_components as dbc
from dash import html

update_button = dbc.Button(
    ["Mettre à jour le statut"],
    id="update-button",
    n_clicks=0,
    outline=True,
    color="primary",
    style={"width": "fit-content", "display": "flex", "flex-direction": "row", "gap": "8px", "align-self": "end"},
)
