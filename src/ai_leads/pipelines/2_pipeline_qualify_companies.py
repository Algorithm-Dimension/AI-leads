import logging

import numpy as np
import pandas as pd

from ai_leads import utils
from ai_leads.Config.param import COMPANY_FILE_PATH, JOB_FILE_PATH
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter
from ai_leads.model.navigator import WebpageScraper

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scraper = WebpageScraper()


def read_csv_file(file_path, sep=";", dtype=str):
    """Lire un fichier CSV et retourner un DataFrame."""
    try:
        return pd.read_csv(file_path, sep=sep, dtype=dtype)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        raise


def find_new_companies(df_jobs: pd.DataFrame, df_companies: pd.DataFrame) -> pd.DataFrame:
    """Identifier les nouvelles entreprises non présentes dans df_companies."""
    df_jobs["company_unidecode"] = df_jobs["company"].apply(utils.clean_str_unidecode)  # noqa: E501
    df_jobs.drop_duplicates(subset="company_unidecode", keep="first", inplace=True)
    company_list = list(df_jobs["company"].unique())
    existing_companies = set(df_companies["company"].apply(utils.clean_str_unidecode))
    new_companies = [
        utils.clean_str_classic(company)
        for company in company_list
        if utils.clean_str_unidecode(company) not in existing_companies
    ]
    return pd.DataFrame({"company": new_companies})


def update_companies_with_new_entries(df_companies, new_companies_df):
    """Ajouter de nouvelles entreprises à df_companies."""
    if not new_companies_df.empty:
        new_companies_df = new_companies_df.assign(**{col: np.nan for col in df_companies.columns if col != "company"})
        return pd.concat([df_companies, new_companies_df], ignore_index=True)
    return df_companies


def fill_missing_values(df_companies: pd.DataFrame, column_name: str, fill_method) -> pd.DataFrame:
    """Fill missing values in a specific column of df_companies."""
    # We will use a for-loop instead of apply for better control over saving
    missing_indices = df_companies[df_companies[column_name].isna()].index

    for idx in missing_indices:
        print(df_companies.iloc[idx]["company"])
        # Fill the missing value with the result of the fill_method
        df_companies.at[idx, column_name] = fill_method(df_companies.at[idx, "company"])
        # Save the DataFrame after each fill
        save_df_to_csv(df_companies, COMPANY_FILE_PATH)

    return df_companies


def save_df_to_csv(df: pd.DataFrame, file_path: str, sep=";"):
    """Sauvegarder un DataFrame dans un fichier CSV."""
    try:
        df.to_csv(file_path, sep=sep, index=False)
        logger.info(f"Fichier sauvegardé avec succès : {file_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier {file_path}: {e}")


def process_company_updates():
    """Processus principal pour mettre à jour les données des entreprises."""
    df_jobs = read_csv_file(JOB_FILE_PATH)
    df_companies = read_csv_file(COMPANY_FILE_PATH)

    new_companies_df = find_new_companies(df_jobs, df_companies)
    df_companies = update_companies_with_new_entries(df_companies, new_companies_df)
    df_companies = fill_missing_values(
        df_companies, "activity_sector", LeadDataFrameConverter(scraper=scraper).determine_activity_sector
    )
    # save_df_to_csv(df_companies, COMPANY_FILE_PATH)

    df_companies = fill_missing_values(df_companies, "website_url", LeadDataFrameConverter().add_web_site_url)

    # save_df_to_csv(df_companies, COMPANY_FILE_PATH)


if __name__ == "__main__":
    try:
        process_company_updates()
        scraper.close_driver()

    except Exception as e:
        logger.error(f"Une erreur est survenue lors de la mise à jour des données des entreprises: {e}")
