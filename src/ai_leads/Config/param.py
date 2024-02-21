import os
from datetime import datetime
from enum import Enum

import pandas as pd
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.output_parsers.enum import EnumOutputParser

ZEPHYR_URL = "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/blob/main/zephyr-7b-beta.Q5_K_M.gguf"
ZEPHYR_NAME = "zephyr-7b-beta.Q5_K_M.gguf"

LAST_UPDATE = datetime(2024, 2, 4)
BASE_DATE = datetime.today()
# BASE_DATE = datetime(2023, 12, 4)
TEMPLATE = """
            You are analyzing the text extracted from a website with job positions : {url}.
            Using this information, give a chart with ALL the:
            - job name
            - company
            - location
            - time indication (publication or last modification. e.g. il y a 2 jours,  aujourd'hui, il y a 1 semaine, 2 days ago …): 
            - contact (an email address or a phone number)
            Write N.A. when the information is not available.
            Exclude the companies that are recruitment companies

            The only output is a csv file (sep = ";")
            (no other text)

            url text: {html_raw_code}.
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

source_param = {
    "LinkedIn": [False, "https://www.linkedin.com/jobs/"],
    "Indeed": [True, """https://fr.indeed.com/q-{job}-l-{location}-emplois.html"""],
}

DF_PARAM_SEARCH = pd.DataFrame(source_param).T
DF_PARAM_SEARCH.columns = ["isDirectLink", "url"]

SOURCE_LIST_PIPELINE = ["Cadre Emploi", "Hello Work", "LinkedIn", "Indeed", "Welcome to the Jungle"]
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
LEAD_FILE_PATH = os.path.join("data", "leads_tests_tests_3_feb.csv")
JOB_FILE_PATH = os.path.join("data", "jobs_tests_3_feb.csv")
COMPANY_FILE_PATH = os.path.join("data", "table_companies.csv")
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
