import os
from typing import List, Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from ai_leads import utils

# Local application imports
from ai_leads.Config.param import LAST_UPDATE, LEAD_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components import (
    add_contact,
    component_card,
    filter_sales,
    filter_past_interactions,
    search_bar,
    filter_status,
)

# Constants
BASE_DATE_STR = LAST_UPDATE.strftime("%d/%m/%y")
DATA_PATH = "data/"

# Read and preprocess the data
df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";")
df_final_result_leads.replace("n.a.", np.nan, inplace=True)
df_final_result_leads.dropna(subset=["Entreprise"], inplace=True)


@app.callback(
    Output("update-output", "children"),
    Input("update-button", "n_clicks"),
    State({"type": "contacted-output", "index": ALL}, "value"),
)
def update_dataframe(n_clicks: Optional[int], checkbox_states: List[bool]) -> None:
    """
    Update the dataframe 'Contacté' column based on the checkbox state and save it to CSV.

    :param n_clicks: Number of times the update button was clicked.
    :param checkbox_states: List of states for each 'Contacté' checkbox.
    """
    if n_clicks is None or n_clicks < 1:
        raise PreventUpdate

    for company, state in zip(df_final_result_leads["Entreprise"], checkbox_states):
        # Normalize company name for matching
        normalized_company = utils.clean_str_unidecode(company)
        df_final_result_leads.loc[
            df_final_result_leads["Entreprise"].apply(utils.clean_str_unidecode)
            == normalized_company,
            "Contacté",
        ] = "Oui" if state else "Non"

    # Save the updated DataFrame
    df_final_result_leads.to_csv(os.path.join(LEAD_FILE_PATH), sep=";", index=False)


@app.callback(
    Output("leads-list", "children"),
    State("search-input", "value"),
    Input("filter-status-dropdown", "value"),
    Input("filter-sales-dropdown", "value"),
    Input("filter-past-interaction-dropdown", "value"),
    # Input("state-dropdown", "value"),
    # Input("segment-dropdown", "value"),
    Input("search-button", "n_clicks"),
    Input("search-input", "n_submit"),
)
def update_prospect_list(
    search_term="",
    selected_is_contacted=None,
    selected_sales=None,
    selected_past_interactions=None,
    n_clicks_search_button=0,
    n_submit_search_input=0,
):
    df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";")

    if search_term:
        # Filter based on the search term
        filtered_prospects = df_final_result_leads.loc[
            df_final_result_leads["Entreprise"]
            .str.lower()
            .str.contains(search_term.lower())
        ]
    else:
        # Select all prospects if no search term is provided
        filtered_prospects = df_final_result_leads

    # Filter prospect based on selected states
    if selected_is_contacted:
        filtered_prospects = filtered_prospects[
            filtered_prospects["status"].isin(selected_is_contacted)
        ]

    if selected_sales:
        filtered_prospects = filtered_prospects[
            filtered_prospects["attributed_sale"].isin(selected_sales)
        ]
    if selected_past_interactions == "Oui":
        filtered_prospects = filtered_prospects[
            ~filtered_prospects["status"].isna()
            | ~filtered_prospects["attributed_sale"].isna()
            | ~filtered_prospects["Notes"].isna()
        ]
    # Create prospect cards with an 'Overview' button
    prospect_cards_none = []
    prospect_cards_flex = []
    for client, nb_offer, website_url, attributed_sale, status in zip(
        df_final_result_leads["Entreprise"],
        df_final_result_leads["Nombre d'offres postés les 10 derniers jours"],
        df_final_result_leads["website_url"],
        df_final_result_leads["attributed_sale"],
        df_final_result_leads["status"],
    ):
        if client not in list(filtered_prospects["Entreprise"]):
            display = "none"
            component_card_section = component_card.component_card_function(
                client, nb_offer, website_url, attributed_sale, status, display
            )
            prospect_cards_none.append(component_card_section)
        else:
            display = "flex"
            component_card_section = component_card.component_card_function(
                client, nb_offer, website_url, attributed_sale, status, display
            )
            prospect_cards_flex.append(component_card_section)
        prospect_cards = prospect_cards_flex + prospect_cards_none
    return prospect_cards


layout = html.Div(
    [
        html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(
                                "Plateforme de prospection pour Kara",
                                style={
                                    "color": "#EEEEEE",
                                    "font-weight": "400",
                                    "text-shadow": "0px 0px 1px #000000",
                                },
                            ),
                            html.H3(
                                "Votre liste de leads générée par l'intelligence artificielle",
                                style={
                                    "color": "#EEEEEE",
                                    "font-weight": "400",
                                    "font-style": "italic",
                                    "text-shadow": "0px 0px 1px #000000",
                                },
                            ),
                        ]
                    ),
                    search_bar.search_bar,
                ],
                style={
                    "max-width": "1920px",
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "space-evenly",
                    "width": "100%",
                    "align-self": "center",
                    "height": "100%",
                },
            ),
            style={
                "height": "500px",
                "background-image": "url('../assets/kara_banniere.jpg')",
                "background-size": "cover",
                "display": "flex",
                "justify-content": "center",
                "padding": "20px",
                "padding-top": "300px",
            },
        ),
        html.Div(
            [
                # update_button.update_button,
                add_contact.modal_new_contact,
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H5("Filtres"),
                                        html.I(className="bi bi-funnel"),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flex-direction": "row",
                                        "gap": "8px",
                                        "align-items": "baseline",
                                    },
                                ),
                                filter_status.attributed_status_dropdown,
                                filter_sales.attributed_sale_dropdown,
                                filter_past_interactions.past_interactions_dropdown,
                            ],
                            style={
                                "flex-basis": "400px",
                                "display": "flex",
                                "flex-direction": "column",
                                "gap": "16px",
                            },
                        ),
                        html.Div(
                            id="leads-list",
                            style={
                                "flex-grow": "1",
                                "display": "flex",
                                "flex-direction": "column",
                                "gap": "20px",
                            },
                        ),
                    ],
                    style={"display": "flex", "flex-direction": "row", "gap": "20px"},
                ),
                # html.Button("Update", id="update-button", n_clicks=0),
                html.Div(
                    [
                        #        html.Div(
                        #            [
                        #                html.Div(
                        #                    [html.H5("Filters"), html.I(className="bi bi-funnel")],
                        #                    style={
                        #                        "display": "flex",
                        #                        "flex-direction": "row",
                        #                        "gap": "8px",
                        #                        "align-items": "baseline",
                        #                    },
                        #                ),
                        #                food_provider_dropdown,
                        #                state_dropdown,
                        #                segment_dropdown,
                        #            ],
                        #            style={"flex-basis": "400px", "display": "flex", "flex-direction": "column", "gap": "16px"},
                        #        ),
                    ],
                    style={"display": "flex", "flex-direction": "row", "gap": "20px"},
                ),
            ],
            style={
                "display": "flex",
                "flex-direction": "column",
                "gap": "10px",
                "padding": "50px 40px",
                "max-width": "1920px",
                "align-self": "center",
                "width": "100%",
                "padding": "20px",
            },
        ),
        html.Div(
            id="update-output",
            style={
                "flex-grow": "1",
                "display": "flex",
                "flex-direction": "column",
                "gap": "20px",
            },
        ),
        # html.Div(id="container-for-badges"),
    ],
    style={
        "display": "flex",
        "flex-direction": "column",
        "background-color": "#FFFFFF",
    },
)
