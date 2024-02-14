import json
from typing import List, Optional

import dash_bootstrap_components as dbc
from dash import html, no_update
import numpy as np
import pandas as pd
from dash import html, callback_context

from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from ai_leads.Config.param import LEAD_FILE_PATH, COMPANY_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE
from ai_leads import utils


def tag_component(attributed_sale: str, company: str):
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
                                    id="delete-badge-button-" + utils.clean_str_unidecode(company),
                                    n_clicks=0,  # Utilisez un ID dynamique basé sur index
                                ),
                                width="auto",
                                className="d-flex align-items-center justify-content-center",
                            ),
                        ],
                        className="g-1 align-items-center",
                    ),
                    color=COLOR_DICT_ATTRIBUTED_SALE[attributed_sale]
                    if attributed_sale in COLOR_DICT_ATTRIBUTED_SALE
                    else "light",
                    pill=True,
                    className="px-2",
                ),
                align="left",
            )
        )
    else:
        tag_component_section = html.Div(id="delete-badge-button-" + utils.clean_str_unidecode(company))
    return html.Div(tag_component_section, id="delete-badge-button-set" + utils.clean_str_unidecode(company))


df_lead = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)


@app.callback(
    [
        Output("delete-badge-button-set" + utils.clean_str_unidecode(company), "style")
        for company in df_lead["Entreprise"]
    ],
    [
        Input("delete-badge-button-" + utils.clean_str_unidecode(company), "n_clicks")
        for company in df_lead["Entreprise"]
    ],
    prevent_initial_call=True,  # Pour éviter que le callback ne se déclenche au chargement de la page
)
def delete_tag_attribute_sale(*args):
    df_lead = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)
    df_table_company = pd.read_csv(COMPANY_FILE_PATH, sep=";", dtype=str)
    ctx = callback_context

    if not ctx.triggered:
        # Si rien n'a été déclenché, ne pas modifier le style
        return no_update
    triggered_id = str(callback_context.triggered[0]["prop_id"].split(".")[0])
    company = triggered_id.split("-")[-1]
    return_list = [
        {"display": "none"} if company == utils.clean_str_unidecode(company_test) else no_update
        for company_test in list(df_lead["Entreprise"])
    ]
    df_lead.loc[
        df_lead["Entreprise"].apply(utils.clean_str_unidecode) == utils.clean_str_unidecode(company), "attributed_sale"
    ] = np.nan

    df_table_company.loc[
        df_table_company["company"].apply(utils.clean_str_unidecode) == utils.clean_str_unidecode(company),
        "attributed_sale",
    ] = np.nan

    df_lead.to_csv(LEAD_FILE_PATH, sep=";", index=False)
    df_table_company.to_csv(COMPANY_FILE_PATH, sep=";", index=False)

    print("Deleted company:", company)
    # Retourner le style pour cacher la `div` correspondante
    return return_list
