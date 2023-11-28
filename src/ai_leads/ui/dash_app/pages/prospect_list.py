import os

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import html
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components import search_bar, update_button

# Data
DATA_PATH = "data/"
df_final_result_leads = pd.read_csv(os.path.join(DATA_PATH, "leads_tests_bis.csv"), sep=",")
# df_final_result_uni["segment"] = "university"
df_final_result_leads.replace("n.a.", np.nan, inplace=True)
df_final_result_leads.dropna(subset=["Entreprise"], inplace=True)
"""# Get unique food segments
unique_segments = df_final_result_leads["segment"].unique().tolist()
# Create a Dropdown component for selecting food providers
segment_dropdown = dcc.Dropdown(
    id="segment-dropdown",
    options=[{"label": segment, "value": segment} for segment in unique_segments if not pd.isna(segment)],
    multi=True,  # Allow multiple selections
    placeholder="Select Segment",
    style={"border-color": "#ECECEC"},
)"""

"""# Get unique food providers
unique_food_providers = df_final_result_leads["foodProviderLLM"].unique().tolist()
# Create a Dropdown component for selecting food providers
food_provider_dropdown = dcc.Dropdown(
    id="food-provider-dropdown",
    options=[{"label": provider, "value": provider} for provider in unique_food_providers if not pd.isna(provider)],
    multi=True,  # Allow multiple selections
    placeholder="Select Food Providers",
    style={"border-color": "#ECECEC"},
)"""


"""# Option List for the dropdown filter for states
state_options = [{"label": name, "value": abbreviation} for abbreviation, name in state_data.items()]
state_dropdown = dcc.Dropdown(
    id="state-dropdown",
    options=state_options,
    multi=True,  # Allow multiple selections
    placeholder="Select States",
    style={"border-color": "#ECECEC"},
)"""


@app.callback(
    Output("update-output", "children"),  # Update this if needed
    Input("update-button", "n_clicks"),
    State({"type": "contacted-output", "index": ALL}, "value"),
)
def update_dataframe(n_clicks, checkbox_states):
    if n_clicks is None or n_clicks < 1:
        raise PreventUpdate
    for company_id, state in zip(df_final_result_leads["company_id"], checkbox_states):
        df_final_result_leads.loc[df_final_result_leads["company_id"] == company_id, "Contacté"] = (
            "Oui" if state else "Non"
        )

    # Save the updated DataFrame
    df_final_result_leads.to_csv(os.path.join(DATA_PATH, "leads_tests_bis.csv"), sep=",", index=False)

    return "Dataframe Updated!"


@app.callback(
    Output("university-list", "children"),
    State("search-input", "value"),
    # Input("food-provider-dropdown", "value"),
    # Input("state-dropdown", "value"),
    # Input("segment-dropdown", "value"),
    Input("search-button", "n_clicks"),
    Input("search-input", "n_submit"),
)
def update_prospect_list(
    search_term="",
    n_clicks_search_button=0,
    n_submit_search_input=0,
):
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

    # Create prospect cards with an 'Overview' button
    prospect_cards = []
    for id, client, nb_offer, already_contacted in zip(
        filtered_prospects["company_id"],
        filtered_prospects["Entreprise"],
        filtered_prospects["Nombre d'offres postés les 10 derniers jours"],
        filtered_prospects["Contacté"],
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
                                    html.H4(client.title()),
                                    dbc.Button(
                                        [html.Img(src="../assets/svg/eye.svg"), "Détail"],
                                        href=f"/list_offers/{id}",
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
                                id={"type": "contacted-output", "index": id},  # Ensure this matches the company_id
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
                        html.Div(
                            id="university-list",
                            style={"flex-grow": "1", "display": "flex", "flex-direction": "column", "gap": "20px"},
                        ),
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


# dbc.Container(
#     [
#         dbc.Row(
#             [
#                 dbc.Col(search_bar.search_bar, md={"size": 6, "offset": 0}),  # Modifié l'offset à 0
#                 dbc.Col(
#                     [
#                         dbc.Row(
#                             dbc.Col(export_button.export_button, className="text-right mt-4"), justify="end"
#                         ),  # Utilisation de justify="end" pour aligner le bouton à droite et ajout de mt-4 pour une plus grande marge supérieure
#                     ],
#                     md={"size": 6, "offset": 0},  # Modifié la largeur à 6
#                 ),
#             ]
#         ),
#         dbc.Row(
#             [
#                 dbc.Col(  # Colonne pour les filtres
#                     [
#                         html.Br(),
#                         food_provider_dropdown,
#                         html.Br(),  # Ajouter une petite marge verticale si nécessaire
#                         state_dropdown,
#                         html.Br(),  # Ajouter une petite marge verticale si nécessaire
#                         segment_dropdown,
#                     ],
#                     width=3,  # La largeur peut être ajustée selon le besoin
#                 ),
#                 dbc.Col(  # Colonne pour la liste des universités
#                     html.Div(id="university-list"), width=9  # La largeur peut être ajustée selon le besoin
#                 ),
#             ]
#         ),
#     ],
#     fluid=True,
# )
