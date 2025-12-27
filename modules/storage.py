import json
import os
import pandas as pd

FICHIER_JSON = "data/vault.json"
FICHIER_XLSX = "data/vault.xlsx"

def charger_donnees():
    if os.path.exists(FICHIER_JSON):
        with open(FICHIER_JSON, "r") as f:
            return json.load(f)
    return []

def sauvegarder_donnees(data):
    with open(FICHIER_JSON, "w") as f:
        json.dump(data, f, indent=4)

def exporter_excel(data):
    df = pd.DataFrame(data)
    df.to_excel(FICHIER_XLSX, index=False)
    return FICHIER_XLSX