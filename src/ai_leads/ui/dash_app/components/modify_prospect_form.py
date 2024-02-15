import dash_bootstrap_components as dbc
from ai_leads import utils
from ai_leads.ui.dash_app.app import app
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from ai_leads.Config.param import LEAD_FILE_PATH, COMPANY_FILE_PATH
from dash import html, no_update, callback_context
from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE
import json

CURRENT_COMPANY = []


def attributed_tag_input(company: str, existing_attributed_sale: str = "") -> dbc.Row:
    attributed_tag_input = dbc.Row(
        [
            dbc.Label("Propriétaire de ce prospect ?", html_for="example-email-row"),
            html.Div(
                [
                    dbc.Button(
                        attributed_sale,
                        color=COLOR_DICT_ATTRIBUTED_SALE[attributed_sale],
                        className="me-3",
                        id="add_attributed_sale-" + utils.clean_str_unidecode(company) + "-" + attributed_sale,
                        outline=True if attributed_sale != existing_attributed_sale else False,
                    )
                    for attributed_sale in COLOR_DICT_ATTRIBUTED_SALE
                ]
            ),
        ],
        className="px-2",
    )
    return attributed_tag_input


password_input = dbc.Row()

radios_input = dbc.Row()


def modify_prospect_form_section_modal(company: str):
    clean_company = utils.clean_str_unidecode(company)
    return html.Div(
        [
            dbc.Button(
                [html.I(className="bi bi-pencil-fill"), "Modifier"],
                id={"type": "modifier-company-button", "index": clean_company},
                n_clicks=0,
                style={
                    "display": "flex",
                    "flex-direction": "row",
                    "align-items": "center",
                    "column-gap": "8px",
                    "color": "success",
                },
            ),
            dbc.Modal(
                [
                    dbc.ModalBody(dbc.Form([attributed_tag_input(company), password_input, radios_input])),
                ],
                id={"type": "modal-form-modify", "index": clean_company},
                size="xl",
            ),
        ]
    )


@app.callback(
    Output({"type": "modal-form-modify", "index": MATCH}, "is_open"),
    Input({"type": "modifier-company-button", "index": MATCH}, "n_clicks"),
    State({"type": "modal-form-modify", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_modal_detail_form(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


df_lead = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)


def callback_function_creation_boutton_tag_sale(company: str):
    if company in CURRENT_COMPANY:
        return
    CURRENT_COMPANY.append(company)

    @app.callback(
        Output("output-attributed_sale" + "-" + utils.clean_str_unidecode(company), "children"),
        [
            Input("add_attributed_sale-" + utils.clean_str_unidecode(company) + "-" + attributed_sale, "n_clicks")
            for attributed_sale in COLOR_DICT_ATTRIBUTED_SALE
        ],
        prevent_initial_call=True,
    )
    def on_button_click(*args):
        df_lead = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)
        df_table_company = pd.read_csv(COMPANY_FILE_PATH, sep=";", dtype=str)
        ctx = callback_context
        # Obtenir l'identifiant du bouton déclencheur
        button_id = ctx.triggered[0]["prop_id"].split(".")[0].split("-")
        attributed_sale = button_id[-1]
        company_index = button_id[-2]
        print(company_index)
        df_lead.loc[
            df_lead["Entreprise"].apply(utils.clean_str_unidecode) == company_index,
            "attributed_sale",
        ] = attributed_sale

        df_table_company.loc[
            df_table_company["company"].apply(utils.clean_str_unidecode) == company_index,
            "attributed_sale",
        ] = attributed_sale

        df_lead.to_csv(LEAD_FILE_PATH, sep=";", index=False)
        df_table_company.to_csv(COMPANY_FILE_PATH, sep=";", index=False)
        return f"{attributed_sale} s'occupera désormais de ce client/prospect"

    return on_button_click
