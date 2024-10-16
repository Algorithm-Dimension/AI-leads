import os

import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output

import ai_leads.ui.dash_app.utils as utils
from ai_leads.Config.param import LEAD_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components import modify_prospect_form, navbar
from ai_leads.ui.dash_app.components.modify_prospect_form import (
    CURRENT_COMPANY_TAG_STATUS,
)
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
    elif "/list_offers/" in pathname:
        company = utils.extract_client_name(pathname)
        return prospect_detail.layout_function(company), False, False
    # elif "/prospect_detail/corporate_id_" in pathname:
    #    id = utils.extract_client_name(pathname)
    #    return prospect_detail.layout_function_corp(int(id)), False, False
    # elif "/prospect_detail/healthcare_id_" in pathname:
    #    id = utils.extract_client_name(pathname)
    #    return prospect_detail.layout_function_healthcare(int(id)), False, False
    # You can also return a 404 page here
    return ("404 Error", False, False)


# Run the app on localhost:8050
if __name__ == "__main__":
    df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";")
    df_final_result_leads["Entreprise"].apply(
        modify_prospect_form.callback_function_creation_boutton_tag_sale
    )
    df_final_result_leads["Entreprise"].apply(
        modify_prospect_form.callback_function_creation_boutton_status
    )
    app.run_server(
        debug=not bool(os.environ.get("PRODUCTION")),
        host="0.0.0.0",
        port=8050,
        dev_tools_props_check=True,
    )

# l'application est configurée pour s'exécuter sur le port 8050 en écoutant toutes les interfaces réseau (0.0.0.0)
# ce qui signifie qu'elle sera accessible localement via HTTP
# (important à avoir lors de la configuration du pare-feu de l'EC2)
