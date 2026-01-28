import hashlib
import requests
import json
import os
import time
from datetime import datetime

from creer_chaine import creer_chaine

API_URL = "http://localhost:5000"
DATA_FILE = "C:/Users/elyes/Desktop/Document d'Elyes/Travail/Code/5A/Tchai/TCHAI-ELYES-MATHIEU/transactions_5000.json"

def add():
    print("=== Test d'attaque : Création d'une transaction malveillante ===\n")
    # creer_chaine()
        
    time.sleep(0.5)  # Attendre que le fichier soit écrit
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        last_t = data[-1]
        emitter = "Victim"
        receptor = "Attacker"
        amount = 100.0
        timestamp = datetime.now().isoformat()
        previous_hash = last_t["hash"]
        transaction_string = f"{emitter}{receptor}{timestamp}{amount}{previous_hash}"
        hashed = hashlib.sha256(transaction_string.encode()).hexdigest()

        data.append({
            "emitter": "Victim",
            "receptor": "Attacker",
            "amount": 100.0,
            "timestamp": datetime.now().isoformat(),
            "hash": hashed,
            "previous_hash": last_t["hash"]
        })
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        print(f"   Fichier {DATA_FILE} non trouvé")
        return

    print("\n4. Redémarrage de l'application...")
    print("   Appuyez sur Entrée après avoir redémarré...")
    input()

    try:
        response = requests.get(f"{API_URL}/transactions")
        response_data = response.json()
        if response_data['transactions'] == data:
            print("   Attaque réussie : La transaction malveillante a été acceptée dans la chaîne.")
        else: 
            print("   Attaque échouée : La transaction malveillante a été détectée et rejetée.")
    except requests.exceptions.ConnectionError:
        print("\n Serveur non accessible")

if __name__ == "__main__":
    add()