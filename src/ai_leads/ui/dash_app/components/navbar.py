# Import necessary libraries
import dash_bootstrap_components as dbc
from dash import html

navbar = html.Div(
    [
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.Row(
                        # This column contains the Sodexo logo
                        dbc.Col(
                            html.A(
                                html.Img(
                                    src="../assets/Kara_Logo.png",
                                    height="40",  # Adjust size as needed
                                    className="my-auto",
                                ),
                                href="/",
                            ),
                            width="auto",  # Let the column size automatically
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                                "column-gap": "15px",
                                "align-items": "end",
                            },
                        ),
                        className="g-0",  # 'g-0' to remove the default gutters from the row
                        align="center",
                    ),
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                    dbc.Nav(
                        [
                            dbc.NavItem(
                                dbc.NavLink(
                                    "Prospect List",
                                    href="/prospect_list",
                                    id="page-1",
                                    style={"color": "black"},
                                    className="nav-item",
                                )  # Change text color to black
                            ),
                            dbc.NavItem(
                                dbc.NavLink(
                                    "Prospect Detail",
                                    href="/prospect_detail",
                                    id="page-2",
                                    style={"color": "black"},
                                )  # Change text color to black
                            ),
                        ],
                        pills=True,
                        fill=True,
                        style={"display": "flex", "flex-direction": "row", "gap": "8px", "visibility": "hidden"},
                    ),
                ]
            ),
            color="white",
            dark=True,
            fixed="top",
            className="shadow-sm",  # Adds a small shadow to the navbar for depth
            style={"padding": "12px"},
        )
    ]
)
