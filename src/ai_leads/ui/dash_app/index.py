import os

from dash import dcc, html
from dash.dependencies import Input, Output

import ai_leads.ui.dash_app.utils as utils
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components import navbar
from ai_leads.ui.dash_app.pages import prospect_detail, prospect_list

nav = navbar.navbar

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        nav,
        html.Div(id="page-content", children=[], className="mt-5"),
    ]
)


@app.callback(
    Output("page-content", "children"),
    Output("page-1", "active"),
    Output("page-2", "active"),
    [Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/prospect_list" or pathname == "/":
        return prospect_list.layout, False, False
    elif pathname == "/prospect_detail":
        return prospect_detail.layout_function(20530), False, False
    elif "/prospect_detail/university_id_" in pathname:
        id = utils.extract_fice_id_university_detail(pathname)
        return prospect_detail.layout_function(int(id)), False, False
    elif "/prospect_detail/corporate_id_" in pathname:
        id = utils.extract_corporate_id_detail(pathname)
        return prospect_detail.layout_function_corp(int(id)), False, False
    elif "/prospect_detail/healthcare_id_" in pathname:
        id = utils.extract_healthcare_id_detail(pathname)
        return prospect_detail.layout_function_healthcare(int(id)), False, False
    # You can also return a 404 page here
    # You can also return a 404 page here
    return ("404 Error", False, False)


# Run the app on localhost:8050
if __name__ == "__main__":
    app.run_server(
        debug=not bool(os.environ.get("PRODUCTION")),
        host="0.0.0.0",
    )
