import os
from typing import List, Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html
from ai_leads.ui.dash_app.components import sales_attributed_tags, modify_prospect_form
from ai_leads import utils

# Local application imports
from ai_leads.Config.param import LAST_UPDATE

BASE_DATE_STR = LAST_UPDATE.strftime("%d/%m/%y")


def component_card_function(company, nb_offer, website_url, attributed_sale, display="flex"):
    component_tag = sales_attributed_tags.tag_component(attributed_sale, company)
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
                                            company.title(),
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
                                dbc.Row(
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                [html.Img(src="../assets/svg/eye.svg"), "Détail"],
                                                href=f"/list_offers/{utils.clean_str_unidecode(company).replace(' ', '')}",
                                                style={
                                                    "display": "flex",
                                                    "flex-direction": "row",
                                                    "align-items": "center",
                                                    "column-gap": "8px",
                                                    "margin-bottom": "5px",
                                                },
                                            ),
                                            # html.Div(
                                            #   [
                                            #      modify_prospect_form.modify_prospect_form_section_modal(company),
                                            # ]
                                            # ),
                                        ]
                                    ),
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
                        component_tag,
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
