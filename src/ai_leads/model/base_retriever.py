import logging
from abc import ABC, abstractmethod
from typing import Dict, List

import numpy as np
import pandas as pd
from langchain.output_parsers import StructuredOutputParser
from ai_leads import utils
from ai_leads.model.llm_model import LLMManager
from ai_leads.model.navigator import WebpageScraper

# TODO Healthcare, corp heritage

# Setup logging
logging.basicConfig(level=logging.INFO)
local_logger = logging.getLogger(__name__)


class BaseInformationRetrieverLLM(ABC):
    """
    A manager to retrieve specific information from raw HTML using LLMS
    """

    def __init__(
        self,
        template: str,
        output_parser: StructuredOutputParser,
        num_results=3,
        logger: logging.Logger = local_logger,
    ):
        self.scraper = WebpageScraper()
        self.llm_manager = LLMManager()
        self.logger = logger
        self.template = template
        self.output_parser = output_parser
        self.num_results = num_results

    def answer_llm(
        self,
        template: str,
        output_parser: StructuredOutputParser,
        **kwargs: str,
    ) -> Dict[str, str]:
        """
        Generate a response to a prompt as a json, structured by the output_parser

        Args:
            template (str): Template to guide the response.
            output_parser (StructuredOutputParser): An object to parse the model's output.
            ** kwargs: the argument that we need in the templates

        Returns:
            str: Parsed response value.
        """
        format_instructions = output_parser.get_format_instructions()
        variable_list = utils.extract_variables(template)
        variable_list.remove("format_instructions")
        prompt = self.llm_manager.prepare_prompt(template, variable_list, {"format_instructions": format_instructions})
        response = self.llm_manager.run_llm_chain(prompt, **kwargs)
        local_logger.debug(f"Response: {response}")
        return output_parser.parse(response)

    @staticmethod
    def append_json_objects(dicts: list) -> dict:
        """
        Merge a list of dictionaries into one dictionary with lists as values for each key.

        Args:
            dicts (list): List of dictionaries to merge.

        Returns:
            dict: Merged dictionary.
        """
        key_set = set(key for d in dicts for key in d.keys())
        merged_dict = {key: [] for key in key_set}
        for key in key_set:
            for d in dicts:
                merged_dict[key].append(d.get(key, np.nan))
        return merged_dict

    @staticmethod
    def merge_jsons(json_list: list, threshold: int = 2) -> dict:
        """
        Merge a list of dictionaries based on specific logic rules.

        Args:
            json_list (list): List of dictionaries to merge.
            threshold (int): Threshold for 'isclient' key.

        Returns:
            dict: Merged dictionary.
        """
        result_json = {
            "isclient": "No",
            "startDate": "n.a.",
            "endDate": "n.a.",
            "contractAmount": "n.a.",
            "sourceDate": "n.a.",
        }
        countYes = sum(1 for json_obj in json_list if json_obj.get("isclient") == "Yes")

        result_json["isclient"] = "Yes" if countYes >= threshold else "No"
        for json_obj in json_list:
            for key, value in json_obj.items():
                if value not in ["n.a.", "Yes"]:
                    result_json[key] = value

        return result_json

    def _process_urls(
        self,
        url_list: list[str],
        **kwargs: str,
    ) -> list:
        """
        Process a list of URLs and return a list of JSON-like responses.

        Args:
            url_list (list): List of URLs.

        Returns:
            list: List of JSON-like responses.
        """
        template = self.template
        output_parser = self.output_parser
        json_list = []
        for url in url_list:
            self.logger.info("Here is the scraped link: %s", url)
            html_raw_code_full = self.scraper.fetch_readable_text(url)
            html_raw_code = self.llm_manager.return_prompt_beginning(html_raw_code_full)
            try:
                json_response = self.answer_llm(template, output_parser, html_raw_code=html_raw_code, **kwargs)
                json_response.update({"source": url})
                json_list.append(json_response)
            except Exception as error:
                self.logger.error("Error processing URL %s: %s", url, error)
        return json_list

    def _process_urls_lazy(
        self,
        url_list: list[str],
        must_contain_keywords=None,
        **kwargs: str,
    ) -> list:
        """
        the same as _process_urls but stops when it finds a correct answer

        Args:
            url_list (list): List of URLs.
            template (str): Template to guide the response.
            output_parser (object): An object to parse the model's output.
            headless (bool): Option to extract readable text.

        Returns:
            list: List of JSON-like responses.
        """
        # makes it immutable in the input
        if must_contain_keywords is None:
            must_contain_keywords = []

        template = self.template
        output_parser = self.output_parser
        json_list = []
        for url in url_list:
            self.logger.info("Here is the scraped link: %s", url)
            html_raw_code_full = self.scraper.fetch_readable_text(url)
            html_raw_code = self.llm_manager.return_prompt_beginning(html_raw_code_full)
            try:
                json_response = self.answer_llm(template, output_parser, html_raw_code=html_raw_code, **kwargs)
                json_response.update({"source": url})
                json_list.append(json_response)
                if self.check_values(json_list):
                    return json_list
            except Exception as error:
                self.logger.error("Error processing URL %s: %s", url, error)
        return json_list

    def create_table_client(self) -> pd.DataFrame:
        """
        Convert JSON-like answers into a pandas DataFrame.

        Args:
            client (str): The client's name.
            food_provider (str): The food provider's name.
            research_type (str): Type of research ('global', 'inProfile', etc.).

        Returns:
            pd.DataFrame: Information in tabular form.
        """
        json_answer = self._obtain_all_answers()
        df = self._json_to_dataframe(json_answer)
        if "source" in df.columns:
            df.drop_duplicates(["source"], inplace=True)
        return df

    @abstractmethod
    def _obtain_all_answers(self) -> dict:
        """
        Fetch answers based on different research types.

        Args:
            research_type (str): Type of research ('global', 'inProfile', etc.).
            threshold (int): Threshold for 'isclient' key in merge_jsons.

        Returns:
            dict: JSON-like result.
        """

    @staticmethod
    def _json_to_dataframe(json_answer: dict) -> pd.DataFrame:
        df = pd.DataFrame()
        try:
            df = pd.DataFrame(json_answer)
            df.drop_duplicates(inplace=True)
        except Exception:
            pass
        df.replace("n.a.", np.nan, inplace=True)
        return df

    @staticmethod
    def check_values(data_list: List[Dict[str, str]]) -> Dict[str, bool]:
        """
        Check if each key contains at least one value different from "n.a." in a list of dictionaries.

        Args:
            data_list (List[Dict[str, str]]): A list of dictionaries to be checked.

        Returns:
            Dict[str, bool]: A dictionary where keys represent the keys from dictionaries,
            and values indicate if the key contains at least one value different from "n.a." (True) or not (False).
        """
        # Create a dictionary to store results by key
        result = {}

        # Iterate through the list of dictionaries
        for item in data_list:
            # Iterate through each key in the dictionary
            for key, value in item.items():
                # Check if the key already exists in the result
                if key not in result:
                    # If the key doesn't exist, initialize it to False
                    result[key] = False

                # Check if the value is different from "n.a."
                if value.lower() != "n.a.":
                    # If a value different from "n.a." is found, mark the key as True
                    result[key] = True
        for key in result:
            if result[key] is False:
                return False
        return True

    @abstractmethod
    def sanity_check(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanity check of found information

        Args:
            df (DataFrame): The input DataFrame.

        Returns:
            DataFrame: A new DataFrame with only verificated rows
        """

    @abstractmethod
    def output_final_dataframes(self, df) -> dict:
        """
        Output the DataFrame with the final information to keep

        Args:
            df (DataFrame): The input DataFrame.

        Returns:
            DataFrame: A new DataFrame with a single row
        """
