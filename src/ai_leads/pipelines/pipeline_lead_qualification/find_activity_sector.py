import logging
import pandas as pd
import numpy as np
from ai_leads.Config.param import JOB_FILE_PATH, COMPANY_FILE_PATH
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter
from ai_leads import utils

# Setup logging
logger = logging.getLogger(__name__)

# Read job and company data from CSV files
df_jobs = pd.read_csv(JOB_FILE_PATH, sep=";", dtype=str)
df_companies = pd.read_csv(COMPANY_FILE_PATH, sep=";", dtype=str)

# Extract unique company names from the job data
company_list = list(df_jobs["company"].unique())

# Create a set of companies already in df_companies
existing_companies = set(df_companies["company"].apply(utils.clean_str_unidecode))

# Find companies from company_list not in df_companies
new_companies = [
    company for company in company_list if utils.clean_str_unidecode(company) not in existing_companies
]  # noqa: E501

# Create a DataFrame with np.nan values for these new companies
new_companies_df = pd.DataFrame({"company": new_companies})
new_companies_df = new_companies_df.assign(
    **{col: np.nan for col in df_companies.columns if col != "company"}
)  # noqa: E501

# add this DataFrame to df_companies using pd.concat
df_companies = pd.concat([df_companies, new_companies_df], ignore_index=True)

# Now you can proceed to save the updated df_companies
df_companies.to_csv(COMPANY_FILE_PATH, sep=";", index=False)

# Fill missing values in the "activity_sector" column of df_companies
# based on the company name using the dfConverter.determine_activity_sector function
missing_activity_sector_mask = df_companies["activity_sector"].isna()
print(missing_activity_sector_mask)
df_companies.loc[missing_activity_sector_mask, "activity_sector"] = df_companies.loc[
    missing_activity_sector_mask, "company"
].apply(LeadDataFrameConverter().determine_activity_sector)

# Save the updated df_companies DataFrame to the CSV file
df_companies.to_csv(COMPANY_FILE_PATH, sep=";", index=False)
