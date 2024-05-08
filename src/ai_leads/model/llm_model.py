import logging

import tiktoken
from dotenv import load_dotenv
from langchain_core.messages.ai import AIMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from ai_leads.Config.param import MODEL_NAME, DEFAULT_ENCODING_NAME, CONTEXT_WINDOW, DEFAULT_RESEARCH_TYPE_THRESHOLD

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Move the API key to environment variables for security reasons
# os.environ["OPENAI_API_KEY"] = API_KEY_RAPH

# Setup logging


class LLMManager:
    def __init__(self, model_name: str = MODEL_NAME, temperature: float = 0.0):
        """Initialize the LLMManager with a model."""
        load_dotenv()
        if model_name == "llama3-8b-8192":
            self.llm = ChatGroq(temperature=0, model_name=model_name)
        elif MODEL_NAME == "gpt-3.5-turbo-16k":
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

    def run_llm_chain(self, prompt: PromptTemplate, **input_vars) -> AIMessage:
        """
        Runs an LLMChain and returns the response.

        Args:
        - prompt: PromptTemplate object
        - input_vars: keyword arguments

        Returns:
        dict: response from LLMChain.run()
        """
        llm_chain = prompt | self.llm
        invoke_params = {key: value for key, value in input_vars.items()}
        return llm_chain.invoke(invoke_params)

    def return_prompt_beginning(self, prompt: str, encoding_name: str = DEFAULT_ENCODING_NAME) -> list:
        """Return the beggining of a prompt if too long.

        Args:
            prompt (str): The input prompt.
            encoding_name (str, optional): Encoding type for tokenization.

        Returns:
            list: List of splitted prompt strings.
        """
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            encoded_prompt = encoding.encode(prompt)
            num_tokens = self.num_tokens_from_string(prompt, encoding_name)
            limit_size = CONTEXT_WINDOW - 2000
            if num_tokens > limit_size:
                encoded_prompt = encoded_prompt[:limit_size]
            decoded_prompt = encoding.decode(encoded_prompt)
            return decoded_prompt
        except:
            return ""

    @staticmethod
    def num_tokens_from_string(string: str, encoding_name: str = DEFAULT_ENCODING_NAME) -> int:
        """Get the number of tokens in a given text string.

        Args:
            string (str): The input text.
            encoding_name (str, optional): Model tokenizer name.

        Returns:
            int: Number of tokens in the string.
        """
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(string))
