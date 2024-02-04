import logging
import os

import numpy as np
import pandas as pd

from ai_leads import utils
from ai_leads.Config.param import COMPANY_FILE_PATH, CONTACT_FILE_PATH, CompanyActivity
from ai_leads.model.linkedin_contact import LinkedInContactRetriever

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


def add_linkedin_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute les contacts LinkedIn aux entreprises.
    """
    df[["firstName1", "lastName1"]] = (
        df["linkedin_url_1"].apply(LinkedInContactRetriever().find_name_from_linkedin_url).apply(pd.Series)
    )

    df[["firstName2", "lastName2"]] = (
        df["linkedin_url_2"].apply(LinkedInContactRetriever().find_name_from_linkedin_url).apply(pd.Series)
    )


def add_linkedin_contacts_and_save(df_company: pd.DataFrame):
    """
    Ajoute les contacts LinkedIn aux entreprises et sauvegarde chaque nouvelle ligne directement dans le fichier existant.
    """
    df_contact = read_data(CONTACT_FILE_PATH)

    for _, row in df_company.iterrows():
        linkedin_data = LinkedInContactRetriever().find_relevant_profiles(row["company"])
        # Supposons que linkedin_data est une liste de profils; ajustez selon votre implémentation
        # Ajout des données LinkedIn (exemple simplifié)
        if linkedin_data:
            row["linkedin_url_1"] = linkedin_data[0]
            row["firstName1"], row["lastName1"] = LinkedInContactRetriever().find_name_from_linkedin_url(
                linkedin_data[0]
            )
            row["linkedin_url_2"] = linkedin_data[1]
            row["firstName2"], row["lastName2"] = LinkedInContactRetriever().find_name_from_linkedin_url(
                linkedin_data[1]
            )
            # Convertir la ligne en DataFrame pour écrire dans le fichier
            df_row = pd.DataFrame([row])
            df_row = df_row[
                [
                    "company",
                    "firstName1",
                    "lastName1",
                    "linkedin_url_1",
                    "firstName2",
                    "lastName2",
                    "linkedin_url_2",
                ]
            ]
            df_contact = pd.concat([df_contact, df_row], ignore_index=True)
            print("OKOKOK")
            df_contact.to_csv(CONTACT_FILE_PATH, sep=";", index=False)
            # Marquer le fichier comme existant pour les futures itérations
        else:
            logger.info(f"Aucun contact LinkedIn trouvé pour l'entreprise {row['company']}.")


def main():
    df_company_list = read_data(COMPANY_FILE_PATH)
    df_contact = read_data(CONTACT_FILE_PATH)
    df_company_list = clean_and_filter_data(df_company_list, df_contact)
    add_linkedin_contacts_and_save(df_company_list)

    logger.info("Tous les contacts LinkedIn ont été ajoutés et sauvegardés avec succès.")


if __name__ == "__main__":
    main()
