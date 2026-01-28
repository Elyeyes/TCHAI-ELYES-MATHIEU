import hashlib
from xml.parsers.expat import errors
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

DATA_FILE = "transactions_5000.json"
DATA_CORRUPTED = "transactions_5000_corrupted.json"

def hash_func(emitter, receptor, amount, timestamp, previous_hash):
    transaction_string = f"{emitter}{receptor}{timestamp}{amount}{previous_hash}"
    return hashlib.sha256(transaction_string.encode()).hexdigest()

def load_transactions():
    if os.path.exists(DATA_CORRUPTED):
        with open(DATA_CORRUPTED, 'r') as f:
            errors = json.load(f)
    else:
        errors = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            transactions = json.load(f)
        for i, t in enumerate(transactions):
            if i > 0:
                t['previous_hash'] = transactions[i-1].get('hash')
            else:
                t['previous_hash'] = None
            
            expected_hash = hash_func(t['emitter'], t['receptor'], t['amount'], t['timestamp'], t['previous_hash'])
            if t['hash'] != expected_hash:
                errors.append({
                    "transaction_id": t['id'],
                    "expected_hash": expected_hash,
                    "found_hash": t['hash'],
                    "status" : "Corrompue"
                })
                # transactions.remove(t) # Plus tard on pourra demander la bonne transaction à un autre noeud
                transactions = transactions[:i]
                break
        with open(DATA_CORRUPTED, 'w') as f:
                json.dump(errors, f, indent=2)
        save_transactions(transactions)
        return transactions
    
    save_transactions([])
    return []

def save_transactions(transactions):
    with open(DATA_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)

transactions = load_transactions()

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
    errors = []
    for i, t in enumerate(transactions):
        if i > 0:
            t['previous_hash'] = transactions[i-1].get('hash')
        else:
            t['previous_hash'] = None #pareil à changer en un nombre au hasard (le meme) pour pas "hacker" facilement
        
        expected_hash = hash_func(t['emitter'], t['receptor'], t['amount'], t['timestamp'], t['previous_hash'])
        if t['hash'] != expected_hash:
            errors.append({
                "transaction_id": t['id'],
                "expected_hash": expected_hash,
                "found_hash": t['hash'],
                "status" : "Corrompue",
            })
    if not errors:
        return jsonify({
            "status": "Ok",
            "message": "Toutes les transactions sont justes.",
            "total_transactions": len(transactions)
            }), 200
    else:
        return jsonify({
            "status": "Erreur",
            "message": "Certaines transactions sont corrompues.",
            "corrupted_transactions": errors,
            "total_corrupted": len(errors)
            }), 418
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)