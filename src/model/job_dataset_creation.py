import logging
import numpy as np
import pandas as pd
from io import StringIO
from llm_model import LLMManager
import utils
from Config.param import TEMPLATE, OUTPUT_PARSER, DF_PARAM_SEARCH
import html_scrapping

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobDataFrameCreator(LLMManager):
    """
    A class to create .

    Attributes:
        df (pd.DataFrame): The input dataframe.
    """

    def __init__(self, plateforms_list, job_list, location):
        """
        Initializes the LeadDataFrameConverter with a dataframe.

        Args:
            df (pd.DataFrame): The input dataframe.
        """
        super().__init__()
        self.plateforms_list = plateforms_list
        self.job_list = job_list
        self.location = location

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
            prompt = self.prepare_prompt(template=template, input_vars=variable_list, 
                                            partial_vars={"format_instructions": format_instructions})
            response = self.run_llm_chain(prompt, url=url, html_raw_code=html_raw_code)
            return(output_parser.parse(response))
        else:
            prompt = self.prepare_prompt(template=template, input_vars=variable_list)
            response = self.run_llm_chain(prompt, url=url, html_raw_code=html_raw_code)
            return response

    def create_table_with_job(self, url: str) -> pd.DataFrame:
        """
        Creates a table with job listings.

        Args:
        - url: str
        
        Returns:
        pd.DataFrame: job listings table
        """
        
        template = TEMPLATE
        output_parser = OUTPUT_PARSER
        html_raw_code = html_scrapping.extract_readable_text(url)
        response = self._find_job_list_url(url, html_raw_code, template, output_parser)

        try:
            df  = pd.read_csv(StringIO(response), sep=";")
        except Exception as error:
            logger.debug(f"An error occured: {error}")
            logger.info(f"LLM Response is: {response}")

        return df

    @staticmethod
    def _unify_dataframe(dataframe_dict):
        # Créez une liste vide pour stocker les DataFrames concaténés
        concatenated_dfs = []

        # Parcourez le dictionnaire et concaténez les DataFrames tout en ajoutant la colonne "source"
        for key, df in dataframe_dict.items():
            # Ajoutez une colonne "source" avec la valeur correspondante à la clé
            concatenated_dfs.append(df)

        # Concaténez tous les DataFrames en un seul
        result_df = pd.concat(concatenated_dfs, ignore_index=True)
        
        return result_df

    def find_all_job(self):
        # FONCTION A FINIR. NE PLUS UTILISER CREATE TABLE WITH JOB AVEC URL (ICI c'est ecris source mais c'est un url)
        # UTILISER UNE LISTE DE SOURCE ET DE POSITION ET POUVOIR RETROUVER LES JOBS
        source_list = self.plateforms_list
        job_list = self.job_list
        dict_df_jobs = {}
        location = self.location
        for source in source_list:
            for job in job_list:
                url = f"https://fr.indeed.com/q-{job}-l-{location}-emplois.html"
                logger.info(f"We scrap this {url}")
                df_job = self.create_table_with_job(url)
                df_job["position"] = job
                df_job["source"] = source
                dict_df_jobs[source + job] = df_job
            final_job_df = self._unify_dataframe(dict_df_jobs)
        return(final_job_df)