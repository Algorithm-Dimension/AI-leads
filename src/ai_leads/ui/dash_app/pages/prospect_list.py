import os
from typing import List, Optional

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from ai_leads import utils

# Local application imports
from ai_leads.Config.param import LAST_UPDATE, LEAD_FILE_PATH

from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components import search_bar, update_button

# Constants
BASE_DATE_STR = LAST_UPDATE.strftime("%d/%m/%y")
DATA_PATH = "data/"

# Read and preprocess the data
df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";")
df_final_result_leads.replace("n.a.", np.nan, inplace=True)
df_final_result_leads.dropna(subset=["Entreprise"], inplace=True)

# Dropdown options based on unique contact statuses
unique_is_contacted = df_final_result_leads["Contacté"].unique().tolist()

# Dropdown component for selecting contact status
contact_dropdown = dcc.Dropdown(
    id="contact-dropdown",
    options=[{"label": status, "value": status} for status in unique_is_contacted if pd.notna(status)],
    multi=True,
    placeholder="Contacté",
    style={"border-color": "#ECECEC"},
)


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
            df_final_result_leads["Entreprise"].apply(utils.clean_str_unidecode) == normalized_company, "Contacté"
        ] = ("Oui" if state else "Non")

    # Save the updated DataFrame
    df_final_result_leads.to_csv(os.path.join(LEAD_FILE_PATH), sep=";", index=False)


@app.callback(
    Output("university-list", "children"),
    State("search-input", "value"),
    Input("contact-dropdown", "value"),
    # Input("state-dropdown", "value"),
    # Input("segment-dropdown", "value"),
    Input("search-button", "n_clicks"),
    Input("search-input", "n_submit"),
)
def update_prospect_list(
    search_term="",
    selected_is_contacted=None,
    n_clicks_search_button=0,
    n_submit_search_input=0,
):
    df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";")
    # Get unique food providers
    unique_is_contacted = df_final_result_leads["Contacté"].unique().tolist()
    # Create a Dropdown component for selecting food providers
    global contact_dropdown
    contact_dropdown = dcc.Dropdown(
        id="contact-dropdown",
        options=[
            {"label": is_contacted, "value": is_contacted}
            for is_contacted in unique_is_contacted
            if not pd.isna(is_contacted)
        ],
        multi=True,  # Allow multiple selections
        placeholder="Sélectionnez le statut",
        style={"border-color": "#ECECEC"},
    )
    if search_term:
        # Filter based on the search term
        filtered_prospects = df_final_result_leads.loc[
            df_final_result_leads["Entreprise"].str.lower().str.contains(search_term.lower())
        ]
    else:
        # Select all prospects if no search term is provided
        filtered_prospects = df_final_result_leads

    # Filter prospect based on selected states
    if selected_is_contacted:
        filtered_prospects = filtered_prospects[filtered_prospects["Contacté"].isin(selected_is_contacted)]

    # Create prospect cards with an 'Overview' button
    prospect_cards = []
    for client, nb_offer, already_contacted, website_url in zip(
        filtered_prospects["Entreprise"],
        filtered_prospects["Nombre d'offres postés les 10 derniers jours"],
        filtered_prospects["Contacté"],
        filtered_prospects["website_url"],
    ):
        contacted_checked = already_contacted == "Oui"
        prospect_cards.append(
            dbc.Card(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    dbc.Row(
                                        dbc.Col(
                                            html.A(
                                                client.title(),
                                                href=website_url,
                                                style={
                                                    "color": "blue",
                                                    "text-decoration": "underline",
                                                    "cursor": "pointer",
                                                    "font-weight": "bold",
                                                    "font-size": "16px",
                                                },
                                            ),
                                        )
                                    ),
                                    dbc.Button(
                                        [html.Img(src="../assets/svg/eye.svg"), "Détail"],
                                        href=f"/list_offers/{utils.clean_str_unidecode(client).replace(' ', '')}",
                                        style={
                                            "display": "flex",
                                            "flex-direction": "row",
                                            "align-items": "center",
                                            "column-gap": "8px",
                                        },
                                    ),
                                ],
                                style={
                                    "justify-content": "space-between",
                                    "display": "flex",
                                    "flex-direction": "row",
                                    "align-items": "center",
                                },
                            ),
                            html.P(["Denière mise à jour: le ", BASE_DATE_STR], style={"margin": "0"}),
                            html.P(f"À : Paris", style={"margin": "0"}),
                            html.P(
                                f"Nombre d'offre postées les 10 derniers jours : {str(nb_offer)}", style={"margin": "0"}
                            ),
                            dbc.Checkbox(
                                id={"type": "contacted-output", "index": ""},
                                value=contacted_checked,
                                label="Déjà Contacté ?",
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flex-direction": "column",
                            "justify-content": "start",
                            "row-gap": "10px",
                            "flex-grow": "1",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flex-direction": "row",
                    "column-gap": "20px",
                    "borderRadius": "15px",
                    "border-color": "#B71515",
                    "boxShadow": "0 6px 20px 0 #0D234F14",
                    "padding": "24px",
                },  # Style de carte global
            )
        )

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
                                style={"color": "#EEEEEE", "font-weight": "400", "text-shadow": "0px 0px 1px #000000"},
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
                update_button.update_button,
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H5("Filtres"), html.I(className="bi bi-funnel")],
                                    style={
                                        "display": "flex",
                                        "flex-direction": "row",
                                        "gap": "8px",
                                        "align-items": "baseline",
                                    },
                                ),
                                contact_dropdown,
                            ],
                            style={"flex-basis": "400px", "display": "flex", "flex-direction": "column", "gap": "16px"},
                        ),
                        html.Div(
                            id="university-list",
                            style={"flex-grow": "1", "display": "flex", "flex-direction": "column", "gap": "20px"},
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
            style={"flex-grow": "1", "display": "flex", "flex-direction": "column", "gap": "20px"},
        ),
    ],
    style={"display": "flex", "flex-direction": "column", "background-color": "#F7F7F7"},
)
