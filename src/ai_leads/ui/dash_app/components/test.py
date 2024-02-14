import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Initialiser l'application Dash avec un thème Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Button("Cliquez-moi", id="button", n_clicks=0, className="me-2"),
        dbc.Badge("Disparaissez", color="primary", id="badge"),
    ],
    id="container",  # Ajout d'un ID pour le conteneur div
)


@app.callback(Output("container", "style"), [Input("button", "n_clicks")])  # Modifier le style du conteneur
def toggle_visibility(n_clicks):
    if n_clicks and n_clicks > 0:
        # Rendre le conteneur invisible après le clic
        return {"display": "none"}
    else:
        # Afficher le conteneur avant le clic
        return {}


if __name__ == "__main__":
    app.run_server(debug=True)
