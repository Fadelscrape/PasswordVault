import streamlit as st
from modules import storage, security
import pandas as pd
from urllib.parse import urlparse

# =====================================================
# Utils
# =====================================================
def normaliser_site(site: str) -> str:
    site = site.strip()
    if site.startswith("http"):
        parsed = urlparse(site)
        domaine = parsed.netloc
        for prefix in ["www.", "web."]:
            if domaine.startswith(prefix):
                domaine = domaine[len(prefix):]
        return domaine
    return site


def get_logo(compte):
    """Retourne toujours un logo (évite KeyError)"""
    return compte.get(
        "logo",
        f"https://www.google.com/s2/favicons?domain={compte['site']}"
    )


# =====================================================
# Formulaire ajout (avec reset auto + message persistant)
# =====================================================
def formulaire_ajout(data):
    # Initialiser les clés de formulaire si absentes
    if "site_input" not in st.session_state:
        st.session_state["site_input"] = ""
    if "identifiant_input" not in st.session_state:
        st.session_state["identifiant_input"] = ""
    if "motdepasse_input" not in st.session_state:
        st.session_state["motdepasse_input"] = ""
    if "reset_form" not in st.session_state:
        st.session_state["reset_form"] = False

    # Réinitialiser les champs si demandé (après un ajout)
    if st.session_state["reset_form"]:
        st.session_state["site_input"] = ""
        st.session_state["identifiant_input"] = ""
        st.session_state["motdepasse_input"] = ""
        st.session_state["reset_form"] = False

    with st.form("ajout_compte"):
        site = st.text_input(
            "Nom du site (ex: facebook.com ou https://facebook.com)",
            key="site_input"
        )
        identifiant = st.text_input("Identifiant", key="identifiant_input")
        mot_de_passe = st.text_input("Mot de passe", type="password", key="motdepasse_input")

        submit = st.form_submit_button("➕ Ajouter")

        if submit:
            if site and identifiant and mot_de_passe:
                domaine = normaliser_site(site)

                data.append({
                    "site": domaine,
                    "identifiant": identifiant,
                    "mot_de_passe": security.chiffrer(mot_de_passe),
                    "logo": f"https://www.google.com/s2/favicons?domain={domaine}"
                })

                storage.sauvegarder_donnees(data)
                # ✅ Stocker le message et demander le reset du formulaire
                st.session_state["message"] = f"✅ Le site **{domaine}** avec l’identifiant **{identifiant}** a été ajouté avec succès."
                st.session_state["reset_form"] = True
                st.rerun()
            else:
                st.warning("Veuillez remplir tous les champs.")

    # ✅ Afficher le message si présent (fallback local si app.py ne le gère pas)
    if "message" in st.session_state:
        st.success(st.session_state["message"])
        del st.session_state["message"]


# =====================================================
# Recherche
# =====================================================
def rechercher_compte(data):
    site_recherche = st.text_input("Nom du site")

    if site_recherche:
        domaine = normaliser_site(site_recherche)

        resultats = [
            compte for compte in data
            if compte["site"].lower() == domaine.lower()
        ]

        if not resultats:
            st.warning("Aucun compte trouvé.")
            return

        for i, compte in enumerate(resultats):
            afficher_ligne_compte(compte, i, prefix="search")


# =====================================================
# Liste desktop avec œil
# =====================================================
def afficher_comptes(data):
    if not data:
        st.info("Aucun compte enregistré.")
        return

    for i, compte in enumerate(data):
        afficher_ligne_compte(compte, i)


def afficher_ligne_compte(compte, index, prefix="main"):
    key = f"{prefix}_show_pwd_{index}"
    if key not in st.session_state:
        st.session_state[key] = False

    mot_de_passe = (
        security.dechiffrer(compte["mot_de_passe"])
        if st.session_state[key]
        else "********"
    )
    eye_icon = "🙈" if st.session_state[key] else "👁️"

    logo = get_logo(compte)

    cols = st.columns([2.5, 2, 2, 0.3])

    with cols[0]:
        st.markdown(
            f"<img src='{logo}' width='20' style='vertical-align:middle;margin-right:8px;'> "
            f"<a href='https://{compte['site']}' target='_blank' "
            f"style='text-decoration:none;color:#1a73e8;'>"
            f"{compte['site']}</a>",
            unsafe_allow_html=True
        )

    with cols[1]:
        st.write(compte["identifiant"])

    with cols[2]:
        st.write(mot_de_passe)

    with cols[3]:
        if st.button(eye_icon, key=f"{prefix}_btn_{index}"):
            st.session_state[key] = not st.session_state[key]
            st.rerun()


