TEMPLATE =  '''
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
                '''        

# Nombre de jour à retenir pour le compte des offres
TIME_WINDOW = 10
OUTPUT_PARSER = None