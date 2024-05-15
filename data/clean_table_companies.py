import pandas as pd
from ai_leads.Config.param import CompanyActivity
from ai_leads import utils

df = pd.read_csv("data/table_companies.csv", sep=";")


def clean_str_classic(text):
    if text in [
        CompanyActivity.OTHER.value,
        CompanyActivity.RECRUITING.value,
        CompanyActivity.FORMATION_ECOLE.value,
    ]:
        return text
    if "recrutement" in text.lower():
        return CompanyActivity.RECRUITING.value
    if "formation" in text.lower() or "éducation" in text.lower():
        return CompanyActivity.FORMATION_ECOLE.value
    return CompanyActivity.OTHER.value


# df["activity_sector"] = df["activity_sector"].apply(clean_str_classic)
# print(df.head)

# df.to_csv("data/table_companies.csv", sep=";", index=False)

df_contact = pd.read_csv("data/table_contact_test.csv", sep=";")
contact_columns = list(df_contact.columns)
df["clean_company"] = df["company"].apply(utils.clean_str_unidecode)
df_contact["clean_company"] = df_contact["company"].apply(utils.clean_str_unidecode)
df_contact.drop("company", axis=1, inplace=True)
df_contact = pd.merge(df_contact, df, on="clean_company", how="right")
df_contact.drop(["clean_company"], axis=1, inplace=True)
df_contact = df_contact[contact_columns]
df_contact.to_csv("data/table_contact_test.csv", sep=";", index=False)
