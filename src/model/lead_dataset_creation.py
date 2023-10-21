import logging
import numpy as np
import pandas as pd
import dateparser
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadDataFrameConverter:
    """
    A class to handle conversion of a dataframe into a lead dataframe.

    Attributes:
        df (pd.DataFrame): The input dataframe.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the LeadDataFrameConverter with a dataframe.

        Args:
            df (pd.DataFrame): The input dataframe.
        """
        self.df = df.copy()
        self.df.columns = [col.strip() for col in self.df.columns]

    def convert_time_column(self, col: str):
        """
        Converts a column in the dataframe from temporal strings to days.

        Args:
            col (str): The name of the column to convert.
        """
        self.df[f"{col} clean"] = self.df[col].apply(self.convert_to_days)

    def convert_to_lead_dataframe(self, time_window: int) -> pd.DataFrame:
        """
        Convert the dataframe with all job offers into a lead dataframe, filtering by a specific time window.

        Args:
            time_window (int): The maximum number of days since an offer was posted.

        Returns:
            pd.DataFrame: The lead dataframe.
        """
        self.convert_time_column("offer date")
        
        self.df = self.df.loc[self.df["offer date clean"] <= time_window]
        
        df_lead = pd.DataFrame(self.df["company"].value_counts()).reset_index()
        df_lead.columns = ["Entreprise", f"Nombre d'offres postés les {time_window} derniers jours"]
        df_lead["Contacté"] = "Non"
        df_lead["Téléphone"] = np.nan
        df_lead["Email"] = np.nan
        df_lead.sort_values(by=f"Nombre d'offres postés les {time_window} derniers jours", ascending=False, inplace=True)
        
        return df_lead

    @staticmethod
    def convert_to_days(temp_string: str) -> int:
        """
        Convert a temporal string into a number of days since that date.

        Args:
            temp_string (str): The temporal string, e.g., "il y a 3 jours".

        Returns:
            int: Number of days since the date represented by temp_string.
        """
        parsed_date = dateparser.parse(temp_string, languages=['fr', 'en'])
        if parsed_date:
            today = datetime.now()
            delta = today - parsed_date
            return int(delta.days)
        else:
            logger.debug(f"Failed to parse date from string: {temp_string}")
            return np.nan