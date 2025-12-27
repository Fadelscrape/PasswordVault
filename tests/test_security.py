from modules import security

def test_chiffrement_dechiffrement():
    mot_de_passe = "secret123"
    chiffre = security.chiffrer(mot_de_passe)
    clair = security.dechiffrer(chiffre)
    assert clair == mot_de_passe
# --- IGNORE ---