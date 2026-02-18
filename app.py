import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration
st.set_page_config(page_title="Analyse Performance", layout="wide")

st.title("📊 Dashboard : Running vs Downtime")
st.markdown("Chargez votre fichier Excel pour générer l'analyse avec correction des week-ends.")

# --- COMPOSANT D'UPLOAD ---
uploaded_file = st.file_uploader("Choisissez le fichier Excel (format .xlsx)", type=["xlsx"])

def process_data(df):
    # On renomme les colonnes selon la structure de ton fichier
    # Note : Si les noms de colonnes varient, on peut utiliser les index df.columns[0], etc.
    df.columns = ['Date', 'Jour', 'Heure_Theorique', 'Downtime']
    
    # Nettoyage
    df = df.dropna(subset=['Date'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # --- LOGIQUE MÉTIER ---
    # 1. Si c'est un weekend (samedi/dimanche), Downtime = 0
    df.loc[df['Jour'].str.lower().isin(['samedi', 'dimanche']), 'Downtime'] = 0
    
    # 2. Calcul du Running (Heure Théorique - Downtime)
    df['Running'] = (df['Heure_Theorique'] - df['Downtime']).clip(lower=0)
    
    return df

if uploaded_file is not None:
    try:
        # Lecture du fichier Excel
        df_raw = pd.read_excel(uploaded_file)
        df = process_data(df_raw)

        # --- FILTRES ---
        st.sidebar.header("Filtres")
        date_range = st.sidebar.date_input("Période d'analyse", [df['Date'].min(), df['Date'].max()])

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
                df_monthly = filtered_df.copy()
                df_monthly['Mois'] = df_monthly['Date'].dt.strftime('%Y-%m')
                monthly_data = df_monthly.groupby('Mois')[['Running', 'Downtime']].sum().reset_index()
                
                fig_bar = px.bar(monthly_data, x='Mois', y=['Running', 'Downtime'],
                                barmode='group',
                                color_discrete_map={"Running": "#00CC96", "Downtime": "#EF553B"},
                                title="Total Mensuel (Heures)")
                st.plotly_chart(fig_bar, use_container_width=True)

            # Tableau de données
            with st.expander("Voir les données corrigées"):
                st.dataframe(filtered_df)
    
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.info("Vérifiez que le fichier Excel respecte bien le format : Date, Jour, Heure Théorique, Downtime.")
else:
    st.info("Veuillez uploader un fichier Excel pour commencer.")
