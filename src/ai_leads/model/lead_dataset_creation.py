import logging
from datetime import datetime

import dateparser
import pandas as pd

from ai_leads import utils
from ai_leads.Config.param import (
    CompanyActivity,
    enum_parser_activity,
    template_find_activity,
    BASE_DATE,
)
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

    def __init__(
        self,
        df: pd.DataFrame = pd.DataFrame(),
        scraper: WebpageScraper = WebpageScraper(),
    ):  # noqa
        """
        Initializes the LeadDataFrameConverter with a dataframe.

        Args:
            df (pd.DataFrame): The input dataframe.
            scraper (WebpageScraper): the scrapper instance to use
        """
        self.df = df.copy()
        self.df.columns = [col.strip() for col in self.df.columns]
        self.llm_manager = LLMManager()
        self.scraper = scraper

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
        df = df_jobs.groupby(["company", "source"]).size().reset_index(name="count")
        max_count_idx = df.groupby(["company"])["count"].idxmax()

        # Sélectionnez les lignes correspondantes dans le DataFrame d'origine
        df_lead = df.loc[max_count_idx, ["company", "source", "count"]]
        # df_lead = pd.DataFrame(self.df["company"].value_counts()).reset_index()
        df_lead.columns = [
            "Entreprise",
            "source",
            f"Nombre d'offres postés les {time_window} derniers jours",
        ]
        df_lead["Entreprise"] = df_lead["Entreprise"].apply(utils.clean_str_classic)
        df_lead = df_lead.groupby("Entreprise").sum()
        df_lead.reset_index(inplace=True)
        df_lead.sort_values(
            by=f"Nombre d'offres postés les {time_window} derniers jours",
            ascending=False,
            inplace=True,  # noqa: E501
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

    def determine_activity_sector(self, company: str) -> str:
        """
        Determine the activity sector of a company by doing research on the web and asking questions to chatGPT

        Args:
            company (str): the company name

        Returns:
            str: the activity sector: Recruiting, education/formation, other, unknown
        """
        logger.info("Search activity sector for: %s", company)
        activity_list = []
        llm_manager = self.llm_manager
        scraper = self.scraper
        query = company
        url_list = self.scraper.get_raw_google_links(query)
        for url in url_list:
            try:
                output_parser = enum_parser_activity
                format_instructions = output_parser.get_format_instructions()
                html_raw_code_full = scraper.fetch_readable_text(url)
                html_raw_code = self.llm_manager.return_prompt_beginning(
                    html_raw_code_full
                )
                prompt = llm_manager.prepare_prompt(
                    template_find_activity,
                    input_vars=["company", "html_raw_code"],
                    partial_vars={"format_instructions": format_instructions},
                )
                response = llm_manager.run_llm_chain(
                    prompt,
                    company=company,
                    html_raw_code=html_raw_code,
                    format_instructions=format_instructions,
                )
                activity_sector = response.content
            except Exception as error:
                logger.info(
                    "An error occured while determining activity sector: %s", error
                )
                activity_sector = CompanyActivity.OTHER.value
            logger.info("Activity sector for %s: %s", company, activity_sector)
            activity_list.append(activity_sector)

        # La priorité est de reconnaitre les agences de recrutements, donc si un des liens
        # nous signale que c'est une agence de recrutement, on la marque comme telle.
        # Ensuite, il faut repréer formation/education, car c'est difficile
        # de trouver les responsables rh sur Linkedin pour ces entreprises

        if CompanyActivity.RECRUITING.value in activity_list:
            return CompanyActivity.RECRUITING.value
        elif CompanyActivity.FORMATION_ECOLE.value in activity_list:
            return CompanyActivity.FORMATION_ECOLE.value
        else:
            return CompanyActivity.OTHER.value

    def verif_recruitment(self, company: str) -> bool:
        """
        Determine if a company is a recruiting company or not

        Args:
            company (str): the company name

        Returns:
            bool: True or False if it is a recruiting company
        """
        activity_sector = self.determine_activity_sector(company)
        return activity_sector == CompanyActivity.RECRUITING.value

    def add_web_site_url(self, company: str) -> str:
        """
        Find the website of a company

        Args:
            company (str): the company name

        Returns:
            str: company website
        """
        logger.info("Search URL for: %s", company)
        query = company
        url_list = self.scraper.get_raw_google_links(query, num_results=1)
        if len(url_list) > 0:
            return url_list[0]
        return "https://www.google.com"
