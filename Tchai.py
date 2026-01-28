import hashlib
from xml.parsers.expat import errors
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
import requests
import sys
from coincurve import PrivateKey, PublicKey

app = Flask(__name__)


PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
print(f"Starting server on port {PORT}")
DATA_FILE = f"transactions_{PORT}.json"
DATA_CORRUPTED = f"transactions_corrupted_{PORT}.json"

###################################################################################################################################
##### DECLARATION FONCTION POUR LE SERVEUR #######
##################################################################################################################################

##### HASHAGE #######


def hash_func(emitter, amount, receptor, signature, timestamp, previous_hash):
    transaction_string = f"{emitter}{amount}{receptor}{signature}{timestamp}{previous_hash}"
    return hashlib.sha256(transaction_string.encode()).hexdigest()

def verify_signature(public_key, transaction, signature_hex):
    try:
        public_key = PublicKey(bytes.fromhex(public_key))
        signature = bytes.fromhex(signature_hex)
        transaction = {
            "emitter": transaction['emitter'],
            "amount": float(transaction['amount']),
            "receptor": transaction['receptor']
        }
        message = json.dumps(transaction, sort_keys=True).encode()
        print(f"Vérification de la signature pour l'émetteur {public_key.format(compressed=True).hex()}")
        
        return public_key.verify(signature, message)
    except Exception as e:
        print(f"Erreur de vérification: {e}")
        return False

##### LOAD ET SAVE #######
def load_transactions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            transactions = json.load(f)

        message, i = verify_chain(transactions)
        transactions = transactions[:i]
        save_transactions(transactions)

        return transactions
    save_transactions([])
    return []

def save_transactions(transactions):
    with open(DATA_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)


##### VERIFY #######
def verify_chain(chain):
    for i, t in enumerate(chain):
        if 'signature' not in t:
            return "erreur: " f"Signature manquante à l'index {i}", i
        
        expected_hash = hash_func(t['emitter'], t['amount'], t['receptor'], t['signature'], t['timestamp'], t['previous_hash'])

        if t['hash'] != expected_hash:
            return "erreur: " f"Hash faux à l'index {i}", i
        
        if i > 0 and t['previous_hash'] != chain[i-1].get('hash'):
            return "erreur: " f"Coupure de chaîne à l'index {i}", i

    return "message: " " Chaine justes.", None


###################################################################################################################################
### GESTION DES CHAINES ###
###################################################################################################################################
def sync_with_neighbor():
    global transactions 
    # Si on est sur le port 5000, le voisin est 5001, et inversement
    neighbor_port = 5001 if PORT == 5000 else 5000
    neighbor_url = f"http://127.0.0.1:{neighbor_port}"
    try:
        response = requests.get(f"{neighbor_url}/transactions", timeout=2)
        if response.status_code == 200:
            neighbor_data = response.json().get('transactions', [])
            message, i = verify_chain(neighbor_data)
            if i:
                print("Le voisin a des données corrompues, synchro annulé, je lui envoi ma liste.")
                send_chain()
                return False
                    
            if len(neighbor_data) > len(transactions):
                transactions = neighbor_data
                save_transactions(transactions)
                print("Synchronisation réussie, liste mise à jour: \n", len(transactions), "transactions")
                return True
            elif len(neighbor_data) < len(transactions):
                print("Ma liste est meilleur")
                send_chain()
            else:
                print("Les deux listes sont identiques")

                
    except Exception as e:
        print(f"Impossible de joindre le voisin : {str(e)}")
    return False

def send_chain():
    neighbor_port = 5001 if PORT == 5000 else 5000
    try:
        requests.post(f"http://127.0.0.1:{neighbor_port}/sendChain", json={"transactions": transactions}, timeout=2)
    except:
        pass


transactions = load_transactions()
sync_with_neighbor()
###################################################################################################################################
### DECLARATION DES ROUTES FLASK ###
###################################################################################################################################

