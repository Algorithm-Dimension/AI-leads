import os
import logging
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Move the API key to environment variables for security reasons
# os.environ["OPENAI_API_KEY"] = API_KEY_RAPH


class LLMManager:
    def __init__(self, model_name: str = "gpt-3.5-turbo-16k", temperature: float = 0.0):
        """Initialize the LLMManager with a model."""
        load_dotenv()
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
