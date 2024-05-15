import os
from datetime import datetime
from enum import Enum

import pandas as pd
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.output_parsers.enum import EnumOutputParser

MODEL_NAME = "llama3-8b-8192"  # gpt-3.5-turbo-16k, llama3-8b-8192

# Constants
DEFAULT_ENCODING_NAME = "cl100k_base"
CONTEXT_WINDOW = 8192
DEFAULT_RESEARCH_TYPE_THRESHOLD = 2

LAST_UPDATE = datetime(2024, 2, 4)
BASE_DATE = datetime.today()
# BASE_DATE = datetime(2023, 12, 4)
TEMPLATE = """
    You are analyzing the text extracted from a website that lists job positions. Use the provided HTML content to extract and compile data into a chart. 

    Requirements for the chart:
    - job name
    - company
    - location
    - time_indication (Ne mélange pas le français et l'anglais:
                        e.g., Si c'est en anglais : "2 days ago", "today","1 week ago" …
                        e.g. Si c'est en français : "il y a deux jours" , "aujourd'hui",
                        "il y a une semaine", "il y a plus de 30 jours" …)

    Write 'N.A.' where information is not available.

    The only final output should be a CSV file with each field separated by a semicolon (';') the colums are:
    ["job name";"company";"location";"time_indication"]. 

    Source URL: {url}
    Raw HTML content: {html_raw_code}
"""


template_verif = (
    "Please carefully read the following text coming from the web and answer strictly based on the information contained within the text."
    "Text: {html_raw_code}"
    "1. is {company} a company specialized in recruitment/HR/job search …? ('Yes' / 'No')"
    "{format_instructions}"
)
output_parser_verif = StructuredOutputParser.from_response_schemas(
    [ResponseSchema(name="isRecruitmentCompany", description="Answer to question 1")]
)

# Nombre de jour à retenir pour le compte des offres
TIME_WINDOW = 10
OUTPUT_PARSER = None
INDEED_NUMBER_PAGE = 3
LINKEDIN_NUMBER_SCROLL = 10

SOURCE_LIST_PIPELINE = [
    "Hello Work",
    "LinkedIn",
    "Indeed",
    "Cadre Emploi",
    "Welcome to the Jungle",
]
JOB_LIST_PIPELINE = [
    "Acheteur",
    "Assistant administratif",
    "Assistant ADV export",
    "Assistant de Direction",
    "Assistant formation",
    "Assistant SAV",
    "Assistant(e) juridique",
    "Business Developer",
    "Gestionnaire back office",
    "Assistant Achat",
    "Assistant Administratif polyvalent",
    "Assistant Commercial",
    "Assistant de Gestion",
    "Assistant RH",
    "Assistant Services Generaux",
    "Assistant Manager",
    "Chargé de mission RH",
    "Documentaliste",
    "Hôte/Hôtesse D'accueil",
    "Office Manager",
]

# JOB_LIST_PIPELINE = ["Acheteur"]
# SOURCE_LIST_PIPELINE = ["Indeed"]

LOCATION = "Paris"

WAIT_TIME = 5
N_PROBA = 4
DATA_RECRUITING_PATH = os.path.join("data", "list_recruiting_company.txt")
DATA_NON_RECRUITING_PATH = os.path.join("data", "list_non_recruiting_company.txt")
DATA_IDF_CITY_PATH = os.path.join("data", "list_city_idf.txt")
DATA_LOCATION_PATH = os.path.join("data", "list_idf_locations.txt")
LEAD_FILE_PATH = os.path.join("data", "leads_tests_5_may_groq.csv")
JOB_FILE_PATH = os.path.join("data", "jobs_tests_5_may_groq.csv")
COMPANY_FILE_PATH = os.path.join("data", "table_companies_groq.csv")
CONTACT_FILE_PATH = os.path.join("data", "table_contact_test.csv")


class CompanyActivity(Enum):
    RECRUITING = "Recruitment"
    FORMATION_ECOLE = "Formation/Education"
    OTHER = "Other"


template_find_activity = """
    What is the activity sector of the company, according to this text ?
    > Text: {html_raw_code}
    Please, answer using the following instructions. Don't do anything else
    Instructions: {format_instructions}"""

enum_parser_activity = EnumOutputParser(enum=CompanyActivity)

SPORT_WEBSITE_LIST = [
    "https://www.lequipe.fr",
    "https://www.eurosport.fr",
    "https://www.sport.fr",
    "https://www.sofoot.com",
    "https://www.goal.com/fr",
    "https://www.francefootball.fr",
    "https://www.football.fr",
    "https://www.intersport.fr",
    "https://sportsmanor.com",
]
