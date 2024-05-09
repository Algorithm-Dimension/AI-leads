import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.Button("Precedent", id="precedent-button"),
        html.Div(id="output-div"),
    ]
)


@app.callback(Output("output-div", "children"), Input("precedent-button", "n_clicks"))
def go_to_precedent_page(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        # Add your code here to handle going back to the precedent page
        # You can use the Flask request object to get the current URL and redirect to the precedent page
        # For example:
        # precedent_url = request.referrer
        # return redirect(precedent_url)
        return "Going back to the precedent page..."
    else:
        return ""


if __name__ == "__main__":
    app.run_server(debug=True)
