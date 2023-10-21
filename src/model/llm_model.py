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
api_key = API_KEY_RAPH
os.environ["OPENAI_API_KEY"] = api_key

def get_llm(model_name="gpt-3.5-turbo-16k", temperature=0.0):
    """
    Returns an instance of a language model.

    Args:
    - model_name: str, optional, default='gpt-3.5-turbo-16k'
    - temperature: float, optional, default=0.0
    
    Returns:
    ChatOpenAI object
    """
    return ChatOpenAI(temperature=temperature, model_name=model_name)

def prepare_prompt(template, input_vars = [], partial_vars = {}):
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

def run_llm_chain(llm, prompt, **input_vars):
    """
    Runs an LLMChain and returns the response.

    Args:
    - llm: ChatOpenAI object
    - prompt: PromptTemplate object
    - input_vars: keyword arguments
    
    Returns:
    dict: response from LLMChain.run()
    """
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return llm_chain.run(**input_vars)

def find_job_list_url(url, html_raw_code, template, output_parser=None):
    """
    Finds a response regarding the assurance of food provider for a university.

    - university: str
    - food_provider: str
    
    Returns:
    str: parsed response value
    """

    llm = get_llm()
    if output_parser != None:
        format_instructions = output_parser.get_format_instructions()
    variable_list = utils.extract_variables(template)
    if "format_instructions" in variable_list:
        variable_list.remove("format_instructions")
        prompt = prepare_prompt(template=template, input_vars=variable_list, 
                                        partial_vars={"format_instructions": format_instructions})
    else:
        prompt = prepare_prompt(template=template, input_vars=variable_list)
    response = run_llm_chain(llm, prompt, url=url, html_raw_code=html_raw_code)
    return response

def create_table_with_job(url, html_raw_code):
    template = TEMPLATE
    output_parser = None
    response = find_job_list_url(url, html_raw_code, template, output_parser)
    # Split the string into lines
    try:
        df  = pd.read_csv(StringIO(response), sep = ";")
    except Exception as error:
        print(error)
        print(response)
    return df

