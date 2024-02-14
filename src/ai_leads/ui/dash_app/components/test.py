from dash import Dash, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        html.Div(
            [
                dbc.Button("Cliquez-moi", id={"type": "delete-button", "index": i}),
                dbc.Badge("Contenu", id={"type": "content-div", "index": i}),
            ],
            id={"type": "container-div", "index": i},
        )
        for i in range(5)  # Supposons que vous ayez 5 paires de bouton et div
    ]
)


@app.callback(
    Output({"type": "container-div", "index": dash.ALL}, "style"),
    Input({"type": "delete-button", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,  # Pour éviter que le callback ne se déclenche au chargement de la page
)
def hide_div(*args):
    ctx = callback_context
    if not ctx.triggered:
        # Si rien n'a été déclenché, ne pas modifier le style
        return dash.no_update

    # Trouver l'identifiant du bouton qui a été cliqué
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    button_id = eval(button_id)  # Convertir la chaîne de caractères en dictionnaire

    # Retourner le style pour cacher la `div` correspondante
    return [
        {"display": "none"} if button_id == {"type": "delete-button", "index": i} else dash.no_update for i in range(5)
    ]


if __name__ == "__main__":
    app.run_server(debug=True)
