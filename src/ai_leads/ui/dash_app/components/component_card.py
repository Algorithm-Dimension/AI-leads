import os
from typing import List, Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from ai_leads import utils

# Local application imports
from ai_leads.Config.param import LAST_UPDATE, LEAD_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE

BASE_DATE_STR = LAST_UPDATE.strftime("%d/%m/%y")


def component_card_function(client, nb_offer, website_url, display="flex"):
    component_card = html.Div(
        dbc.Card(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                dbc.Row(
                                    dbc.Col(
                                        html.A(
                                            client.title(),
                                            href=website_url,
                                            style={
                                                "color": "#444444",
                                                "text-decoration": "none",
                                                "cursor": "pointer",
                                                "font-weight": "bold",
                                                "font-size": "16px",
                                            },
                                        ),
                                    )
                                ),
                                dbc.Button(
                                    [html.Img(src="../assets/svg/eye.svg"), "Détail"],
                                    href=f"/list_offers/{utils.clean_str_unidecode(client).replace(' ', '')}",
                                    style={
                                        "display": "flex",
                                        "flex-direction": "row",
                                        "align-items": "center",
                                        "column-gap": "8px",
                                    },
                                ),
                            ],
                            style={
                                "justify-content": "space-between",
                                "display": "flex",
                                "flex-direction": "row",
                                "align-items": "center",
                            },
                        ),
                        html.P(["Denière mise à jour: le ", BASE_DATE_STR], style={"margin": "0"}),
                        html.P(
                            f"Nombre d'offre postées les 10 derniers jours : {str(nb_offer)}",
                            style={"margin": "0"},
                        ),
                        dbc.Checkbox(
                            id={"type": "contacted-output", "index": ""},
                            label="Déjà Contacté ?",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "column",
                        "justify-content": "start",
                        "row-gap": "10px",
                        "flex-grow": "1",
                    },
                ),
            ],
            style={
                "display": display,
                "flex-direction": "row",
                "column-gap": "20px",
                "borderRadius": "15px",
                "border-color": "primary",
                "boxShadow": "0 6px 20px 0 #0D234F14",
                "padding": "24px",
            },  # Style de carte global
        )
    )
    return component_card
