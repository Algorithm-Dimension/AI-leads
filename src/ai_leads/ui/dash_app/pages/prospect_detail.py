import math
import os
from typing import List
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import ALL, Input, Output, State, dcc, html, no_update
from ai_leads import utils
from ai_leads.Config.param import CONTACT_FILE_PATH, JOB_FILE_PATH, LEAD_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components import modify_prospect_form
from ai_leads.ui.dash_app.components.header import header_prospect_detail
from ai_leads.ui.dash_app.Config.param import COLOR_DICT_JOB_BOARD_BADGES, JOBS_PER_PAGE
from ai_leads.ui.dash_app.utils import sort_df_by_date

# -*- coding: utf-8 -*-


# Importer les dépendances de Dash
# from dash.dependencies import ALL, Input, Output, State, callback_context, dcc, html, no_update

# Définir une liste vide pour stocker l'entreprise actuelle
CURRENT_COMPANY = []

# Charger les données à partir des fichiers CSV
df_jobs = pd.read_csv(os.path.join(JOB_FILE_PATH), sep=";", dtype=str)[
    ["job name", "company", "location", "offer date", "position", "source", "url"]
]
df_jobs.replace(["n.a.", "N.A."], np.nan, inplace=True)
df_jobs["company"] = df_jobs["company"].astype(str)

df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";", dtype=str)
df_final_result_leads.replace(["n.a.", "N.A."], np.nan, inplace=True)
df_final_result_leads.dropna(subset=["Entreprise"], inplace=True)

df_table_contact = pd.read_csv(os.path.join(CONTACT_FILE_PATH), sep=";", dtype=str)


# Fonction pour créer une div d'offre d'emploi
def _create_job_div(row):
    # Extraire les données de l'offre d'emploi à partir de la ligne
    position = row["job name"]
    location = row["location"]
    offer_date = row["offer date"]
    source_platform = row["source"]

    # Créer des composants HTML pour chaque partie de l'offre d'emploi
    position_html = html.H6(position.title(), className="mb-0")  # Nom du poste
    location_html = html.P(
        location,
        style={
            "background-color": "#EEFAFF",
            "width": "fit-content",
            "padding": "4px",
            "borderRadius": "4px",
            "color": "#0011CC",
        },
    )  # Informations sur l'emplacement
    offer_date_html = html.Small(offer_date, className="text-muted")  # Date de l'offre
    platform_html = html.A(
        dbc.Badge(
            source_platform.title(), color=COLOR_DICT_JOB_BOARD_BADGES[source_platform]
        ),
        className="text-muted",
    )  # Plateforme source

    # Compiler les composants dans une seule Div
    job_div = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(position_html, width=4),
                    dbc.Col(location_html, width=4),
                    dbc.Col(offer_date_html, width=2),
                    dbc.Col(platform_html, width=2),
                ],
                className="my-2",
                style={"border-bottom": "1px solid #ccc"},
            )
        ],
        className="p-2",
    )

    return job_div


# Fonction pour paginer un DataFrame
def paginate_dataframe(df: pd.DataFrame, page: int, page_size: int = JOBS_PER_PAGE):
    """Retourne une tranche du DataFrame correspondant au numéro de page."""
    start = (page - 1) * page_size
    end = start + page_size
    return df.iloc[start:end]


# Fonction pour rendre le composant de pagination
def render_pagination(total_pages: int, active_page: int):
    """Rendre le composant de pagination avec des boutons."""
    pagination_style = {
        "color": "#007BFF",
        "backgroundColor": "transparent",
        "borderColor": "#007BFF",
    }  # Exemple de couleur
    active_style = {
        "backgroundColor": "#007BFF",
        "borderColor": "#0056b3",
        "color": "white",
    }  # Exemple de couleur active

    return dbc.Pagination(
        max_value=total_pages,
        active_page=active_page,
        previous_next=True,
        fully_expanded=False,
        id="pagination",
    )


# Fonction pour créer la liste d'offres d'emploi pour une entreprise spécifique
def job_list_output(company: str, page: int) -> List[dbc.Row]:
    """Fonction pour créer la liste de divs d'offres d'emploi pour une page spécifique dans l'application web."""
    if utils.clean_str_unidecode(company) in list(
        df_jobs["company"].apply(utils.clean_str_unidecode)
    ):
        rows = df_jobs.loc[
            df_jobs["company"].apply(utils.clean_str_unidecode)
            == utils.clean_str_unidecode(company)
        ]
        # Trier par date et paginer
        sorted_rows = sort_df_by_date(rows, "offer date")
        page_rows = paginate_dataframe(sorted_rows, page)
        job_divs = page_rows.apply(_create_job_div, axis=1)
        return job_divs.tolist()
    return []


