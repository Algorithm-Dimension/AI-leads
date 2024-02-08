import logging

import pandas as pd

from ai_leads.Config.param import JOB_FILE_PATH, JOB_LIST_PIPELINE, LOCATION, SOURCE_LIST_PIPELINE  # noqa: E501
from ai_leads.model.job_dataset_creation import JobDataFrameCreator
from ai_leads.model.navigator import WebpageScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_jobs_and_save_to_csv():
    """Scrape job data from multiple platforms and save to a CSV file."""
    df_jobs = pd.DataFrame()

    for platform in SOURCE_LIST_PIPELINE:
        scraper = WebpageScraper(platform=platform)
        for job in JOB_LIST_PIPELINE:
            logger.info(f"Scraping {job} jobs from {platform}")
            df_jobs = scrape_jobs_from_platform(platform, job, df_jobs, scraper)
        scraper.close_driver()

    logger.info("Job data saved to CSV.")


def scrape_jobs_from_platform(platform, job, df_jobs, scraper: WebpageScraper):
    """Scrape job data from a specific platform and job type."""
    url_list = scraper.find_url_list(job, LOCATION)
    for url in url_list:
        logger.info(f"Scraping data from URL: {url}")
        df_job = JobDataFrameCreator(scraper=scraper).create_table_with_job(url, platform)
        df_job = enrich_job_data(df_job, job, platform, url)
        df_jobs = pd.concat([df_jobs, df_job])
        # Save the final DataFrame to a CSV after collecting all jobs to reduce disk I/O
    df_jobs.drop_duplicates(subset=["job name", "company", "location", "offer date", "source"], inplace=True)
    df_jobs.to_csv(JOB_FILE_PATH, sep=";", index=False)
    logger.info("Job data saved to CSV.")

    return df_jobs


def enrich_job_data(df_job, job, platform, url):
    """Enrich the job DataFrame with additional data."""
    df_job["position"] = job
    df_job["source"] = platform
    df_job["url"] = url
    return df_job


if __name__ == "__main__":
    try:
        scrape_jobs_and_save_to_csv()
    except Exception as e:
        logger.error(f"An error occurred during job scraping: {e}")
