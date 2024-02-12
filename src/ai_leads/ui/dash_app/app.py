import os

import dash_auth
import dash_bootstrap_components as dbc
from dash import Dash
from dotenv import load_dotenv

load_dotenv()

app = Dash(
    __name__,
    assets_folder="assets",
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True,
    title="Kara leads",
)
auth = dash_auth.BasicAuth(
    app,
    {os.environ.get("DASH_USERNAME"): os.environ.get("DASH_PASSWORD")},
)
server = app.server  # Expose le serveur pour le déploiement
