import logging
import numpy as np
import pandas as pd
import dateparser
from datetime import datetime
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_days(temp_string):
        # Utilisez dateparser pour analyser la chaîne temporelle et obtenir une date
        parsed_date = dateparser.parse(temp_string, languages=['fr', 'en'])
        if parsed_date:
            # Calculez la différence en jours par rapport à la date actuelle
            today = datetime.now()
            delta = today - parsed_date
            return int(delta.days)
        else:
            # Si la conversion a échoué, retournez NaN ou une autre valeur par défaut
            return np.nan

def convert_time_column(df,col):
    df[f"{col} clean"] = df[col].apply(convert_to_days)

def convert_to_lead_dataframe(df, time_window=None):
    df_curr = df.copy()
    df_curr.columns = [col.strip() for col in df_curr.columns]
    convert_time_column(df_curr,"offer date")
    print(df_curr)
    # On ne garde que les offre postées il y a moins de 10 jours
    df_curr = df_curr.loc[df_curr["offer date clean"] <= time_window]
    df_lead = pd.DataFrame(df_curr["company"].value_counts()).reset_index()
    df_lead.columns = ["Entreprise", f"Nombre d'offres postés les {time_window} derniers jours"]
    df_lead["Contacté"] = "Non"
    df_lead["Téléphone"] = np.nan
    df_lead["Email"] = np.nan
    df_lead.sort_values(by=f"Nombre d'offres postés les {time_window} derniers jours", ascending=False, inplace=True)
    return(df_lead)