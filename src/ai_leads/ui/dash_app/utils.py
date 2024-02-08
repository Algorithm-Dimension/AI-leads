import os

import numpy as np
import pandas as pd
from unidecode import unidecode

from ai_leads.Config.param import LEAD_FILE_PATH

# Data
DATA_PATH = "data/"
df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=";")
# df_final_result_uni["segment"] = "university"
df_final_result_leads.fillna(np.nan, inplace=True)
df_final_result_leads["Entreprise"] = df_final_result_leads["Entreprise"].astype(str)


def extract_client_name(path: str) -> str:
    unidecoded_company = path[len("/list_offers/") :]
    company = df_final_result_leads[
        df_final_result_leads["Entreprise"].apply(lambda x: unidecode(x).replace(" ", "")) == unidecoded_company
    ]["Entreprise"].iloc[0]
    return company


def sort_df_by_date(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Function which sort a dataframe by date: from the most to the least recent. string values are the last
    df: pd.DataFrame
    date_col: nale of the column with the date
    """
    df["offer_date_converted"] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    # Crée une colonne temporaire pour identifier les lignes avec des chaînes de caractères
    df["is_string"] = df["offer_date_converted"].isna()

    # Trie le DataFrame :
    # 1. Les dates en ordre décroissant.
    # 2. Les chaînes de caractères (is_string=True) à la fin.
    df_sorted = df.sort_values(by=["is_string", "offer_date_converted"], ascending=[True, False])
    # Supprime la colonne 'is_string' et 'offer_date_converted'
    df_sorted.drop(["is_string", "offer_date_converted"], axis=1, inplace=True)
    return df_sorted
