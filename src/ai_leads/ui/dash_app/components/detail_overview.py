import dash_bootstrap_components as dbc
from ai_leads import utils
from ai_leads.ui.dash_app.app import app
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from ai_leads.Config.param import LEAD_FILE_PATH
from dash import html, no_update, callback_context
from ai_leads.ui.dash_app.pages import prospect_detail


def detail_jobs_section_modal(company: str):
    clean_company = utils.clean_str_unidecode(company)
    return html.Div(
        [
            dbc.Button(
                [html.Img(src="../assets/svg/eye.svg"), "Détail"],
                style={
                    "display": "flex",
                    "flex-direction": "row",
                    "align-items": "center",
                    "column-gap": "8px",
                    "margin-bottom": "5px",
                },
                id={"type": "detail-company-button", "index": clean_company},
            ),
            dbc.Modal(
                [
                    dbc.ModalBody(prospect_detail.layout_function(company)),
                ],
                id={"type": "modal-detail-view", "index": clean_company},
                size="xl",
            ),
        ]
    )


@app.callback(
    Output({"type": "modal-detail-view", "index": MATCH}, "is_open"),
    Input({"type": "detail-company-button", "index": MATCH}, "n_clicks"),
    State({"type": "modal-detail-view", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
