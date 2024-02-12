import dash_bootstrap_components as dbc
from dash import html

from ai_leads.ui.dash_app.app import app

# Définition du style pour la barre de recherche pour qu'elle ressemble à celle de l'image
search_bar_style = {
    "position": "relative",
    "margin-top": "20px",  # Ajustez en fonction de votre en-tête
    "margin-bottom": "20px",  # Ajustez en fonction de votre en-tête
}
# Création de la barre de recherche
search_bar = html.Div(
    dbc.InputGroup(
        [
            dbc.Input(
                id="search-input",
                type="text",
                placeholder="Recherchez un prospect",
                className="form-control-lg",  # Augmente la taille de l'entrée
            ),
            dbc.Button(
                html.I(className="bi bi-search"),  # Icône de recherche FontAwesome
                color="primary",
                className="btn-lg",
                id="search-button",
            ),
        ],
        size="lg",  # Définir la taille du InputGroup à large
        style={"border-radius": "100px"},
    )
)
