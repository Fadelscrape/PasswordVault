from modules import storage

def test_sauvegarde_et_chargement(tmp_path):
    fichier = tmp_path / "vault.json"
    data = [{"site": "test.com", "identifiant": "user", "mot_de_passe": "pass"}]
    storage.sauvegarder_donnees(data)
    result = storage.charger_donnees()
    assert result[0]["site"] == "test.com"
    assert result[0]["identifiant"] == "user"
    assert result[0]["mot_de_passe"] == "pass"