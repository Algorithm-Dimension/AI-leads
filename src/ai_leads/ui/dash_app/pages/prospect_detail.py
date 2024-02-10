# -*- coding: utf-8 -*-

import os
from typing import List

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State

from ai_leads.Config.param import JOB_FILE_PATH, LEAD_FILE_PATH, CONTACT_FILE_PATH
from ai_leads.ui.dash_app.app import app
from ai_leads.ui.dash_app.components.header import header_prospect_detail
from ai_leads import utils
from ai_leads.ui.dash_app.utils import sort_df_by_date

df_jobs = pd.read_csv(os.path.join(JOB_FILE_PATH), sep=";", dtype=str)[
    ["job name", "company", "location", "offer date", "contact", "position", "source", "url"]
]
df_jobs.replace(["n.a.", "N.A."], np.nan, inplace=True)
df_jobs["company"] = df_jobs["company"].astype(str)
df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";", dtype=str)
df_final_result_leads.replace(["n.a.", "N.A."], np.nan, inplace=True)
df_final_result_leads.dropna(subset=["Entreprise"], inplace=True)

df_table_contact = pd.read_csv(os.path.join(CONTACT_FILE_PATH), sep=";", dtype=str)


# La fonction _create_job_div
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
    platform_html = html.Small(source_platform.title(), className="text-muted")  # Plateforme source

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


def job_list_output(company: str) -> List[dbc.Row]:
    """Function to create the list of job on the web app"""
    if utils.clean_str_unidecode(company) in list(df_jobs["company"].apply(utils.clean_str_unidecode)):
        rows = df_jobs.loc[df_jobs["company"].apply(utils.clean_str_unidecode) == utils.clean_str_unidecode(company)]
        # Apply the function to create HTML divs for each meal plan
        rows = sort_df_by_date(rows, "offer date")
        job_divs = rows.apply(_create_job_div, axis=1)
        return job_divs.tolist()
    return []


def linkedin_contact_output(company: str):
    if utils.clean_str_unidecode(company) in list(df_table_contact["company"].apply(utils.clean_str_unidecode)):
        contacts = df_table_contact.loc[
            df_table_contact["company"].apply(utils.clean_str_unidecode) == utils.clean_str_unidecode(company)
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


def create_contacts_section(company: str):
    contacts = linkedin_contact_output(company)
    if not contacts:
        return html.P("Aucun contact pertinent trouvé.")

    contacts_elements = []
    for contact in contacts:
        # Créer un hyperlien contenant le nom et le logo LinkedIn
        contact_link = html.A(
            [
                f"{contact['first_name']} {contact['last_name']}",  # Nom et prénom
                html.Img(
                    src="../assets/LinkedIn_logo_initials.png", style={"height": "1.5rem", "marginLeft": "10px"}
                ),  # Logo LinkedIn
            ],
            href=contact["linkedin_url"],
            target="_blank",
            style={"textDecoration": "none", "color": "black", "display": "flex", "alignItems": "center"},
        )

        contact_element = dbc.Row(
            [
                dbc.Col(contact_link),
            ],
            className="mb-2",
        )
        contacts_elements.append(contact_element)

    return dbc.Card(
        [
            dbc.CardHeader("Contacts potentiellement pertinents"),
            dbc.CardBody(contacts_elements),
        ],
        className="mb-3",
    )

    return dbc.Card(
        [
            dbc.CardHeader("Contacts potentiellement pertinents"),
            dbc.CardBody(contacts_elements),
        ],
        className="mb-3",
    )


def job_info(company: str) -> dbc.Row:
    layout = dbc.Row(
        dbc.Card(
            [
                html.H4(f"Liste d'offres d'emploi postées par : {company.title()}", className="ms-3 my-3 text-muted"),
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
                            style={"border-bottom": "1px solid #ccc"},  # Add this line for border style
                        )
                    ]
                    + [html.P(job_item, className="card-text") for job_item in job_list_output(company)]
                ),
            ],
            className="mb-3 border-0 shadow px-5 py-2",  # Appliquez 'border-0' ici pour enlever les bords.
            style={"backgroundColor": "white"},  # Gardez le fond en blanc.
        ),
    )
    return [layout]


@app.callback(
    Output("personal-notes", "value"),
    Input("save-button", "n_clicks"),
    State("personal-notes", "value"),
    State("company-name-store", "data"),
)
def save_personal_notes(n_clicks, notes, company):
    if n_clicks:
        df_final_result_leads.loc[
            df_final_result_leads["Entreprise"].str.lower().str.strip() == company.lower().strip(), "Notes"
        ] = notes
        # Save the updated DataFrame
        df_final_result_leads.to_csv(os.path.join(LEAD_FILE_PATH), sep=";", index=False)
        return no_update
    return no_update


def layout_function(company):
    # Utilisez dbc.Row ou dbc.Col pour créer des espaces gris clair entre les sections
    section_spacing_style = {"paddingTop": "0.5rem", "paddingBottom": "0.5rem"}  # Ajustez les valeurs selon les besoins
    bg_color = "#F7F7F7"  # Couleur de fond gris clair, correspond à la classe bg-light de Bootstrap

    # Obtenir la valeur de la colonne "Notes" pour la ligne correspondante
    notes_default_value = df_final_result_leads.loc[df_final_result_leads["Entreprise"] == company, "Notes"].values[0]

    layout = html.Div(
        children=[
            dbc.Container(
                [
                    html.Br(),
                    # En-tête de la page
                    dbc.Row(
                        dbc.Col(header_prospect_detail(company.title(), "", "", ""), width=12),
                        style={"paddingBottom": "1rem", "backgroundColor": bg_color},
                    ),
                    dbc.Row(
                        dbc.Col(create_contacts_section(company), width=12),
                        style={"paddingBottom": "1rem", "backgroundColor": bg_color},
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("Notes Personnelles", className="card-title"),
                                        dcc.Textarea(
                                            id="personal-notes",
                                            value=notes_default_value,  # Valeur par défaut de la zone de texte
                                            style={
                                                "width": "100%",
                                                "height": "200px",
                                            },  # Ajustez la taille selon vos préférences
                                        ),
                                        dbc.Button(
                                            "Sauvegarder",
                                            id="save-button",
                                            color="primary",  # Couleur du bouton
                                            className="mt-3",  # Marge supérieure pour l'espacement
                                        ),
                                    ]
                                ),
                                className="mb-3 border-0 shadow",  # Appliquez la classe card à la carte
                                style={"backgroundColor": "white"},  # Gardez le fond en blanc.
                            ),
                            width=12,
                        ),
                        style={**section_spacing_style, "backgroundColor": bg_color},
                    ),
                    dbc.Row(
                        dbc.Col(job_info(company), width=12),
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
