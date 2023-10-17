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
    # Remplacez le graphique à barres par un pie chart
    # Remplacez le graphique à barres par un pie chart
    st.subheader("Nombre de postes par entreprise")
    postes_par_entreprise = data_filtered['Entreprise'].value_counts()
    st.plotly_chart(
        px.pie(postes_par_entreprise, names=postes_par_entreprise.index, values=postes_par_entreprise.values,
               title="Répartition des postes par entreprise"))

    # Autres KPI et visualisations
    # Vous pouvez ajouter d'autres KPI et visualisations en utilisant Plotly Express ou d'autres bibliothèques de visualisation.

    # 2 Exemple : Nombre de postes par lieu
    st.subheader("Nombre de postes par lieu")
    postes_par_lieu = data_filtered['Lieu'].value_counts().reset_index()
    postes_par_lieu.columns = ['Lieu', 'Nombre de postes']

    fig = px.bar(postes_par_lieu, x='Lieu', y='Nombre de postes')
    #st.plotly_chart(fig)


    # 4 - Titre du tableau de bord
    st.title("Tendances Temporelles des Offres d'Emploi")

    # Créer un graphique des tendances temporelles
    st.subheader("Évolution du Nombre d'Offres d'Emploi au Fil du Temps")
    fig = px.line(data_filtered, x="Date", title="Nombre d'Offres d'Emploi par Date")
    st.plotly_chart(fig)

    # Afficher le nombre total d'offres d'emploi pendant la période sélectionnée
    total_offres = len(data_filtered)
    st.write(f"Nombre total d'offres d'emploi : {total_offres}")


    # 5
    st.title("Analyse Comparative des Entreprises")

    # Créer une barre latérale pour sélectionner l'entreprise à comparer
    st.sidebar.header("Sélectionnez l'Entreprise")
    entreprise_selectionnee = st.sidebar.selectbox("Entreprise", df["Entreprise"].unique())

    # Filtrer les données en fonction de l'entreprise sélectionnée
    data_filtered_company = df[df["Entreprise"] == entreprise_selectionnee]

    # Afficher le nombre d'offres d'emploi de l'entreprise sélectionnée
    nombre_offres = len(data_filtered_company)
    st.subheader(f"Nombre d'Offres d'Emploi de {entreprise_selectionnee}")
    st.write(f"Nombre d'Offres d'Emploi : {nombre_offres}")

    # Créer une section pour l'analyse comparative des critères
    st.subheader("Analyse Comparative")

    # Vous pouvez ajouter différents critères ici et comparer les entreprises en fonction de ces critères.
    # Par exemple, le nombre d'offres d'emploi, la durée moyenne de publication, etc.

    # Exemple : Comparaison du nombre d'offres d'emploi par entreprise
    st.subheader("Comparaison du Nombre d'Offres d'Emploi par Entreprise")
    fig = px.bar(df, x="Entreprise", y="Poste",
                 title="Comparaison du Nombre d'Offres d'Emploi par Entreprise")
    st.plotly_chart(fig)

    #6


