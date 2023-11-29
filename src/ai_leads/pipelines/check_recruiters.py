import logging
import pandas as pd
from ai_leads.Config.param import DATA_RECRUITING_PATH, LEAD_FILE_PATH
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter

# Setup logging
logger = logging.getLogger(__name__)

df_leads = pd.read_csv(LEAD_FILE_PATH, sep=",", dtype=str)
company_list = df_leads["Entreprise"].to_list()
id_list = df_leads["company_id"].to_list()

dfConverter = LeadDataFrameConverter(df_leads)

with open(DATA_RECRUITING_PATH, "r") as file:
    recruiting_company_list = file.readlines()
recruiting_company_list = [company[:-1] for company in recruiting_company_list]

for id, company in zip(id_list, company_list):
    company = str(company).lower().strip()
    logger.info("%s, %s", id, company)
    if company in recruiting_company_list:
        pass
    else:
        is_recruiting_company = dfConverter.verif_recruitment(company)
        print(is_recruiting_company)
        if is_recruiting_company:
            recruiting_company_list.append(company)
            with open(DATA_RECRUITING_PATH, "a") as file:
                file.write(company + "\n")
