import streamlit as st
import pandas as pd

# Créez une DataFrame de test
data = {'Nom': ['Alice', 'Bob', 'Charlie', 'David'],
        'Âge': [25, 30, 35, 28],
        'Ville': ['New York', 'Los Angeles', 'Chicago', 'Houston']}

df = pd.DataFrame(data)

# Titre de la page
st.title('Exemple de filtre sur une colonne de la DataFrame')

# Sélectionnez la colonne pour le filtre
colonne_filtre = st.selectbox('Sélectionnez une colonne pour le filtre', df.columns)

# Affichez la DataFrame filtrée en fonction de la colonne sélectionnée
if colonne_filtre:
    valeur_filtre = st.text_input(f'Filtrer par {colonne_filtre}', '')
    if valeur_filtre:
        df = df[df[colonne_filtre] == valeur_filtre]
        st.dataframe(df)
    else:
        st.warning('Veuillez entrer une valeur pour le filtre.')
else:
    st.warning('Veuillez sélectionner une colonne pour le filtre.')
