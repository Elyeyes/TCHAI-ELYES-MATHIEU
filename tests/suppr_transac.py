import requests
import json
import os
import time

from creer_chaine import creer_chaine
API_URL = "http://localhost:5000"
DATA_FILE = "C:/Users/elyes/Desktop/Document d'Elyes/Travail/Code/5A/Tchai/TCHAI-ELYES-MATHIEU/transactions_5000.json"

def suppr_transac():
    print("=== Test d'attaque : Suppression d'une transaction ===\n")
    
    # 1. Créer une transaction légitime
    creer_chaine()
        

    # 2. Attaque : Supprimer directement le fichier
    print("\n3. Suppression directe du fichier...")
    time.sleep(0.5)  # Attendre que le fichier soit écrit
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        transac_tmp = data
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
    failed = False
    # 4. Vérifier la suppression unique 
    try:
        response = requests.get(f"{API_URL}/transactions")
        transactions_apres = response.json()
        print(f"\n5. Transactions APRÈS suppression: {transactions_apres}")
        for t in transactions_apres["transactions"]:
            if t == transaction_supprime:
                if 'statut' in t and t['statut'] == 'corrompue hash faux':
                    failed = True
        if transaction_supprime not in transactions_apres["transactions"] and all(t in transactions_apres["transactions"] for t in transactions_a_supprimer):
            print("\n VULNÉRABILITÉ CONFIRMÉE!")
        elif failed == True:
            print("\n L'attaque a réussi partiellement, certaines transactions marquées comme corrompues")
        elif transac_tmp == transactions_apres["transactions"]:
            print("\n L'attaque a échoué, toutes les transactions sont présentes")
        else:
            print("\n L'attaque a échoué, suppression unique impossible")
    except requests.exceptions.ConnectionError:
        print("\n Serveur non accessible")

if __name__ == "__main__":
    suppr_transac()