import streamlit as st
from modules import storage, security, ui_helpers
import os
import pandas as pd

# --- Configuration de la page ---
st.set_page_config(page_title="PasswordVault", page_icon="🔐", layout="wide")

# --- CSS responsive ---
custom_css = """
<style>
/* Sidebar style */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a73e8 0%, #0c47a1 100%);
    color: white;
    padding: 1.5em 1em;
}
[data-testid="stSidebar"] .stRadio > div {
    display: flex;
    flex-direction: column;
    gap: 0.5em;
}
[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.15);
    color: #ffffff !important;
    padding: 0.8em 1em;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: 0.3s;
    width: 100%;
    text-align: center;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.35);
    transform: scale(1.02);
}
[data-testid="stSidebar"] .stRadio input:checked + div label {
    background: #ffffff !important;
    color: #1a73e8 !important;
    font-weight: 700;
}

/* Responsive table for mobile */
@media (max-width: 768px) {
    table {
        font-size: 14px;
    }
    th, td {
        padding: 6px;
    }
    [data-testid="stSidebar"] {
        display: none; /* cacher la sidebar sur mobile */
    }
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

# --- Sidebar navigation (desktop uniquement) ---
if st.session_state.get("is_mobile", False) is False:
    st.sidebar.title("🔐 PasswordVault")
    st.sidebar.markdown("**Menu principal**")
    menu = st.sidebar.radio(
        "📂 Choisissez une page :",
        ["Accueil", "Ajouter", "Lister", "Recherche", "Suppression", "Export"]
    )
else:
    # Sur mobile, menu en haut
    menu = st.selectbox(
        "📂 Choisissez une page :",
        ["Accueil", "Ajouter", "Lister", "Recherche", "Suppression", "Export"]
    )

# --- Pages ---
if menu == "Accueil":
    st.title("🔐 PasswordVault")
    st.markdown("Bienvenue dans votre coffre-fort numérique sécurisé. Gérez vos identifiants en toute simplicité.")

    total_comptes = len(data)
    st.metric(label="Nombre total de comptes", value=total_comptes)

    if data:
        st.subheader("📊 Derniers comptes ajoutés")
        derniers = data[-5:] if len(data) > 5 else data

        if "show_home_pwds" not in st.session_state:
            st.session_state["show_home_pwds"] = False

        eye_icon = "🙈 Masquer tous" if st.session_state["show_home_pwds"] else "👁️ Afficher tous"
        if st.button(eye_icon, key="toggle_home_pwds"):
            st.session_state["show_home_pwds"] = not st.session_state["show_home_pwds"]
            st.rerun()

        comptes_affiches = []
        for compte in derniers:
            mot_de_passe = (
                security.dechiffrer(compte["mot_de_passe"])
                if st.session_state["show_home_pwds"]
                else "********"
            )
            comptes_affiches.append({
                "Site": compte["site"],
                "Identifiant": compte["identifiant"],
                "Mot de passe": mot_de_passe
            })

        df = pd.DataFrame(comptes_affiches)

        # --- Desktop : tableau HTML ---
        if not st.session_state.get("is_mobile", False):
            table_style = """
            <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #1a73e8;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
            </style>
            """
            st.markdown(table_style, unsafe_allow_html=True)
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            # --- Mobile : affichage style carte ---
            ui_helpers.afficher_style_mobile(derniers)
    else:
        st.info("Aucun compte enregistré pour le moment.")

elif menu == "Ajouter":
    st.header("➕ Ajouter un compte")
    ui_helpers.formulaire_ajout(data)

elif menu == "Lister":
    st.header("📋 Comptes enregistrés")
    if st.session_state.get("is_mobile", False):
        ui_helpers.afficher_style_mobile(data)
    else:
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
