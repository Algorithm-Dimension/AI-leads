import json
from typing import List, Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import callback_context, html, no_update
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate

from ai_leads import utils
from ai_leads.Config.param import COMPANY_FILE_PATH, LEAD_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE

# Supposons que df_lead est déjà chargé
df_lead = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)


def tag_component_attributed_sales(attributed_sale: str, company: str):
    clean_company = utils.clean_str_unidecode(company)
    if not pd.isna(attributed_sale):
        tag_component_section = dbc.Row(
            dbc.Col(
                dbc.Badge(
                    dbc.Row(
                        [
                            dbc.Col(attributed_sale, className="d-flex align-items-center", width="auto"),
                            dbc.Col(
                                dbc.Button(
                                    html.Span("×", style={"fontSize": "10px", "lineHeight": "1"}),
                                    style={"backgroundColor": "transparent", "border": "none", "padding": 0},
                                    className="d-flex align-items-center p-0",
                                    id={"type": "delete-badge-button", "index": clean_company},
                                    n_clicks=0,
                                ),
                                width="auto",
                                className="d-flex align-items-center justify-content-center",
                            ),
                        ],
                        className="g-1 align-items-center",
                    ),
                    color=COLOR_DICT_ATTRIBUTED_SALE.get(attributed_sale, "light"),
                    pill=True,
                    className="px-2",
                ),
                align="left",
            )
        )
    else:
        tag_component_section = None  # Pas besoin de créer une div vide si aucun tag n'est attribué
    return html.Div(tag_component_section, id={"type": "delete-badge-button-set", "index": clean_company})


@app.callback(
    Output({"type": "delete-badge-button-set", "index": MATCH}, "style"),
    Input({"type": "delete-badge-button", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_tag_attribute_sale(n_clicks):
    df_lead = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)
    df_table_company = pd.read_csv(COMPANY_FILE_PATH, sep=";", dtype=str)

    if n_clicks is None:
        raise PreventUpdate

    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"]
    company_index = triggered_id.split(".")[0]  # Récupère l'index à partir de l'ID
    company_index = eval(company_index)["index"]  # Convertit la chaîne en dictionnaire puis extrait l'index
    print(company_index)
    # Mettre à jour les données comme nécessaire ici
    # Note : Cette étape dépend de la logique métier spécifique et de la structure des données

    # Retourner le style pour cacher la `div` correspondante

    df_lead.loc[
        df_lead["Entreprise"].apply(utils.clean_str_unidecode) == utils.clean_str_unidecode(company_index),
        "attributed_sale",
    ] = np.nan

    df_table_company.loc[
        df_table_company["company"].apply(utils.clean_str_unidecode) == utils.clean_str_unidecode(company_index),
        "attributed_sale",
    ] = np.nan

    df_lead.to_csv(LEAD_FILE_PATH, sep=";", index=False)
    df_table_company.to_csv(COMPANY_FILE_PATH, sep=";", index=False)
    return {"display": "none"}
