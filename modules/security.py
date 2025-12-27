from cryptography.fernet import Fernet

# Générer une clé une seule fois et la sauvegarder
KEY_FILE = "data/key.key"

def generer_cle():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def charger_cle():
    with open(KEY_FILE, "rb") as f:
        return f.read()

def chiffrer(mot_de_passe):
    f = Fernet(charger_cle())
    return f.encrypt(mot_de_passe.encode()).decode()

def dechiffrer(mot_de_passe_chiffre):
    f = Fernet(charger_cle())
    return f.decrypt(mot_de_passe_chiffre.encode()).decode()
# --- IGNORE ---