# Callback pour mettre à jour la liste d'offres d'emploi et la pagination
@app.callback(
    Output("job-list", "children"),
    Output("pagination", "active_page"),
    [Input("pagination", "active_page")],
    [State("company-name-store", "data")],
)
def update_page(active_page: int, company: str):
    # Déterminer le nouveau numéro de page à partir du composant de pagination
    if not active_page:
        active_page = 1

    # Obtenir la nouvelle page d'offres d'emploi
    job_divs = job_list_output(company, active_page)

    # Retourner les nouvelles divs d'offres d'emploi et la page actuelle
    return job_divs, active_page


# Fonction pour obtenir les contacts LinkedIn pour une entreprise spécifique
def linkedin_contact_output(company: str):
    if utils.clean_str_unidecode(company) in list(
        df_table_contact["company"].apply(utils.clean_str_unidecode)
    ):
        contacts = df_table_contact.loc[
            df_table_contact["company"].apply(utils.clean_str_unidecode)
            == utils.clean_str_unidecode(company)
        ]
        contacts_list = []
        for _, row in contacts.iterrows():
            if pd.notna(row["linkedin_url_1"]):
                contacts_list.append(
                    {
                        "first_name": row["firstName1"],
                        "last_name": row["lastName1"],
                        "linkedin_url": row["linkedin_url_1"],
                    }
                )
            if pd.notna(row["linkedin_url_2"]):
                contacts_list.append(
                    {
                        "first_name": row["firstName2"],
                        "last_name": row["lastName2"],
                        "linkedin_url": row["linkedin_url_2"],
                    }
                )
        return contacts_list
    return []


# Fonction pour créer la section des contacts LinkedIn
def create_contacts_section(company: str):
    contacts = linkedin_contact_output(company)
    if not contacts:
        return html.P("Aucun contact pertinent trouvé")

    contacts_elements = []
    for contact in contacts:
        # Créer un hyperlien contenant le nom et le logo LinkedIn
        contact_link = html.A(
            [
                f"{contact['first_name']} {contact['last_name']}",  # Nom et prénom
                html.Img(
                    src="../assets/LinkedIn_logo_initials.png",
                    style={"height": "1.5rem", "marginLeft": "10px"},
                ),  # Logo LinkedIn
            ],
            href=contact["linkedin_url"],
            target="_blank",
            style={
                "textDecoration": "none",
                "color": "black",
                "display": "flex",
                "alignItems": "center",
            },
        )

        contact_element = dbc.Row(
            [
                dbc.Col(contact_link, align="center"),
            ],
            align="center",
            className="mb-2",
        )
        contacts_elements.append(contact_element)

    return dbc.Card(
        [
            dbc.CardHeader("Profils Linkedin"),
            dbc.CardBody(contacts_elements),
        ],
    )


# Fonction pour créer la section d'informations sur les offres d'emploi
def job_info(company: str) -> dbc.Row:
    layout = dbc.Row(
        dbc.Card(
            [
                html.H4(
                    f"Liste d'offres d'emploi postées par : {company.title()}",
                    className="ms-3 my-3 text-muted",
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col("Poste", width=4),
                                dbc.Col("Localisation", width=4),
                                dbc.Col("Date", width=2),
                                dbc.Col("Job Board d'origine", width=2),
                            ],
                            className="p-2",
                            style={
                                "border-bottom": "1px solid #ccc"
                            },  # Ajouter cette ligne pour le style de la bordure
                        )
                    ]
                    + [
                        html.P(job_item, className="card-text")
                        for job_item in job_list_output(company)
                    ]
                ),
            ],
            className="mb-3 border-0 shadow px-5 py-2",  # Appliquer 'border-0' ici pour supprimer les bordures.
            style={"backgroundColor": "white"},  # Garder le fond en blanc.
        ),
    )
    return [layout]


# Callback pour sauvegarder les notes personnelles
@app.callback(
    Output("personal-notes", "value"),
    Input("save-button", "n_clicks"),
    State("personal-notes", "value"),
    State("company-name-store", "data"),
)
def save_personal_notes(n_clicks, notes, company):
    if n_clicks:
        df_final_result_leads.loc[
            df_final_result_leads["Entreprise"].str.lower().str.strip()
            == company.lower().strip(),
            "Notes",
        ] = notes
        # Sauvegarder le DataFrame mis à jour
        df_final_result_leads.to_csv(os.path.join(LEAD_FILE_PATH), sep=";", index=False)
        return no_update
    return no_update


