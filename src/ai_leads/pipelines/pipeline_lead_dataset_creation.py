import logging
import pandas as pd
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


df_jobs = pd.read_csv("data/jobs_tests.csv", sep=";")
dfConverter = LeadDataFrameConverter(df_jobs)
df_leads = dfConverter.convert_to_lead_dataframe(time_window=10)
df_leads = df_leads.loc[~df_leads["Entreprise"].apply(dfConverter.verif_recruitment)]
df_leads.to_csv("data/leads_tests.csv", sep=",")
