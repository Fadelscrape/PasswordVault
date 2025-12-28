import streamlit as st
from modules import storage, security, ui_helpers
import os
import pandas as pd

# --- Configuration de la page ---
st.set_page_config(page_title="PasswordVault", page_icon="🔐", layout="wide")

# --- CSS personnalisé ---
custom_css = """
<style>
body {
    background-color: #f5f7fa;
    font-family: 'Segoe UI', sans-serif;
    color: #2c3e50;
}
h1, h2, h3 {
    color: #1a73e8;
    font-weight: 600;
}
.stButton>button {
    background-color: #1a73e8;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.6em 1.2em;
    font-size: 16px;
    font-weight: 500;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #0c47a1;
    transform: scale(1.05);
}
.stDataFrame, .stTable {
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
}
thead tr {
    background-color: #1a73e8;
    color: white;
    font-weight: bold;
}
tbody tr:nth-child(even) {
    background-color: #f2f6fc;
}
tbody tr:hover {
    background-color: #eaf1fb;
}
.stAlert {
    border-radius: 8px;
    padding: 0.8em;
    font-weight: 500;
}

/* --- Sidebar premium --- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a73e8 0%, #0c47a1 100%);
    color: white;
    padding: 1.5em 1em;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 600;
}
[data-testid="stSidebar"] .stRadio > label {
    color: #ffffff !important;
    font-size: 16px;
    font-weight: 500;
}
[data-testid="stSidebar"] .stButton>button {
    background-color: #ffffff;
    color: #1a73e8;
    border-radius: 8px;
    border: none;
    padding: 0.5em 1em;
    font-size: 14px;
    font-weight: 600;
    transition: 0.3s;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background-color: #f2f6fc;
    color: #0c47a1;
    transform: scale(1.05);
}
[data-testid="stSidebar"] hr {
    border: 1px solid #ffffff33;
}
[data-testid="stSidebar"] p {
    color: #eaf1fb !important;
    font-size: 14px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Vérifier la clé de chiffrement ---
if not os.path.exists("data/key.key"):
    security.generer_cle()

# --- Charger les données ---
try:
    data = storage.charger_donnees()
except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")
    data = []

# --- Sidebar navigation ---
st.sidebar.title("🔐 PasswordVault")
st.sidebar.markdown("**Menu principal**")
menu = st.sidebar.radio("📂 Choisissez une page :", ["Accueil", "Ajouter", "Lister", "Recherche", "Suppression", "Export"])

# --- Pages ---
if menu == "Accueil":
    st.title("🔐 PasswordVault")
    st.markdown("Bienvenue dans votre coffre-fort numérique sécurisé. Gérez vos identifiants en toute simplicité.")

    # --- Mini tableau de bord ---
    total_comptes = len(data)
    st.metric(label="Nombre total de comptes", value=total_comptes)

    if data:
        st.subheader("📊 Derniers comptes ajoutés")
        derniers = data[-5:] if len(data) > 5 else data
        comptes_affiches = []
        for compte in derniers:
            comptes_affiches.append({
                "Site": compte["site"],
                "Identifiant": compte["identifiant"],
                "Mot de passe": security.dechiffrer(compte["mot_de_passe"])
            })
        df = pd.DataFrame(comptes_affiches)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun compte enregistré pour le moment.")

elif menu == "Ajouter":
    st.header("➕ Ajouter un compte")
    ui_helpers.formulaire_ajout(data)

elif menu == "Lister":
    st.header("📋 Comptes enregistrés")
    ui_helpers.afficher_comptes(data)

elif menu == "Recherche":
    st.header("🔎 Rechercher un compte")
    ui_helpers.rechercher_compte(data)

elif menu == "Suppression":
    st.header("🗑️ Supprimer un compte")
    ui_helpers.supprimer_compte(data)

elif menu == "Export":
    st.header("📤 Exporter les données")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Exporter en Excel"):
            try:
                fichier_excel = storage.exporter_excel(data)
                if fichier_excel:
                    with open(fichier_excel, "rb") as f:
                        st.download_button("📥 Télécharger Excel", f, file_name="vault.xlsx")
                    st.success("Export Excel réalisé avec succès ✅")
                else:
                    st.info("Aucune donnée à exporter.")
            except Exception as e:
                st.error(f"Erreur lors de l'export Excel : {e}")

    with col2:
        if st.button("Exporter en JSON"):
            try:
                fichier_json = "data/vault.json"
                if os.path.exists(fichier_json):
                    with open(fichier_json, "rb") as f:
                        st.download_button("📥 Télécharger JSON", f, file_name="vault.json")
                    st.success("Export JSON réalisé avec succès ✅")
                else:
                    st.info("Aucune donnée à exporter.")
            except Exception as e:
                st.error(f"Erreur lors de l'export JSON : {e}")
# --- Fin de l'application ---
