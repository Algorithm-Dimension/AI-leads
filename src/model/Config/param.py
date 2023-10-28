import pandas as pd

TEMPLATE = """
            You are analyzing the text extracted from a website with job positions : {url}.
            Using this information, give a chart with ALL the:
            - job name
            - company
            - location
            - offer date (ex. 10 days ago, 2 months ago, today, aujourd'hui, il y a 2 jours, …)
            - contact (an email address or a phone number)
            Write N.A. when the information is not available.

            The only output is a csv file (sep = ";")
            (no other text)

            url text: {html_raw_code}.
                """

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

SOURCE_LIST_PIPELINE = ["Indeed"]
JOB_LIST_PIPELINE = ["assistant-comptable"]
LOCATION = "Paris"
