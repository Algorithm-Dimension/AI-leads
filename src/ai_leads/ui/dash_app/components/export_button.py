import base64
import os
from io import BytesIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html

# Données
DATA_PATH = "data"
df_final_result = pd.read_csv(os.path.join(DATA_PATH, "leads_tests.csv"), sep=";")


def generate_excel_download_link(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)

    output.seek(0)
    excel_data = output.read()
    excel_base64 = base64.b64encode(excel_data).decode("utf-8")
    href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64}"

    return href, f"Export"


excel_href, excel_download_button_text = generate_excel_download_link(df_final_result)

# Bouton Export


export_button = dbc.Button(
    [html.I(className="bi bi-download"), excel_download_button_text],
    id="export-button",
    href=excel_href,
    download="final_result_uni.xlsx",
    outline=True,
    color="primary",
    style={"width": "fit-content", "display": "flex", "flex-direction": "row", "gap": "8px", "align-self": "end"},
)
