"""
Test d'attaque : Modification directe du fichier de données
Démontre comment un attaquant peut falsifier les transactions
"""
import requests
import json
import os
import time

API_URL = "http://localhost:5000"
DATA_FILE = "C:/Users/elyes/Desktop/Document d'Elyes/Travail/Code/5A/Tchai/TCHAI-ELYES-MATHIEU/transactions.json"

def test_file_modification():
    print("=== Test d'attaque : Modification du fichier de données ===\n")
    
    # 1. Créer une transaction légitime
    print("1. Création d'une transaction légitime...")
    transaction = {"emitter": "Alice", "receptor": "Bob", "amount": 100}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
    print(f"   Transaction créée: Alice -> Bob: 100€")
    
    # 2. Vérifier le solde avant attaque
    response = requests.get(f"{API_URL}/solde/Alice")
    solde_avant = response.json()["solde"]
    print(f"\n2. Solde d'Alice AVANT attaque: {solde_avant}€")
    
    # 3. Attaque : Modifier directement le fichier
    print("\n3. Modification directe du fichier...")
    time.sleep(0.5)  # Attendre que le fichier soit écrit
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        print(f"   Fichier trouvé avec {len(data)} transaction(s)")
        print(f"   Transaction originale: {data[0]}")
        
        # Modifier le montant de 100€ à 10€
        data[0]['amount'] = 10
        data[0]['description'] = "FALSIFIE PAR ATTAQUANT"
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"   Transaction modifiée: montant changé de 100€ à 10€")
        print(f"   Description modifiée")
    else:
        print(f"   Fichier {DATA_FILE} non trouvé")
        return
    
    # 4. Recharger les données (redémarrer l'API ou attendre le prochain chargement)
    print("\n4. Redémarrage de l'application pour charger les données falsifiées...")
    print("   (Redémarrez manuellement vulnerable_app.py)")
    print("   Appuyez sur Entrée après avoir redémarré...")
    input()
    
    # 5. Vérifier le solde après attaque
    try:
        response = requests.get(f"{API_URL}/solde/Alice")
        solde_apres = response.json()["solde"]
        print(f"\n5. Solde d'Alice APRÈS attaque: {solde_apres}€")
        
        response = requests.get(f"{API_URL}/transactions")
        transaction_modifiee = response.json()["transactions"][0]
        
        print(f"\n6. Transaction dans le système:")
        print(f"   Montant: {transaction_modifiee['amount']}€")
        print(f"   Description: {transaction_modifiee['description']}")
        
        if transaction_modifiee['amount'] == 10:
            print("\n VULNÉRABILITÉ CONFIRMÉE!")
            print("   L'attaquant a réussi à modifier l'historique des transactions")
            print("   Impact:")
            print("   - Falsification de l'historique financier")
            print("   - Perte d'intégrité des données")
            print("   - Possibilité de fraude")
            print(f"   - Différence: {abs(solde_avant - solde_apres)}€")
    except requests.exceptions.ConnectionError:
        print("\n Serveur non accessible")

if __name__ == "__main__":
    test_file_modification()