# =====================================================
# 🔥 Affichage MOBILE (comme l’image)
# =====================================================
def afficher_style_mobile(data):
    st.markdown("### 🔐 Vos comptes")

    st.markdown("""
    <style>
    .account-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 16px;
        border-bottom: 1px solid #eee;
        transition: background-color 0.2s ease;
    }
    .account-row:hover {
        background-color: #f7f9fc;
    }
    .account-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .account-site {
        font-weight: 600;
        color: #202124;
    }
    .account-sub {
        font-size: 13px;
        color: #5f6368;
    }
    .arrow {
        font-size: 18px;
        color: #5f6368;
    }
    </style>
    """, unsafe_allow_html=True)

    if not data:
        st.info("Aucun compte enregistré.")
        return

    for compte in data:
        logo = get_logo(compte)

        st.markdown(f"""
        <a href="https://{compte['site']}" target="_blank" style="text-decoration:none;">
            <div class="account-row">
                <div class="account-left">
                    <img src="{logo}" width="22">
                    <div>
                        <div class="account-site">{compte['site']}</div>
                        <div class="account-sub">{compte['identifiant']}</div>
                    </div>
                </div>
                <div class="arrow">▶</div>
            </div>
        </a>
        """, unsafe_allow_html=True)


# =====================================================
# Suppression (par site OU identifiant) avec message persistant
# =====================================================
def supprimer_compte(data):
    site_supprimer = st.text_input("Nom du site à supprimer (optionnel)")
    identifiant_supprimer = st.text_input("Identifiant à supprimer (optionnel)")

    if st.button("Supprimer"):
        domaine = normaliser_site(site_supprimer) if site_supprimer else None

        nouveaux = []
        supprimes = []

        for c in data:
            condition_site = domaine and c["site"].lower() == domaine.lower()
            condition_identifiant = identifiant_supprimer and c["identifiant"].lower() == identifiant_supprimer.lower()

            if condition_site or condition_identifiant:
                supprimes.append(c)
            else:
                nouveaux.append(c)

        if supprimes:
            storage.sauvegarder_donnees(nouveaux)
            # Si plusieurs suppressions, on affiche le dernier message (ou concaténer si tu préfères)
            dernier = supprimes[-1]
            st.session_state["message"] = f"✅ Le site **{dernier['site']}** avec l’identifiant **{dernier['identifiant']}** a été supprimé."
            st.rerun()
        else:
            st.warning("Aucun compte correspondant trouvé.")

    # ✅ Afficher le message si présent (fallback local)
    if "message" in st.session_state:
        st.success(st.session_state["message"])
        del st.session_state["message"]


# =====================================================
# Suppression TOTALE avec message persistant
# =====================================================
def supprimer_tous_comptes(data):
    st.markdown("### ⚠️ Supprimer TOUS les comptes")

    if st.button("🗑️ Supprimer tout"):
        storage.sauvegarder_donnees([])  # on vide la base
        st.session_state["message"] = "✅ Tous les comptes ont été supprimés."
        st.rerun()

    # ✅ Afficher le message si présent (fallback local)
    if "message" in st.session_state:
        st.success(st.session_state["message"])
        del st.session_state["message"]


# =====================================================
# Derniers comptes
# =====================================================
def afficher_derniers_comptes(data):
    if not data:
        st.info("Aucun compte enregistré.")
        return

    st.subheader("📊 Derniers comptes ajoutés")
    derniers = data[-5:]

    if "show_home_pwds" not in st.session_state:
        st.session_state["show_home_pwds"] = False

    label = "🙈 Masquer" if st.session_state["show_home_pwds"] else "👁️ Afficher"
    if st.button(label):
        st.session_state["show_home_pwds"] = not st.session_state["show_home_pwds"]
        st.rerun()

    rows = []
    for c in derniers:
        rows.append({
            "Site": c["site"],
            "Identifiant": c["identifiant"],
            "Mot de passe": security.dechiffrer(c["mot_de_passe"])
            if st.session_state["show_home_pwds"]
            else "********"
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)
