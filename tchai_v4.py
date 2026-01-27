import hashlib
from xml.parsers.expat import errors
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
import requests
import sys

app = Flask(__name__)


PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
print(f"Starting server on port {PORT}")
DATA_FILE = f"transactions_{PORT}.json"
DATA_CORRUPTED = f"transactions_corrupted_{PORT}.json"

###################################################################################################################################
##### DECLARATION FONCTION POUR LE SERVEUR #######
##################################################################################################################################

##### HASHAGE #######
def proof_of_work(last_hash, transactions_data, difficulty=2):
    nonce = 0
    while True:
        content = f"{last_hash}{transactions_data}{nonce}".encode()
        guess_hash = hashlib.sha256(content).hexdigest()
        if guess_hash[:difficulty] == "0" * difficulty:
            return nonce, guess_hash
        nonce += 1
        
def hash_func(emitter, receptor, amount, timestamp, previous_hash):
    transaction_string = f"{emitter}{receptor}{timestamp}{amount}{previous_hash}"
    return hashlib.sha256(transaction_string.encode()).hexdigest()


##### LOAD ET SAVE #######
def load_transactions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            transactions = json.load(f)

        message, i = verify(transactions)
        transactions = transactions[:i]
        save_transactions(transactions)
        return transactions
    return []

def save_transactions(transactions):
    with open(DATA_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)


##### VERIFY #######
def verify(transaction_):
    for i, t in enumerate(transaction_):
        expected_hash = hash_func(t['emitter'], t['receptor'], t['amount'], t['timestamp'], t['previous_hash'])

        if t['hash'] != expected_hash:
            return "erreur: " f"Chaîne reçue corrompue à l'index {i}", i
            
        if i > 0 and t['previous_hash'] != transaction_[i-1].get('hash'):
            return "erreur: " f"Coupure de chaîne à l'index {i}", i

    return "message: " "Toutes les transactions sont justes.", None

transactions = load_transactions()
###################################################################################################################################
### DECLARATION DES ROUTES FLASK ###
###################################################################################################################################

@app.route('/')
def home():
    return jsonify({
        "message": "Bienvenue sur Tchai_v2",
        "endpoints": {
            "POST /transaction": "Enregistrer une transaction",
            "GET /transactions": "Afficher toutes les transactions",
            "GET /transactions/<person>": "Afficher les transactions d'une personne chronologiquement",
            "GET /solde/<person>": "Afficher le solde d'une personne",
            "GET /verify": "Verifier l'integrite des transactions"
        }
    })

#Enregistrer une transaction
@app.route('/transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    
    if not data or 'emitter' not in data or 'receptor' not in data or 'amount' not in data:
        return jsonify({"erreur": "Données manquantes (emetteur, receveur, montant requis)"}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"erreur": "Le montant doit être positif"}), 400
    except ValueError:
        return jsonify({"erreur": "Le montant doit être un nombre"}), 400
    
    emitter = data['emitter']
    receptor = data['receptor']
    timestamp = datetime.now().isoformat()

    previous_hash = transactions[-1].get('hash') if transactions else None #A changer en un nombre au hasard pour pas "hacker" facilement
    h = hash_func(emitter, receptor, amount, timestamp, previous_hash)

    transaction = {
        'id': len(transactions) + 1,
        'emitter': data['emitter'],
        'receptor': data['receptor'],
        'amount': amount,
        'timestamp': timestamp,
        'hash': h,
        'previous_hash': previous_hash
    }
    
    transactions.append(transaction)
    save_transactions(transactions)
    
    return jsonify({
        "message": "Transaction enregistrée avec succès",
        "transaction": transaction
    }), 201

###############################################################################################################################
###############################################################################################################################
###############################################################################################################################
# Afficher toutes les transactions dans l'ordre chronologique
@app.route('/transactions', methods=['GET'])
def afficher_transactions():
    return jsonify({
        "total": len(transactions),
        "transactions": transactions
    }), 200

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
    
    return jsonify({
        "person": person,
        "solde": solde,
        "transactions_count": len([t for t in transactions 
                                   if t['emitter'] == person or t['receptor'] == person])
    }), 200

@app.route('/verify', methods=['GET'])
def verify_integrity():
    message, i = verify(transactions)
    if i:
        return jsonify(message, i), 418 
    else:
        return jsonify(message, len(transactions)), 200
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)

    
# python app.py 5001