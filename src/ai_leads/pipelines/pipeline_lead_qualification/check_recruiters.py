import logging
import pandas as pd
from ai_leads.Config.param import DATA_RECRUITING_PATH, DATA_NON_RECRUITING_PATH, JOB_FILE_PATH
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter

# Setup logging
logger = logging.getLogger(__name__)

df_jobs = pd.read_csv(JOB_FILE_PATH, sep=";", dtype=str)
company_list = list(df_jobs["company"].unique())

dfConverter = LeadDataFrameConverter(df_jobs)

with open(DATA_RECRUITING_PATH, "r") as file:
    recruiting_company_list = file.readlines()
recruiting_company_list = [company[:-1] for company in recruiting_company_list]

with open(DATA_NON_RECRUITING_PATH, "r") as file:
    non_recruiting_company_list = file.readlines()
non_recruiting_company_list = [company[:-1] for company in non_recruiting_company_list]

for company in company_list:
    company = str(company).lower().strip()
    logger.info("%s", company)
    if company in recruiting_company_list or company in non_recruiting_company_list:
        pass
    else:
        is_recruiting_company = dfConverter.verif_recruitment(company)
        if is_recruiting_company:
            recruiting_company_list.append(company)
            with open(DATA_RECRUITING_PATH, "a") as file:
                file.write(company + "\n")
        else:
            non_recruiting_company_list.append(company)
            with open(DATA_NON_RECRUITING_PATH, "a") as file:
                file.write(company + "\n")
