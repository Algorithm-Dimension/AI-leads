import logging

import pandas as pd

from ai_leads import utils
from ai_leads.Config.param import COMPANY_FILE_PATH, JOB_FILE_PATH, LEAD_FILE_PATH, CompanyActivity
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_csv_file(file_path, sep=";"):
    """Lire un fichier CSV et retourner un DataFrame."""
    try:
        return pd.read_csv(file_path, sep=sep)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        raise


def convert_jobs_to_leads(df_jobs, time_window):
    """Convertir les données des offres d'emploi en prospects."""
    df_jobs.drop_duplicates(subset=["job name", "company", "location", "offer date", "source"], inplace=True)
    dfConverter = LeadDataFrameConverter(df_jobs)
    return dfConverter.convert_to_lead_dataframe(time_window=time_window)


def merge_leads_with_companies(df_leads, df_company_list):
    """Fusionner les données des prospects avec les informations des entreprises."""
    df_leads["company_join"] = df_leads["Entreprise"].apply(utils.clean_str_unidecode)
    df_company_list["company_join"] = df_company_list["company"].apply(utils.clean_str_unidecode)
    df_merged = pd.merge(df_leads, df_company_list, on="company_join", how="left")
    df_merged.drop(columns=["company", "company_join"], inplace=True)
    return df_merged


def filter_leads_by_activity(df_leads):
    """Filtrer les prospects en excluant certains secteurs d'activité."""
    return df_leads.loc[df_leads["activity_sector"] != CompanyActivity.RECRUITING.value]


def save_to_csv(df, file_path, sep=";"):
    """Sauvegarder un DataFrame dans un fichier CSV."""
    try:
        df.to_csv(file_path, sep=sep, index=False)
        logger.info(f"Fichier sauvegardé avec succès : {file_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier {file_path}: {e}")


def main():
    try:
        df_jobs = read_csv_file(JOB_FILE_PATH)
        df_leads = convert_jobs_to_leads(df_jobs, time_window=10)
        df_company_list = read_csv_file(COMPANY_FILE_PATH)
        df_leads = merge_leads_with_companies(df_leads, df_company_list)
        df_leads = filter_leads_by_activity(df_leads)
        save_to_csv(df_leads, LEAD_FILE_PATH)
    except Exception as e:
        logger.error(f"Une erreur est survenue : {e}")


if __name__ == "__main__":
    main()
