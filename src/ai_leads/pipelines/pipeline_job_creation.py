import logging

import pandas as pd

from ai_leads.Config.param import JOB_FILE_PATH, JOB_LIST_PIPELINE, LOCATION, SOURCE_LIST_PIPELINE
from ai_leads.model.job_dataset_creation import JobDataFrameCreator
from ai_leads.model.navigator import WebpageScraper

# Setup logging
logger = logging.getLogger(__name__)

# Create an empty DataFrame to store job data
df_jobs = pd.DataFrame()

# Loop through each source and job in the pipelines
for platform in SOURCE_LIST_PIPELINE:
    for job in JOB_LIST_PIPELINE:
        logger.info(f"Scraping {job} jobs from {platform}")

        # Retrieve a list of URLs for the specified job and location
        url_list = WebpageScraper(platform=platform).find_url_list(job, LOCATION)

        # Loop through each URL and collect job data
        for url in url_list:
            logger.info(f"Scraping data from URL: {url}")

            # Create a DataFrame for the job from the URL
            df_job = JobDataFrameCreator().create_table_with_job(url, platform)

            # Add additional columns for position, source, and URL
            df_job["position"] = job
            df_job["source"] = platform
            df_job["url"] = url

            # Append the job data to the main DataFrame
            df_jobs = pd.concat([df_jobs, df_job])

            # Save the combined DataFrame to a CSV file
            df_jobs.to_csv(JOB_FILE_PATH, sep=";", index=False)
