import os

import numpy as np
import pandas as pd
from unidecode import unidecode

from ai_leads.Config.param import LEAD_FILE_PATH

# Data
DATA_PATH = "data/"
df_final_result_leads = pd.read_csv(os.path.join(LEAD_FILE_PATH), sep=",")
# df_final_result_uni["segment"] = "university"
df_final_result_leads.fillna(np.nan, inplace=True)
df_final_result_leads["Entreprise"] = df_final_result_leads["Entreprise"].astype(str)


def extract_client_name(path: str) -> str:
    unidecoded_company = path[len("/list_offers/") :]
    company = df_final_result_leads[
        df_final_result_leads["Entreprise"].apply(lambda x: unidecode(x).replace(" ", "")) == unidecoded_company
    ]["Entreprise"].iloc[0]
    return company
