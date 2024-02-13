import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate

# Assurez-vous que les chemins suivants sont correctement définis dans votre module de configuration
from ai_leads.Config.param import COMPANY_FILE_PATH, LEAD_FILE_PATH, CompanyActivity
from ai_leads.ui.dash_app.app import app  # Assurez-vous que 'app' est bien initialisé dans ce module

# Formulaire pour entrer une nouvelle entreprise


company_input = dbc.Row(
    [
        dbc.Col(dbc.Label("Entreprise", width="auto"), width=2),
        dbc.Col(
            dbc.Input(type="text", id="new-company-input", placeholder=""),
            className="me-3",
        ),
    ],
    className="mb-3",
    align="center",
)

url_input = dbc.Row(
    [
        dbc.Col(dbc.Label("Page Web", width="auto"), width=2),
        dbc.Col(
            dbc.Input(type="text", id="new-url-input", placeholder=""),
            className="me-3",
        ),
    ],
    className="mb-3",
    align="center",
)

activity_sector = dbc.Row(
    [
        dbc.Col(dbc.Label("Secteur d'activité", width="auto"), width=2),
        dbc.Col(
            dbc.RadioItems(
                id="new-activity-sector-input",
                options=[
                    {"label": "Recrutement", "value": CompanyActivity.RECRUITING.value, "disabled": True},
                    {"label": "Formation / Éducation", "value": CompanyActivity.FORMATION_ECOLE.value},
                    {"label": "Autre", "value": CompanyActivity.OTHER.value},
                ],
            )
        ),
    ],
    className="mb-3",
    align="center",
)

form = dbc.Form([company_input, url_input, activity_sector])

# Modal pour ajouter un nouveau contact
modal_new_contact = html.Div(
    [
        dbc.Button("Ajouter un nouveau prospect", id="open-new-contact-box", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Nouveau prospect")),
                dbc.ModalBody(form),
                dbc.ModalFooter(dbc.Button("Soumettre", id="submit-new-contact", className="ms-auto", n_clicks=0)),
            ],
            id="modal_new_contact",
            is_open=False,
        ),
        html.Div(id="update-output-new-contact"),  # Ajout pour l'affichage des résultats
    ]
)


# Callback pour ouvrir/fermer le modal
@app.callback(
    Output("modal_new_contact", "is_open"),
    [Input("open-new-contact-box", "n_clicks"), Input("submit-new-contact", "n_clicks")],
    [State("modal_new_contact", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Callback pour ajouter un nouveau contact et mettre à jour les données
@app.callback(
    Output("update-output-new-contact", "children"),
    [Input("submit-new-contact", "n_clicks")],
    [
        State("new-company-input", "value"),
        State("new-url-input", "value"),
        State("new-activity-sector-input", "value"),
    ],
    prevent_initial_call=True,  # Empêche l'exécution initiale lors du chargement de la page
)
def add_new_contact_to_dataframe(n_clicks, new_company, new_url, new_activity_sector):
    if not new_company:  # Vérifie si le champ est vide
        raise PreventUpdate

    # Lecture des DataFrames existants
    df_final_result_leads = pd.read_csv(LEAD_FILE_PATH, sep=";", dtype=str)
    df_table_company = pd.read_csv(COMPANY_FILE_PATH, sep=";", dtype=str)

    # Mise à jour des DataFrames
    df_table_company, df_final_result_leads = add_unique(
        df_table_company, df_final_result_leads, new_company, new_url, new_activity_sector
    )

    # Sauvegarde des DataFrames mis à jour
    df_final_result_leads.to_csv(LEAD_FILE_PATH, sep=";", index=False)
    df_table_company.to_csv(COMPANY_FILE_PATH, sep=";", index=False)


def add_unique(
    df_company: pd.DataFrame,
    df_leads: pd.DataFrame,
    company: str = np.nan,
    url: str = np.nan,
    activity_sector: str = np.nan,
):
    # Vérifie si l'entreprise n'existe pas déjà dans df_company
    if company not in df_company["company"].values:
        new_row_company = pd.DataFrame(
            {"company": [company], "website_url": [url], "activity_sector": [activity_sector]}, index=[len(df_company)]
        )
        df_company = pd.concat([df_company, new_row_company], ignore_index=True)

    # Vérifie si l'entreprise n'existe pas déjà dans df_leads
    if company not in df_leads["Entreprise"].values:
        new_row_leads = pd.DataFrame(
            {"Entreprise": [company], "website_url": [url], "activity_sector": [activity_sector]}, index=[len(df_leads)]
        )
        df_leads = pd.concat([df_leads, new_row_leads], ignore_index=True)

    return df_company, df_leads
