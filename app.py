import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration
st.set_page_config(page_title="Analyse Performance", layout="wide")

st.title("📊 Dashboard : Running vs Downtime")
st.markdown("Analyse des indicateurs de performance avec correction automatique des week-ends.")

@st.cache_data
def load_and_clean_data():
    # Chargement
    file_path = 'running vs downtime.xlsx - Feuil1.csv'
    df = pd.read_csv(file_path)
    
    # Renommer les colonnes (basé sur ton fichier)
    df.columns = ['Date', 'Jour', 'Heure_Theorique', 'Downtime']
    
    # Nettoyage
    df = df.dropna(subset=['Date'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # --- LOGIQUE MÉTIER DEMANDÉE ---
    # 1. Si c'est un weekend (samedi/dimanche), Downtime = 0
    weekend_mask = df['Jour'].str.lower().isin(['samedi', 'dimanche'])
    df.loc[weekend_mask, 'Downtime'] = 0
    
    # 2. Calcul du Running (Heure Théorique - Downtime)
    # On s'assure que le running ne soit pas négatif
    df['Running'] = (df['Heure_Theorique'] - df['Downtime']).apply(lambda x: x if x > 0 else 0)
    
    return df

try:
    df = load_and_clean_data()

    # Sidebar pour le filtrage
    st.sidebar.header("Filtres")
    start_date = df['Date'].min()
    end_date = df['Date'].max()
    
    date_range = st.sidebar.date_input("Période d'analyse", [start_date, end_date])

    if len(date_range) == 2:
        mask = (df['Date'] >= pd.Timestamp(date_range[0])) & (df['Date'] <= pd.Timestamp(date_range[1]))
        filtered_df = df.loc[mask]

        # --- GRAPHIQUES ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Évolution Temporelle")
            fig_line = px.line(filtered_df, x='Date', y=['Running', 'Downtime'],
                             color_discrete_map={"Running": "#00CC96", "Downtime": "#EF553B"},
                             title="Running vs Downtime par Jour")
            st.plotly_chart(fig_line, use_container_width=True)

        with col2:
            st.subheader("Répartition Cumulée")
            # Aggregation par mois pour le second graph
            df_monthly = filtered_df.copy()
            df_monthly['Mois'] = df_monthly['Date'].dt.strftime('%Y-%m')
            monthly_data = df_monthly.groupby('Mois')[['Running', 'Downtime']].sum().reset_index()
            
            fig_bar = px.bar(monthly_data, x='Mois', y=['Running', 'Downtime'],
                            barmode='group',
                            color_discrete_map={"Running": "#00CC96", "Downtime": "#EF553B"},
                            title="Total Mensuel (Heures)")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Tableau de données
        with st.expander("Voir les données détaillées"):
            st.write(filtered_df)
    else:
        st.info("Veuillez sélectionner une date de début et de fin.")

except Exception as e:
    st.error(f"Erreur : {e}")
