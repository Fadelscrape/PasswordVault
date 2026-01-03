import streamlit as st
from modules import storage, security
import pandas as pd
from urllib.parse import urlparse

def normaliser_site(site: str) -> str:
    site = site.strip()
    if site.startswith("http"):
        parsed = urlparse(site)
        domaine = parsed.netloc
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
    """Affiche les comptes avec un petit bouton œil compact pour chaque mot de passe."""
    if data:
        for i, compte in enumerate(data):
            site = compte["site"]
            logo = compte.get("logo", "")
            identifiant = compte["identifiant"]

            key = f"show_pwd_{i}"
            if key not in st.session_state:
                st.session_state[key] = False

            if st.session_state[key]:
                mot_de_passe = security.dechiffrer(compte["mot_de_passe"])
                eye_icon = "🙈"
            else:
                mot_de_passe = "********"
                eye_icon = "👁️"

            cols = st.columns([2, 2, 2, 0.2])
            with cols[0]:
                st.markdown(
                    f"<img src='{logo}' width='20' style='vertical-align:middle;margin-right:8px;'> "
                    f"<a href='https://{site}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{site}</a>",
                    unsafe_allow_html=True
                )
            with cols[1]:
                st.write(identifiant)
            with cols[2]:
                st.write(mot_de_passe)
            with cols[3]:
                if st.button(eye_icon, key=f"btn_{i}"):
                    st.session_state[key] = not st.session_state[key]
                    st.rerun()
    else:
        st.info("Aucun compte enregistré pour le moment.")

def rechercher_compte(data):
    """Recherche un compte par site et affiche le résultat avec bouton œil compact."""
    site_recherche = st.text_input("Nom du site à rechercher")
    if site_recherche:
        domaine = normaliser_site(site_recherche)
        resultats = []
        for i, compte in enumerate(data):
            if compte["site"].lower() == domaine.lower():
                key = f"show_search_pwd_{i}"
                if key not in st.session_state:
                    st.session_state[key] = False

                if st.session_state[key]:
                    mot_de_passe = security.dechiffrer(compte["mot_de_passe"])
                    eye_icon = "🙈"
                else:
                    mot_de_passe = "********"
                    eye_icon = "👁️"

                site_affiche = (
                    f"<img src='{compte.get('logo','')}' width='20' style='vertical-align:middle;margin-right:8px;'> "
                    f"<a href='https://{compte['site']}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{compte['site']}</a>"
                )

                cols = st.columns([2, 2, 2, 0.2])
                with cols[0]:
                    st.markdown(site_affiche, unsafe_allow_html=True)
                with cols[1]:
                    st.write(compte["identifiant"])
                with cols[2]:
                    st.write(mot_de_passe)
                with cols[3]:
                    if st.button(eye_icon, key=f"search_btn_{i}"):
                        st.session_state[key] = not st.session_state[key]
                        st.rerun()
                resultats.append(compte)
        if not resultats:
            st.warning("Aucun compte trouvé pour ce site.")

def afficher_style_mobile(data):
    """Affichage façon mobile : icône + domaine cliquable + identifiant + flèche."""
    st.markdown("### 🔐 Vos comptes enregistrés")
    for i, compte in enumerate(data):
        site = compte["site"]
        identifiant = compte["identifiant"]
        logo = compte.get("logo", "")
        url = f"https://{site}"

        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 15px;border-bottom:1px solid #eee;">
            <div style="display:flex;align-items:center;gap:10px;">
                <img src="{logo}" width="20" style="vertical-align:middle;">
                <div>
                    <a href="{url}" target="_blank" style="text-decoration:none;color:#1a73e8;font-weight:600;">{site}</a><br>
                    <span style="font-size:13px;color:#555;">{identifiant}</span>
                </div>
            </div>
            <div>
                <span style="font-size:18px;">➡️</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def supprimer_compte(data):
    site_supprimer = st.text_input("Nom du site à supprimer")
    if st.button("Supprimer"):
        domaine = normaliser_site(site_supprimer)
        nouveaux_comptes = [c for c in data if c["site"].lower() != domaine.lower()]
        if len(nouveaux_comptes) < len(data):
            storage.sauvegarder_donnees(nouveaux_comptes)
            st.success(f"Compte {domaine} supprimé ❌")
            st.rerun()
        else:
            st.warning("Aucun compte trouvé avec ce nom.")
# --- Fin des helpers UI ---
def afficher_derniers_comptes(data):
    """Affiche les 5 derniers comptes ajoutés avec option pour afficher/masquer tous les mots de passe."""
    if data:
        st.subheader("📊 Derniers comptes ajoutés")
        derniers = data[-5:] if len(data) > 5 else data

        # --- état global pour afficher/masquer ---
        if "show_home_pwds" not in st.session_state:
            st.session_state["show_home_pwds"] = False

        # bouton global
        eye_icon = "🙈 Masquer tous" if st.session_state["show_home_pwds"] else "👁️ Afficher tous"
        if st.button(eye_icon, key="toggle_home_pwds"):
            st.session_state["show_home_pwds"] = not st.session_state["show_home_pwds"]
            st.rerun()

        # construire le tableau
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

        # --- Style du tableau ---
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
        st.info("Aucun compte enregistré pour le moment.")