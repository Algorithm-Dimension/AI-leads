import logging
import re
from datetime import datetime
from io import StringIO
from typing import Dict

import dateparser
import pandas as pd
from langchain.output_parsers import StructuredOutputParser
from unidecode import unidecode

import ai_leads.utils as utils
from ai_leads.Config.param import BASE_DATE, DATA_IDF_CITY_PATH, OUTPUT_PARSER, TEMPLATE
from ai_leads.model.llm_model import LLMManager
from ai_leads.model.navigator import WebpageScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobDataFrameCreator(LLMManager):
    """
    A class to create .

    Attributes:
        df (pd.DataFrame): The input dataframe.
    """

    def __init__(self, scraper: WebpageScraper = WebpageScraper()):
        """
        Initializes the LeadDataFrameConverter with a dataframe.

        Args:
            scraper (WebpageScraper): The scraper instance to use
        """
        super().__init__()
        self.scraper = scraper
        self.llm_manager = LLMManager()

    def _find_job_list_url(
        self, url: str, html_raw_code: str, template: str, output_parser: StructuredOutputParser = None
    ) -> str:
        """
        Find all the job offer of a web page

        Args:
        - url: str
        - html_raw_code: str
        - template: str
        - output_parser: optional

        Returns:
        str: parsed response value
        """

        variable_list = utils.extract_variables(template)

        if output_parser is not None:
            format_instructions = output_parser.get_format_instructions()
            variable_list.remove("format_instructions")
            prompt = self.prepare_prompt(
                template=template,
                input_vars=variable_list,
                partial_vars={"format_instructions": format_instructions},
            )
            response = self.run_llm_chain(prompt, url=url, html_raw_code=html_raw_code)
            return output_parser.parse(response)
        else:
            prompt = self.prepare_prompt(template=template, input_vars=variable_list)
            response = self.run_llm_chain(prompt, url=url, html_raw_code=html_raw_code)
            return response

    def create_table_with_job(self, url: str, platform: str) -> pd.DataFrame:
        """
        Creates a table with job listings.

        Args:
        - url: str

        Returns:
        pd.DataFrame: job listings table
        """

        df = pd.DataFrame()
        template = TEMPLATE
        output_parser = OUTPUT_PARSER
        html_raw_code_full = WebpageScraper(platform, headless=False).fetch_readable_text(url)
        html_raw_code = self.llm_manager.return_prompt_beginning(html_raw_code_full)
        response = self._find_job_list_url(url, html_raw_code, template, output_parser)
        try:
            df = pd.read_csv(StringIO(response), sep=";", on_bad_lines="skip")
            df.columns = [col.strip() for col in df.columns]
            logger.info("We just keep idf cities")
            df = df.loc[df["location"].apply(lambda x: self.is_in_ile_de_france(x))]
            logger.info("We process date")
            df["offer date"] = df["time indication"].apply(lambda x: self.convert_to_date(x))
            df.drop(columns=["time indication"], inplace=True)
        except Exception as error:
            logger.info("An error occured: %s", error)
            logger.info("LLM Response is: %s", response)
        return df

    @staticmethod
    def _unify_dataframe(dataframe_dict: Dict[str, pd.DataFrame]):
        # Créez une liste vide pour stocker les DataFrames concaténés
        concatenated_dfs = []

        # Parcourez le dictionnaire et concaténez les DataFrames tout en ajoutant la colonne "source"
        for key, df in dataframe_dict.items():
            # Ajoutez une colonne "source" avec la valeur correspondante à la clé
            concatenated_dfs.append(df)

        # Concaténez tous les DataFrames en un seul
        result_df = pd.concat(concatenated_dfs, ignore_index=True)

        return result_df

    @staticmethod
    def clean_str(string: str) -> str:
        # Utiliser une expression régulière pour garder seulement les lettres de l'alphabet
        clean_string = re.sub(r"[^a-zA-Z]", "", unidecode(string))
        return clean_string.lower()

    def is_in_ile_de_france(self, city: str) -> bool:
        with open(DATA_IDF_CITY_PATH, "r") as file:
            idf_location_list = file.readlines()
        idf_location_list = [city[:-1] for city in idf_location_list]
        try:
            if self.clean_str(city) in idf_location_list:
                return True
        except Exception as e:
            print(f"An error occurred: {e}")
        return False

    @staticmethod
    def convert_to_date(temp_string: str, base_date: datetime = BASE_DATE) -> str:
        """
        Convert a temporal string into a date in string.

        Args:
            temp_string (str): The temporal string, e.g., "il y a 3 jours".

        Returns:
            int: Number of days since the date represented by temp_string.
        """
        try:
            temp_string = temp_string.lower()
            # On enlève ici tous les mots génants pour convertir en date
            temp_string = temp_string.replace("moins de ", "")
            temp_string = temp_string.replace("plus de ", "")
            temp_string = temp_string.replace("publiée ", "")
            temp_string = temp_string.replace("publié ", "")
            temp_string = temp_string.replace("modifiée ", "")
            temp_string = temp_string.replace("modifié ", "")
            # On s'occupe de certains cas particuliers:
            if "instant" in temp_string:
                return base_date.strftime("%d-%m-%Y")
            parsed_date = dateparser.parse(
                temp_string, languages=["fr", "en"], date_formats=["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]  # noqa
            )
            return parsed_date.strftime("%d-%m-%Y")
        except Exception as error:
            logger.info("Failed to parse date from string %s %s", temp_string, error)
            return temp_string
