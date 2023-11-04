import logging
import pandas as pd
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter

# Setup logging
logger = logging.getLogger(__name__)


df_jobs = pd.read_csv("src/ai_leads/jobs_tests.csv", sep=";")
dfConverter = LeadDataFrameConverter(df_jobs)
df_leads = dfConverter.convert_to_lead_dataframe(time_window=10)
df_leads.to_csv("src/ai_leads/leads_tests.csv", sep=",")
