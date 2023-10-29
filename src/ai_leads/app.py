import streamlit as st
from streamlit_login_auth_ui.widgets import __login__
import pandas as pd
import plotly.express as px
import datetime


from st_aggrid import AgGrid


__login__obj = __login__(auth_token = "courier_auth_token",
                    company_name = "Shims",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')


def print_dataframe(df):
    st.title('Mes leads')
    st.dataframe(df)

    st.subheader('Afficher uniquement la colonne "Âge"')
    st.write(df['Âge'])


if __name__ == '__main__':
    #LOGGED_IN = __login__obj.build_login_ui()
    #if LOGGED_IN == True:

    types_de_donnees = {'prenom': str, 'age': str, 'job': str}

    df = pd.read_csv("/Users/remyadda/Desktop/AD/AlgoDimension/Projets/Actuels/AI-leads/src/df.csv",
                     sep=';', dtype=types_de_donnees, parse_dates=["Date"])


    # Créez une zone de formulaire Streamlit
    with st.form(key='my_form'):
        # Ajoutez un champ de texte pour le nom de la nouvelle colonne
        nom_colonne = st.text_input('Nom de la nouvelle colonne :')

        # Ajoutez un bouton de soumission dans le formulaire
        soumettre = st.form_submit_button('Ajouter')

    # Lorsque le formulaire est soumis, vérifiez si un nom de colonne a été fourni
    if soumettre:
        if nom_colonne:
            # Ajoutez la nouvelle colonne 'ok' avec des valeurs vides
            df[nom_colonne] = [' ']*len(df)
            # Stockez la DataFrame mise à jour dans la session
            st.session_state.df = df

    df_edit = st.data_editor(df)
    df_edit.to_csv("/Users/remyadda/Desktop/AD/AlgoDimension/Projets/Actuels/AI-leads/src/df.csv",
                   sep=';', index=False)

    #TODO: besoin de cliquer deux fois sur les cases pr que les modif soient prises en compte

    # Page d'accueil
    st.title("Dashboard des offres d'emploi")

    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # Sidebar pour la sélection de l'intervalle de temps
    st.sidebar.header("Sélectionnez l'intervalle de temps")

    # Spécifiez les valeurs minimales et maximales pour les dates
    date_min = st.sidebar.date_input("Date de début", min_value=datetime.date(2013, 10, 16))
    date_max = st.sidebar.date_input("Date de fin", max_value=datetime.date(2023, 11, 21))

    # Filtrer les données en fonction de l'intervalle de temps sélectionné
    data_filtered = df[(df['Date'] >= date_min) & (df['Date'] <= date_max)]
    # Afficher le nombre de postes par entreprise
    st.subheader("Nombre de postes par entreprise")
    postes_par_entreprise = data_filtered['Entreprise'].value_counts()
    st.bar_chart(postes_par_entreprise)

    # Afficher une table des données filtrées
    st.subheader("Données filtrées")
    st.dataframe(data_filtered)

    # Autres KPI et visualisations
    # Vous pouvez ajouter d'autres KPI et visualisations en utilisant Plotly Express ou d'autres bibliothèques de visualisation.

    # Exemple : Nombre de postes par lieu
    st.subheader("Nombre de postes par lieu")
    postes_par_lieu = data_filtered['Lieu'].value_counts().reset_index()
    postes_par_lieu.columns = ['Lieu', 'Nombre de postes']

    fig = px.bar(postes_par_lieu, x='Lieu', y='Nombre de postes')
    st.plotly_chart(fig)







