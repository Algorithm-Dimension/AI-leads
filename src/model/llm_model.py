import os
import logging
import numpy as np
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from Config.config_safe import API_KEY_RAPH
import html_scrapping

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

def prepare_prompt(template, input_vars, partial_vars):
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

def find_job_list_url(url, html_raw_code):
    """
    Finds a response regarding the assurance of food provider for a university.

    Args:
    - university: str
    - food_provider: str
    
    Returns:
    str: parsed response value
    """

    template =  '''
            You are analyzing the text extracted from a website with job positions : {url}.
            Using this information, write a table with:
            - job name
            - company
            - location
            - offer date
            - contact (an email address or a phone number)
            Write N.A when the information is not available.
            
            url text: {html_raw_code}.
                '''                
    llm = get_llm()
    prompt = PromptTemplate(template=template, input_variables=["url", "html_raw_code"])
    response = run_llm_chain(llm, prompt, url=url, html_raw_code=html_raw_code)
    return response


def create_table_customer(url, html_raw_code):
    json_answer = find_job_list_url(url, html_raw_code)
    print("JSON Answer = ", json_answer)
    df = pd.DataFrame(json_answer)
    return df

