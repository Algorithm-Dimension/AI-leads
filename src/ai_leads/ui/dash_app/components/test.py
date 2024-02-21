import json

import dash_bootstrap_components as dbc
from dash import ALL, Dash, Input, Output, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from ai_leads.ui.dash_app.Config.param import COLOR_DICT_ATTRIBUTED_SALE, COLOR_DICT_JOB_BOARD_BADGES, JOBS_PER_PAGE

app = Dash(
    __name__,
    assets_folder="assets",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True,
    title="Kara leads",
)

# Données de test pour les boutons

attributed_tag_input = html.Div(
    [
        html.Button(
            f"Button {attributed_sale}",
            id={"type": "add_attributed_sale", "index": attributed_sale},
            n_clicks=0,
            style={"margin": "5px", "backgroundColor": COLOR_DICT_ATTRIBUTED_SALE[attributed_sale]},
        )
        for attributed_sale in COLOR_DICT_ATTRIBUTED_SALE
    ],
    style={"padding": "20px"},
)


@app.callback(
    Output("output", "children"),
    [Input({"type": "add_attributed_sale", "index": ALL}, "n_clicks")],
    prevent_initial_call=True,
)
def on_button_click(n_clicks):
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate

    # Obtenir l'identifiant du bouton déclencheur
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    button_id = json.loads(button_id)  # Convertir la chaîne de caractères en dictionnaire
    index = button_id["index"]

    return f"Button {index} was clicked"


app.layout = html.Div([attributed_tag_input, html.Div(id="output")])


if __name__ == "__main__":
    app.run_server(debug=True)
