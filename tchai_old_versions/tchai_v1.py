from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

DATA_FILE = "transactions.json"

def load_transactions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    
    save_transactions([])
    return []

def save_transactions(transactions):
    with open(DATA_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)

transactions = load_transactions()

@app.route('/')
def home():
    return jsonify({
        "message": "Bienvenue sur Tchai_v1",
        "endpoints": {
            "POST /transaction": "Enregistrer une transaction",
            "GET /transactions": "Afficher toutes les transactions",
            "GET /transactions/<person>": "Afficher les transactions d'une personne chronologiquement",
            "GET /solde/<person>": "Afficher le solde d'une personne"
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
    
    transaction = {
        'id': len(transactions) + 1,
        'emitter': data['emitter'],
        'receptor': data['receptor'],
        'amount': amount,
        'timestamp': datetime.now().isoformat(),
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)