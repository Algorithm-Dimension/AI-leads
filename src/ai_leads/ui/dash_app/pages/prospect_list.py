import os

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from unidecode import unidecode

from ai_leads.Config.param import JOB_FILE_PATH, LEAD_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components import search_bar, update_button

# Data
DATA_PATH = "data/"
df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=",")
df_final_result_leads.replace("n.a.", np.nan, inplace=True)
df_final_result_leads.dropna(subset=["Entreprise"], inplace=True)

unique_is_contacted = ["Oui", "Non"]
# Create a Dropdown component for selecting contact status
global contact_dropdown
contact_dropdown = dcc.Dropdown(
    id="contact-dropdown",
    options=[
        {"label": is_contacted, "value": is_contacted}
        for is_contacted in unique_is_contacted
        if not pd.isna(is_contacted)
    ],
    multi=True,  # Allow multiple selections
    placeholder="Contacté",
    style={"border-color": "#ECECEC"},
)


@app.callback(
    Output("update-output", "children"),  # Update this if needed
    Input("update-button", "n_clicks"),
    State({"type": "contacted-output", "index": ALL}, "value"),
)
def update_dataframe(n_clicks, checkbox_states):
    if n_clicks is None or n_clicks < 1:
        raise PreventUpdate
    for company, state in zip(df_final_result_leads["Entreprise"], checkbox_states):
        df_final_result_leads.loc[
            df_final_result_leads["Entreprise"].apply(lambda x: unidecode(x)) == unidecode(company), "Contacté"
        ] = ("Oui" if state else "Non")

    # Save the updated DataFrame
    df_final_result_leads.to_csv(os.path.join(LEAD_FILE_PATH), sep=",", index=False)

    return


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
    df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=",")
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
    """
    # Filter prospect based on selected food providers
    if selected_food_providers:
        filtered_prospects = filtered_prospects[filtered_prospects["foodProviderLLM"].isin(selected_food_providers)]"""

    """
    # Filter prospect based on selected states
    if selected_states:
        filtered_prospects = filtered_prospects[filtered_prospects["state"].isin(selected_states)]"""

    """
    # Filter prospect based on selected states
    if selected_segments:
        filtered_prospects = filtered_prospects[filtered_prospects["segment"].isin(selected_segments)]"""

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
                # [
                # dbc.CardHeader(
                #         html.Strong(client, style={"color": "#343a40"}),  # Couleur de texte personnalisée
                #         style={"backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6"},  # En-tête stylisé
                #     ),
                #     dbc.CardBody(
                #         [
                #             html.P(f"{city} - {state}", className="text-muted"),  # Classe de texte personnalisée
                #             html.P(food_provider_text, style=food_provider_style),
                #             dbc.Button(
                #                 [
                #                     "Overview ",  # Espace ajouté avant l'icône pour une meilleure esthétique
                #                 ],
                #                 href=f"/prospect_detail/{segment}_id_{id}",
                #                 style={
                #                     "backgroundColor": "#2255c5",  # Couleur de fond personnalisée
                #                     "color": "white",
                #                     "border": "none",
                #                     "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)",  # Ombre portée
                #                     "transition": "0.3s",  # Animation de transition
                #                 },
                #                 className="my-2",  # Marges personnalisées (classe Bootstrap)
                #             ),
                #         ],
                #         style={"padding": "20px"},  # Padding personnalisé
                #     )],
                [
                    # html.Img(src=f"../assets/svg/{segment}.svg", style={"width": "auto", "height": "50px"}),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dbc.Col(
                                        html.A(
                                            client.title(),
                                            href=website_url,
                                        ),
                                        style={
                                            "text-decoration": "underline",
                                            "cursor": "pointer",
                                            "font-weight": "bold",
                                            "font-size": "16px",
                                        },
                                    ),
                                    dbc.Button(
                                        [html.Img(src="../assets/svg/eye.svg"), "Détail"],
                                        href=f"/list_offers/{unidecode(client).replace(' ', '')}",
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
                            html.P("Denière mise à jour: 13/11/2023", style={"margin": "0"}),
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
                                "Plateforme de leads pour Kara",
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
                "height": "400px",
                "background-image": "url('../assets/hero4.jpg')",
                "background-size": "cover",
                "display": "flex",
                "justify-content": "center",
                "padding": "20px",
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
