import requests
import json
import os
import time

API_URL = "http://localhost:5000"
DATA_FILE = "C:/Users/elyes/Desktop/Document d'Elyes/Travail/Code/5A/Tchai/TCHAI-ELYES-MATHIEU/transactions.json"

def modif_fichier():
    print("=== Test d'attaque : Modification du fichier de données ===\n")
    
    # 1. Créer une transaction légitime
    print("1. Création d'une transaction")
    transaction = {"emitter": "Alice", "receptor": "Bob", "amount": 1}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
        
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
        
        print(f"   Transaction à modifier: {data[0]}")
        
        data[0]['amount'] = 1000
        data[0]['description'] = "FALSIFIE PAR ATTAQUANT"
        transaction = data[0]
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        print(f"   Fichier {DATA_FILE} non trouvé")
        return
    solde_voulu = solde_avant - 999

    # 4. Recharger les données
    print("\n4. Redémarrage de l'application pour charger les données falsifiées...")
    print("   Appuyez sur Entrée après avoir redémarré...")
    input()
    
    # 5. Vérifier le solde après attaque
    try:
        response = requests.get(f"{API_URL}/solde/Alice")
        solde_apres = response.json()["solde"]
        print(f"\n5. Solde d'Alice APRÈS attaque: {solde_apres}€")
        if solde_apres == solde_voulu:
            print("\n VULNÉRABILITÉ CONFIRMÉE!")
            print(f"   - Différence: {abs(solde_avant - solde_apres)}€")
        else:
            print("\n L'attaque a échoué, modification impossible")
    except requests.exceptions.ConnectionError:
        print("\n Serveur non accessible")

if __name__ == "__main__":
    modif_fichier()