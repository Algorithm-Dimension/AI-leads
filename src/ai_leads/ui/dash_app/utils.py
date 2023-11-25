import pandas as pd
import os
import numpy as np

# Data
DATA_PATH = "data/"
df_final_result_leads = pd.read_csv(os.path.join(DATA_PATH, "leads_tests.csv"), sep=",")
# df_final_result_uni["segment"] = "university"
df_final_result_leads.fillna(np.nan, inplace=True)
df_final_result_leads["company_id"] = df_final_result_leads["company_id"].astype(str)


def extract_client_name(path: str) -> str:
    id = path[len("/list_offers/") :]
    df_final_result_leads[df_final_result_leads["company_id"] == str(id)]
    company = df_final_result_leads[df_final_result_leads["company_id"] == str(id)]["Entreprise"].iloc[0]
    return company