# Callback pour afficher ou masquer la fenêtre modale
@app.callback(
    Output("modal", "is_open"),
    [Input("save-button", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Fonction pour créer la mise en page de la page de détails du prospect
def layout_function(company):
    # Utiliser dbc.Row ou dbc.Col pour créer des espaces gris clair entre les sections
    section_spacing_style = {
        "paddingTop": "0.5rem",
        "paddingBottom": "0.5rem",
    }  # Ajuster les valeurs selon les besoins
    bg_color = "#F7F7F7"  # Couleur de fond gris clair, correspond à la classe bg-light de Bootstrap

    # Obtenir la valeur de la colonne "Notes" pour la ligne correspondante
    notes_default_value = df_final_result_leads.loc[
        df_final_result_leads["Entreprise"] == company, "Notes"
    ].values[0]

    # Obtenir le nombre de pages
    total_jobs = len(
        df_jobs[
            df_jobs["company"].apply(utils.clean_str_unidecode)
            == utils.clean_str_unidecode(company)
        ]
    )
    total_pages = math.ceil(total_jobs / JOBS_PER_PAGE)

    # Composant de pagination en haut de la liste d'offres d'emploi
    pagination_component = render_pagination(total_pages, active_page=1)

    # Liste initiale d'offres d'emploi pour la première page
    initial_job_list = job_list_output(company, page=1)

    # Conteneur pour la liste d'offres d'emploi dynamique
    job_list_container = html.Div(id="job-list", children=initial_job_list)

    layout = html.Div(
        children=[
            dbc.Container(
                [
                    html.Br(),
                    # En-tête de la page
                    dbc.Row(
                        dbc.Col(header_prospect_detail(company.title()), width=12),
                        style={
                            "paddingBottom": "1rem",
                            "paddingLeft": "1rem",
                            "paddingRight": "1rem",
                            "backgroundColor": bg_color,
                        },
                    ),
                    dbc.Accordion(
                        dbc.AccordionItem(
                            [
                                modify_prospect_form.attributed_tag_input(company),
                                html.Div(
                                    id="output-attributed_sale"
                                    + "-"
                                    + utils.clean_str_unidecode(company)
                                ),
                                modify_prospect_form.status_tag_input(company),
                                html.Div(
                                    id="output-status"
                                    + "-"
                                    + utils.clean_str_unidecode(company)
                                ),
                            ],
                            title="Information de travail",
                        )
                    ),
                    dbc.Accordion(
                        dbc.AccordionItem(
                            [create_contacts_section(company)],
                            title="Contacts potentiellement pertinents",
                        )
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "Notes Personnelles", className="card-title"
                                        ),
                                        dcc.Textarea(
                                            id="personal-notes",
                                            value=notes_default_value,  # Valeur par défaut de la zone de texte
                                            style={
                                                "width": "100%",
                                                "height": "200px",
                                            },  # Ajuster la taille selon vos préférences
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Sauvegarder",
                                                    id="save-button",
                                                    color="primary",  # Couleur du bouton
                                                    className="mt-3",  # Marge supérieure pour l'espacement
                                                ),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalBody(
                                                            "Vos notes ont bien été sauvegardées"
                                                        ),
                                                        dbc.ModalFooter(
                                                            dbc.Button(
                                                                "Fermer",
                                                                id="close",
                                                                className="ms-auto",
                                                                n_clicks=0,
                                                            )
                                                        ),
                                                    ],
                                                    id="modal",
                                                    is_open=False,
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                                className="mb-3 border-0 shadow",  # Appliquer la classe card à la carte
                                style={
                                    "backgroundColor": "white"
                                },  # Garder le fond en blanc.
                            ),
                            width=12,
                        ),
                        style={**section_spacing_style, "backgroundColor": bg_color},
                    ),
                    # Ajouter le composant de pagination avant la liste d'offres d'emploi
                    dbc.Row(
                        dbc.Col(pagination_component, width=12),
                        style={**section_spacing_style, "backgroundColor": bg_color},
                    ),
                    # Ajouter le conteneur qui contiendra la liste d'offres d'emploi dynamique
                    dbc.Row(
                        dbc.Col(job_list_container, width=12),
                        style={**section_spacing_style, "backgroundColor": bg_color},
                    ),
                ],
                fluid=True,
                style={"maxWidth": "100%", "background-color": bg_color},
                className="px-5",
            ),
        ],
    )

    return layout
