import logging
import pandas as pd
from ai_leads.Config.param import SOURCE_LIST_PIPELINE, JOB_LIST_PIPELINE, LOCATION, JOB_FILE_PATH
from ai_leads.model.navigator import WebpageScraper
from ai_leads.model.job_dataset_creation import JobDataFrameCreator

# Setup logging
logger = logging.getLogger(__name__)

df_jobs = pd.DataFrame()

for platform in SOURCE_LIST_PIPELINE:
    dict_df_jobs = {}
    location = LOCATION
    for job in JOB_LIST_PIPELINE:
        logger.info(f"{platform}, {job}")
        url_list = WebpageScraper(platform=platform).find_url_list(job, location)
        for url in url_list:
            logger.info("We scrap this url: %s", url)
            df_job = JobDataFrameCreator().create_table_with_job(url, platform)
            df_job["position"] = job
            df_job["source"] = platform
            df_job["url"] = url
            df_jobs = pd.concat([df_jobs, df_job])
            # print("df_jobs =", df_job)
            df_jobs.to_csv(JOB_FILE_PATH, sep=";")
