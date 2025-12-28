import streamlit as st
from modules import storage, security
import pandas as pd
from urllib.parse import urlparse

def normaliser_site(site: str) -> str:
    """Extrait uniquement le domaine d'une URL ou retourne tel quel si déjà un domaine."""
    site = site.strip()
    if site.startswith("http"):
        parsed = urlparse(site)
        domaine = parsed.netloc
        # enlever 'www.' ou 'web.' si présent
        if domaine.startswith("www."):
            domaine = domaine[4:]
        if domaine.startswith("web."):
            domaine = domaine[4:]
        return domaine
    return site

def formulaire_ajout(data):
    with st.form("ajout_compte"):
        site = st.text_input("Nom du site (ex: facebook.com ou https://facebook.com)")
        identifiant = st.text_input("Identifiant")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Ajouter")
        if submit:
            if site and identifiant and mot_de_passe:
                domaine = normaliser_site(site)
                logo_url = f"https://www.google.com/s2/favicons?domain={domaine}"
                data.append({
                    "site": domaine,
                    "identifiant": identifiant,
                    "mot_de_passe": security.chiffrer(mot_de_passe),
                    "logo": logo_url
                })
                storage.sauvegarder_donnees(data)
                st.success(f"Compte pour {domaine} ajouté ✅")
            else:
                st.warning("Veuillez remplir tous les champs avant de valider.")

def afficher_comptes(data):
    """Affiche les comptes dans un tableau HTML interactif avec logos et textes combinés."""
    if data:
        comptes_affiches = []
        for compte in data:
            site = compte["site"]
            logo = compte.get("logo", "")
            identifiant = compte["identifiant"]
            mot_de_passe = security.dechiffrer(compte["mot_de_passe"])

            # Combiner logo + texte dans une seule cellule HTML
            site_affiche = f"<img src='{logo}' width='20' style='vertical-align:middle;margin-right:8px;'> {site}"

            comptes_affiches.append({
                "Site": site_affiche,
                "Identifiant": identifiant,
                "Mot de passe": mot_de_passe
            })

        df = pd.DataFrame(comptes_affiches)
        st.write("### 📋 Liste des comptes enregistrés")
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("Aucun compte enregistré pour le moment.")

def rechercher_compte(data):
    site_recherche = st.text_input("Nom du site à rechercher")
    if site_recherche:
        domaine = normaliser_site(site_recherche)
        resultats = []
        for compte in data:
            if compte["site"].lower() == domaine.lower():
                site_affiche = f"<img src='{compte.get('logo','')}' width='20' style='vertical-align:middle;margin-right:8px;'> {compte['site']}"
                resultats.append({
                    "Site": site_affiche,
                    "Identifiant": compte["identifiant"],
                    "Mot de passe": security.dechiffrer(compte["mot_de_passe"])
                })
        if resultats:
            st.success("Résultat trouvé ✅")
            df = pd.DataFrame(resultats)
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.warning("Aucun compte trouvé pour ce site.")

def supprimer_compte(data):
    site_supprimer = st.text_input("Nom du site à supprimer")
    if st.button("Supprimer"):
        domaine = normaliser_site(site_supprimer)
        nouveaux_comptes = [c for c in data if c["site"].lower() != domaine.lower()]
        if len(nouveaux_comptes) < len(data):
            storage.sauvegarder_donnees(nouveaux_comptes)
            st.success(f"Compte {domaine} supprimé ❌")
            st.experimental_rerun()
        else:
            st.warning("Aucun compte trouvé avec ce nom.")
# --- Fin des helpers UI ---
# --- IGNORE ---