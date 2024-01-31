import logging
import pandas as pd
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter
from ai_leads.Config.param import LEAD_FILE_PATH, JOB_FILE_PATH, COMPANY_FILE_PATH, CompanyActivity
from ai_leads import utils

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


df_jobs = pd.read_csv(JOB_FILE_PATH, sep=";")
dfConverter = LeadDataFrameConverter(df_jobs)
df_leads = dfConverter.convert_to_lead_dataframe(time_window=10)
df_leads["company_join"] = df_leads["Entreprise"].apply(utils.clean_str_unidecode)
df_company_list = pd.read_csv(COMPANY_FILE_PATH, sep=";")

df_company_list["company_join"] = df_company_list["company"].apply(utils.clean_str_unidecode)  # noqa: E501
df_leads = pd.merge(df_leads, df_company_list, on="company_join", how="left")
df_leads.drop(columns=["company", "company_join"], inplace=True)
df_leads = df_leads.loc[df_leads["activity_sector"] != CompanyActivity.RECRUITING.value]
df_leads.to_csv(LEAD_FILE_PATH, sep=";", index=False)