@app.route('/')
def home():
    return jsonify({
        "message": "Bienvenue sur Tchai_Bitcoin",
        "endpoints": {
            "POST /sendList": "Recevoir une liste de transactions d'un autre noeud",
            "POST /transaction": "Enregistrer une transaction",
            "GET /transactions": "Afficher toutes les transactions",
            "GET /transactions/<person>": "Afficher les transactions d'une personne chronologiquement",
            "GET /solde/<person>": "Afficher le solde d'une personne",
            "GET /verify": "Verifier l'integrite des transactions"
        }
    })


@app.route('/sendChain', methods=['POST'])
def receive_list():
    global transactions
    data = request.get_json()
    neighbor_chain = data.get('transactions', [])

    message, my_i = verify_chain(transactions)
    if my_i:
        transactions = transactions[:my_i]
        save_transactions(transactions)

    if len(neighbor_chain) <= len(transactions):
        return jsonify({"message": "Ma chaîne est déjà plus longue ou égale. Rejeté."}), 200

    message, i = verify_chain(neighbor_chain)
    if i:
        return jsonify(message), 400

    transactions = neighbor_chain
    save_transactions(transactions)
    print(f"Chaîne mise à jour par un pair (Taille: {len(transactions)})")
    
    return jsonify({"message": "Chaîne mise à jour avec succès"}), 200


#Enregistrer une transaction
@app.route('/transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    
    if not data or 'emitter' not in data or 'receptor' not in data or 'amount' not in data or 'signature' not in data:
        return jsonify({"erreur": "Données manquantes (emetteur, receveur, montant, signature requis)"}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"erreur": "Le montant doit être positif"}), 400
    except ValueError:
        return jsonify({"erreur": "Le montant doit être un nombre"}), 400
    
    emitter = data['emitter']
    receptor = data['receptor']
    signature = data['signature']
    if not verify_signature(emitter, data, signature):
        return jsonify({"transaction rejeté": "Signature invalide"}), 400
    
    
    timestamp = datetime.now().isoformat()
    previous_hash = transactions[-1].get('hash') if transactions else "0" * 64 #A changer en un nombre au hasard pour pas "hacker" facilement
    
    h = hash_func(emitter, amount, receptor, signature, timestamp, previous_hash)

    transaction = {
        'hash': h,
        'emitter': emitter, #PublicKey
        'amount': amount,
        'receptor': receptor, #PublicKey
        'signature': signature,
        'timestamp': timestamp,
        'previous_hash': previous_hash
    }
    
    transactions.append(transaction)
    save_transactions(transactions)
    send_chain()

    return jsonify({"message": "Transaction enregistrée avec succès","transaction": transaction}), 201

###############################################################################################################################
###############################################################################################################################
###############################################################################################################################

# Afficher toutes les transactions dans l'ordre chronologique
@app.route('/transactions', methods=['GET'])
def afficher_transactions():
    return jsonify({"total": len(transactions), "transactions": transactions}), 200

# Afficher les transactions liées à une personne donnée chronologiquement
@app.route('/transactions/<person>', methods=['GET'])
def afficher_transactions_personne(person):
    transactions_personne = [
        t for t in transactions 
        if t['emitter'] == person or t['receptor'] == person
    ]
    
    return jsonify({
        "person": person,
        "total": len(transactions_personne),
        "transactions": transactions_personne
    }), 200

# Afficher le solde du compte d'une personne
@app.route('/solde/<person>', methods=['GET'])
def afficher_solde(person):
    solde = 0.0
    
    for t in transactions:
        if t['emitter'] == person:
            solde -= t['amount']
        if t['receptor'] == person:
            solde += t['amount']
    
    return jsonify({"person": person,"solde": solde}), 200

@app.route('/verify', methods=['GET'])
def verify_integrity():
    message, i = verify_chain(transactions)
    if i:
        return jsonify(message, i), 418 
    else:
        return jsonify(message, len(transactions)), 200
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)

#python Tchai_Bitcoin.py 5000