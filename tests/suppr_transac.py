import requests
import json
import os
import time

API_URL = "http://localhost:5000"
DATA_FILE = "C:/Users/elyes/Desktop/Document d'Elyes/Travail/Code/5A/Tchai/TCHAI-ELYES-MATHIEU/transactions.json"

def suppr_transac():
    print("=== Test d'attaque : Suppression d'une transaction ===\n")
    
    # 1. Créer une transaction légitime
    print("1. Création d'une chaine de transaction")
    transaction = {"emitter": "Bought", "receptor": "Alice", "amount": 50}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
    transaction = {"emitter": "Miner", "receptor": "Bob", "amount": 500}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
    transaction = {"emitter": "Miner", "receptor": "Alice", "amount": 50}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
    transaction = {"emitter": "Alice", "receptor": "Bob", "amount": 100}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
        

    # 2. Attaque : Supprimer directement le fichier
    print("\n3. Suppression directe du fichier...")
    time.sleep(0.5)  # Attendre que le fichier soit écrit
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        transaction_supprime = data[2]
        print(f"   Transactions avant suppression: {data}\n")
        data.remove(data[2])
        # prendre les data après celle supprimée
        transactions_a_supprimer = []
        for d in data[2:]:
            transactions_a_supprimer.append(d)
        print(f"   Transactions après suppression: {data}\n" )
        print(f"   Transactions à supprimer pour cohérence: {transactions_a_supprimer}\n")
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        print(f"   Fichier {DATA_FILE} non trouvé")
        return

    # 3. Recharger les données
    print("\n4. Redémarrage de l'application...")
    print("   Appuyez sur Entrée après avoir redémarré...")
    input()
    
    # 4. Vérifier la suppression unique 
    try:
        response = requests.get(f"{API_URL}/transactions")
        transactions_apres = response.json()
        print(f"\n5. Transactions APRÈS suppression: {transactions_apres}")
        if transaction_supprime not in transactions_apres["transactions"] and all(t in transactions_apres["transactions"] for t in transactions_a_supprimer):
            print("\n VULNÉRABILITÉ CONFIRMÉE!")
        else:
            print("\n L'attaque a échoué, suppression unique impossible")
    except requests.exceptions.ConnectionError:
        print("\n Serveur non accessible")

if __name__ == "__main__":
    suppr_transac()