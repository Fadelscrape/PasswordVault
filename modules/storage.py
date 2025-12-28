import json
import os
import pandas as pd

FICHIER_JSON = "data/vault.json"
FICHIER_XLSX = "data/vault.xlsx"

# S'assurer que le dossier data existe
os.makedirs("data", exist_ok=True)

def charger_donnees():
    """Charge les données depuis vault.json, retourne une liste vide si fichier absent ou vide."""
    if os.path.exists(FICHIER_JSON):
        try:
            with open(FICHIER_JSON, "r") as f:
                contenu = f.read().strip()
                if contenu:  # si le fichier n'est pas vide
                    return json.loads(contenu)
        except Exception:
            return []
    return []

def sauvegarder_donnees(data):
    """Sauvegarde les données dans vault.json."""
    with open(FICHIER_JSON, "w") as f:
        json.dump(data, f, indent=4)

def exporter_excel(data):
    """Exporte les données en Excel (vault.xlsx)."""
    if data:  # éviter d'exporter un fichier vide
        df = pd.DataFrame(data)
        df.to_excel(FICHIER_XLSX, index=False)
        return FICHIER_XLSX
    else:
        return None
# --- IGNORE ---