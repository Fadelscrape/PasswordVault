import streamlit as st
from modules import storage, security

def formulaire_ajout(data):
    with st.form("ajout_compte"):
        site = st.text_input("Nom du site")
        identifiant = st.text_input("Identifiant")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Ajouter")
        if submit:
            data.append({
                "site": site,
                "identifiant": identifiant,
                "mot_de_passe": security.chiffrer(mot_de_passe)
            })
            storage.sauvegarder_donnees(data)
            st.success("Compte ajouté ✅")

def afficher_comptes(data):
    st.subheader("Comptes enregistrés")
    for compte in data:
        st.write(f"🌐 {compte['site']} — 👤 {compte['identifiant']}")

def rechercher_compte(data):
    site_recherche = st.text_input("Rechercher un site")
    if site_recherche:
        for compte in data:
            if compte["site"] == site_recherche:
                mdp = security.dechiffrer(compte["mot_de_passe"])
                st.info(f"Identifiant : {compte['identifiant']} | Mot de passe : {mdp}")

def supprimer_compte(data):
    site_supprimer = st.text_input("Supprimer un site")
    if st.button("Supprimer"):
        data = [c for c in data if c["site"] != site_supprimer]
        storage.sauvegarder_donnees(data)
        st.warning(f"Compte {site_supprimer} supprimé ❌")
        st.experimental_rerun()
# --- IGNORE ---