from dash import Dash, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html

modal = html.Div(
    [
        dbc.Button("Open modal", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Header")),
                dbc.ModalBody("This is the content of the modal"),
                dbc.ModalFooter(dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)


@app.callback(
    [Output("modal", "is_open")],
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        print(is_open)
        return [not is_open]
    print(not is_open)
    return [is_open]


app.layout = html.Div(modal)

if __name__ == "__main__":
    app.run_server(debug=True)
