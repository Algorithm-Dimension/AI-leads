import logging
import pandas as pd
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter
from ai_leads.Config.param import DATA_RECRUITING_PATH, LEAD_FILE_PATH

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


df_jobs = pd.read_csv("data/jobs_tests.csv", sep=";")
dfConverter = LeadDataFrameConverter(df_jobs)
df_leads = dfConverter.convert_to_lead_dataframe(time_window=10)
df_leads.reset_index(inplace=True)

with open(DATA_RECRUITING_PATH, "r") as file:
    recruiting_company_list = file.readlines()
recruiting_company_list = [company[:-1] for company in recruiting_company_list]

df_leads = df_leads.loc[~df_leads["Entreprise"].str.lower().str.strip().isin(recruiting_company_list)]
df_leads.to_csv(LEAD_FILE_PATH, sep=",", index=False)
