import os
import logging
import numpy as np
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from io import StringIO
from Config.config_safe import API_KEY_RAPH
from param import TEMPLATE
import utils

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Move the API key to environment variables for security reasons
os.environ["OPENAI_API_KEY"] = API_KEY_RAPH

class LLMManager:
    def __init__(self, model_name: str = "gpt-3.5-turbo-16k", temperature: float = 0.0):
        """Initialize the LLMManager with a model."""
        self.llm = ChatOpenAI(temperature=temperature, model_name=model_name)

    def prepare_prompt(self, template: str, input_vars: list = [], partial_vars: dict = {}) -> PromptTemplate:
        """
        Prepares a prompt template.

        Args:
        - template: str
        - input_vars: list[str]
        - partial_vars: dict
        
        Returns:
        PromptTemplate object
        """
        return PromptTemplate(template=template, input_variables=input_vars, partial_variables=partial_vars)

    def run_llm_chain(self, prompt: PromptTemplate, **input_vars) -> dict:
        """
        Runs an LLMChain and returns the response.

        Args:
        - prompt: PromptTemplate object
        - input_vars: keyword arguments
        
        Returns:
        dict: response from LLMChain.run()
        """
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        return llm_chain.run(**input_vars)

def find_job_list_url(url: str, html_raw_code: str, template: str, output_parser=None) -> str:
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

    manager = LLMManager()
    variable_list = utils.extract_variables(template)
    
    if output_parser != None:
        format_instructions = output_parser.get_format_instructions()
        variable_list.remove("format_instructions")
        prompt = manager.prepare_prompt(template=template, input_vars=variable_list, 
                                        partial_vars={"format_instructions": format_instructions})
        response = manager.run_llm_chain(prompt, url=url, html_raw_code=html_raw_code)
        return(output_parser.parse(response))
    else:
        prompt = manager.prepare_prompt(template=template, input_vars=variable_list)
        response = manager.run_llm_chain(prompt, url=url, html_raw_code=html_raw_code)
        return response

def create_table_with_job(url: str, html_raw_code: str) -> pd.DataFrame:
    """
    Creates a table with job listings.

    Args:
    - url: str
    - html_raw_code: str
    
    Returns:
    pd.DataFrame: job listings table
    """
    
    template = TEMPLATE
    output_parser = None
    response = find_job_list_url(url, html_raw_code, template, output_parser)

    try:
        df  = pd.read_csv(StringIO(response), sep=";")
    except Exception as error:
        print(error)
        print(response)
        
    return df
