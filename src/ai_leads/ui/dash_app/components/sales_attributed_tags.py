import json
from typing import List, Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
import numpy as np
import pandas as pd
from dash import html
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from ai_leads.Config.param import LEAD_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE


def tag_component(attributed_sale: str, ind: int):
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
                                    id={
                                        "type": "delete-badge-button",
                                        "index": ind,
                                    },
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
                    else None,
                    pill=True,
                    className="px-2",
                ),
                align="left",
            )
        )
        return tag_component_section


@app.callback(
    Output("container-for-badges", "children"),
    [Input({"type": "delete-badge-button", "index": ALL}, "n_clicks")],
    prevent_initial_call=True,
)
def delete_badge(n_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate  # Prevents callback from firing initially

    button_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    index_found = int(button_id["index"])  # Convertit en entier

    df_final_result_leads = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)
    # Assuming 'index_found' is correctly identifying the row to be updated
    df_final_result_leads.at[index_found, "attributed_sale"] = np.nan
    df_final_result_leads.to_csv(LEAD_FILE_PATH, sep=";", index=False)

    return dash.no_update  # Or update your badges layout accordingly
