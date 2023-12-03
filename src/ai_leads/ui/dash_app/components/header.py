import dash_bootstrap_components as dbc
from dash import html, dcc


# Page header
def header_prospect_detail(company: str, city: str, state: str, segment: str) -> dbc.Row:
    header_prospect_detail = dbc.Row(
        [
            dcc.Store(id="company-name-store", data=company),  # Add this line
            dbc.Col(
                [
                    html.H1(
                        f"{company}",
                        className="text-center my-3",
                        style={"color": "#444444", "font-weight": "400"},
                    ),
                ],
                width=12,
                style={
                    "justify-content": "center",
                    "padding": "20px",
                    "align-items": "center",
                    "display": "flex",
                    "flex-direction": "row",
                    "gap": "20px",
                },
            ),
        ],
        style={"backgroundColor": "white"},
        className="shadow",
    )
    return header_prospect_detail
