import logging
import pandas as pd
from typing import Dict
from io import StringIO
from ai_leads.model.llm_model import LLMManager
import ai_leads.utils as utils
from ai_leads.Config.param import TEMPLATE, OUTPUT_PARSER
from ai_leads.model.navigator import WebpageScraper

# Setup logging
logger = logging.getLogger(__name__)


class JobDataFrameCreator(LLMManager):
    """
    A class to create .

    Attributes:
        df (pd.DataFrame): The input dataframe.
    """

    def __init__(self):
        """
        Initializes the LeadDataFrameConverter with a dataframe.

        Args:
            df (pd.DataFrame): The input dataframe.
        """
        super().__init__()
        self.scraper = WebpageScraper()

    def _find_job_list_url(self, url: str, html_raw_code: str, template: str, output_parser=None) -> str:
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

        if output_parser != None:
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

        template = TEMPLATE
        output_parser = OUTPUT_PARSER
        html_raw_code = WebpageScraper(platform, headless=False).fetch_readable_text(url)
        response = self._find_job_list_url(url, html_raw_code, template, output_parser)
        try:
            df = pd.read_csv(StringIO(response), sep=";")

        except Exception as error:
            logger.info("An error occured: %s", error)
            logger.info("LLM Response is: %s", response)
        print("DF = ", df)
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
