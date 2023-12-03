import logging
import numpy as np
import pandas as pd
import dateparser
from datetime import datetime
from ai_leads.Config.param import template_verif, output_parser_verif
from ai_leads.model.llm_model import LLMManager
from ai_leads.model.navigator import WebpageScraper

# Setup logging
logger = logging.getLogger(__name__)


class LeadDataFrameConverter:
    """
    A class to handle conversion of a dataframe into a lead dataframe.

    Attributes:
        df (pd.DataFrame): The input dataframe.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the LeadDataFrameConverter with a dataframe.

        Args:
            df (pd.DataFrame): The input dataframe.
        """
        self.df = df.copy()
        self.df.columns = [col.strip() for col in self.df.columns]
        self.llm_manager = LLMManager()
        self.scraper = WebpageScraper()

    def convert_time_column(self, col: str):
        """
        Converts a column in the dataframe from temporal strings to days.

        Args:
            col (str): The name of the column to convert.
        """
        self.df[f"{col} clean"] = self.df[col].apply(self.convert_to_days)

    def convert_to_lead_dataframe(self, time_window: int) -> pd.DataFrame:
        """
        Convert the dataframe with all job offers into a lead dataframe, filtering by a specific time window.

        Args:
            time_window (int): The maximum number of days since an offer was posted.

        Returns:
            pd.DataFrame: The lead dataframe.
        """
        try:
            self.convert_time_column("offer date")
        except Exception as error:
            logger.info("An error occured while converting time: %s", error)

        df_jobs = self.df.loc[self.df["offer date clean"] <= time_window]
        df = df_jobs.groupby(["company_id", "company", "source"]).size().reset_index(name="count")
        max_count_idx = df.groupby(["company_id", "company"])["count"].idxmax()

        # Sélectionnez les lignes correspondantes dans le DataFrame d'origine
        df_lead = df.loc[max_count_idx, ["company_id", "company", "source", "count"]]
        # df_lead = pd.DataFrame(self.df["company"].value_counts()).reset_index()
        df_lead.columns = [
            "company_id",
            "Entreprise",
            "source",
            f"Nombre d'offres postés les {time_window} derniers jours",
        ]
        df_lead["Entreprise"] = df_lead["Entreprise"].apply(lambda x: x.strip())
        df_lead["Entreprise"] = df_lead["Entreprise"].apply(lambda x: x.lower())
        df_lead = df_lead.groupby("Entreprise").sum()
        df_lead["Contacté"] = "Non"
        df_lead["Téléphone"] = np.nan
        df_lead["Email"] = np.nan
        df_lead.sort_values(
            by=f"Nombre d'offres postés les {time_window} derniers jours", ascending=False, inplace=True
        )

        return df_lead

    @staticmethod
    def convert_to_days(temp_string: str) -> int:
        """
        Convert a temporal string into a number of days since that date.

        Args:
            temp_string (str): The temporal string, e.g., "il y a 3 jours".

        Returns:
            int: Number of days since the date represented by temp_string.
        """
        try:
            parsed_date = dateparser.parse(temp_string, languages=["fr", "en"])
            today = datetime.now()
            delta = today - parsed_date
            return int(delta.days)
        except Exception as error:
            logger.info("Failed to parse date from string %s %s", temp_string, error)
            return -1

    def verif_recruitment(self, company: str):
        llm_manager = self.llm_manager
        scraper = self.scraper
        query = company
        url_list = self.scraper.get_raw_google_links(query)
        for url in url_list:
            output_parser = output_parser_verif
            format_instructions = output_parser.get_format_instructions()
            html_raw_code_full = scraper.fetch_readable_text(url)
            html_raw_code = self.llm_manager.return_prompt_beginning(html_raw_code_full)
            prompt = llm_manager.prepare_prompt(
                template_verif,
                input_vars=["company", "html_raw_code"],
                partial_vars={"format_instructions": format_instructions},
            )
            response = llm_manager.run_llm_chain(prompt, company=company, html_raw_code=html_raw_code)
            is_recruitement_company = output_parser.parse(response)["isRecruitmentCompany"]
            if is_recruitement_company == "Yes":
                return True
        return False
