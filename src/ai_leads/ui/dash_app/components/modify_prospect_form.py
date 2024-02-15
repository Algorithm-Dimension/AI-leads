import dash_bootstrap_components as dbc
from ai_leads import utils
from ai_leads.ui.dash_app.app import app
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from ai_leads.Config.param import LEAD_FILE_PATH
from dash import html, no_update, callback_context

email_input = dbc.Row(
    [
        dbc.Label("Email", html_for="example-email-row", width=2),
        dbc.Col(
            dbc.Input(type="email", id="example-email-row", placeholder="Enter email"),
            width=10,
        ),
    ],
    className="mb-3",
)

password_input = dbc.Row(
    [
        dbc.Label("Password", html_for="example-password-row", width=2),
        dbc.Col(
            dbc.Input(
                type="password",
                id="example-password-row",
                placeholder="Enter password",
            ),
            width=10,
        ),
    ],
    className="mb-3",
)

radios_input = dbc.Row(
    [
        dbc.Label("Radios", html_for="example-radios-row", width=2),
        dbc.Col(
            dbc.RadioItems(
                id="example-radios-row",
                options=[
                    {"label": "First radio", "value": 1},
                    {"label": "Second radio", "value": 2},
                    {
                        "label": "Third disabled radio",
                        "value": 3,
                        "disabled": True,
                    },
                ],
            ),
            width=10,
        ),
    ],
    className="mb-3",
)


def modify_propsect_form_section_modal(company: str):
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
                    dbc.ModalBody(dbc.Form([email_input, password_input, radios_input])),
                ],
                id={"type": "modal-form-modify", "index": clean_company},
            ),
        ]
    )


@app.callback(
    Output({"type": "modal-form-modify", "index": MATCH}, "is_open"),
    Input({"type": "modifier-company-button", "index": MATCH}, "n_clicks"),
    State({"type": "modal-form-modify", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
