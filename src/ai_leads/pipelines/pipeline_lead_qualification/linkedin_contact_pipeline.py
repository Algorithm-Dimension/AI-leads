import logging
import pandas as pd
import numpy as np
from ai_leads.Config.param import COMPANY_FILE_PATH, CONTACT_FILE_PATH, CompanyActivity
from ai_leads.model.linkedin_contact import LinkedInContactRetriever
from ai_leads import utils

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_data(file_path: str) -> pd.DataFrame:
    """
    Lit un fichier CSV et retourne un DataFrame.
    """
    try:
        return pd.read_csv(file_path, sep=";")
    except Exception as e:
        logger.error(f"Erreur de lecture du fichier {file_path}: {e}")
        raise


def clean_and_filter_data(df_company: pd.DataFrame, df_contact: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et filtre les données de l'entreprise.
    """
    existing_companies_contacts = set(df_contact["company"].apply(utils.clean_str_unidecode))
    df_company = df_company[~df_company["company"].apply(utils.clean_str_unidecode).isin(existing_companies_contacts)]
    df_company = df_company[
        ~df_company["activity_sector"].isin([CompanyActivity.RECRUITING.value, CompanyActivity.FORMATION_ECOLE.value])
    ]
    return df_company


def add_linkedin_contacts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute les contacts LinkedIn aux entreprises.
    """
    df[["linkedin_url_1", "linkedin_url_2"]] = (
        df["company"].apply(LinkedInContactRetriever().find_relevant_profiles).apply(pd.Series)
    )
    return df[["company", "linkedin_url_1", "linkedin_url_2"]]


def main():
    df_company_list = read_data(COMPANY_FILE_PATH)
    df_contact = read_data(CONTACT_FILE_PATH)

    df_company_list = clean_and_filter_data(df_company_list, df_contact)
    df_company_list = add_linkedin_contacts(df_company_list)

    df_contact = pd.concat([df_contact, df_company_list], ignore_index=True)
    df_contact.fillna(np.nan, inplace=True)

    try:
        df_contact.to_csv(CONTACT_FILE_PATH, sep=";", index=False)
        logger.info("Fichier de contacts sauvegardé avec succès.")
    except Exception as e:
        logger.error(f"Erreur de sauvegarde du fichier de contacts: {e}")


if __name__ == "__main__":
    main()
