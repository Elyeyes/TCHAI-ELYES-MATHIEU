# TCHAI-ELYES-MATHIEU
chaine de transaction

## Tchaî v1

### Base URL
```
http://localhost:5000
```

---

Ici nous avons la première version avec ci-dessous la liste des commandes:

### 1. Enregistrer une transaction

Un émitteur envoie un montant à un receveur.

**Endpoint**
```http
POST /transaction
```

**Headers**
```
Content-Type: application/json
```

**Body**
```json
{
    "emitter": "user1",
    "receptor": "user2",
    "amount": 50.0
}
```

**Réponse (201 Created)**
```json
{
    "message": "Transaction enregistrée avec succès",
    "transaction": {
        "id": 1,
        "emitter": "user1",
        "receptor": "user2",
        "amount": 10.0,
        "timestamp": "time_of_transaction"
  }
}
```

**Exemples**

<details>
<summary>cURL</summary>

```bash
curl -X POST http://localhost:5000/transaction \
  -H "Content-Type: application/json" \
  -d '{"emitter":"user1","receptor":"user2","amount":10}'
```
</details>

<details>
<summary>Python (requests)</summary>

```python
import requests

response = requests.post('http://localhost:5000/transaction', json={
    "emitter": "user1",
    "receptor": "user2",
    "amount": 50
})
print(response.json())
```
</details>

<details>
<summary>JavaScript (fetch)</summary>

```javascript
fetch('http://localhost:5000/transaction', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        emitter: "user1",
        receptor: "user2",
        amount: 10
  })
})
.then(res => res.json())
.then(data => console.log(data));
```
</details>

---

### 2. Afficher toutes les transactions

Récupère la liste complète des transactions dans l'ordre chronologique.

**Endpoint**
```http
GET /transactions
```

**Réponse (200 OK)**
```json
{
    "total": 2,
    "transactions": [
    {
        "id": 1,
        "emitter": "user1",
        "receptor": "user2",
        "amount": 10.0,
        "timestamp": "time_of_transaction"
    },
    {
        "id": 2,
        "emitter": "user2",
        "receptor": "user1",
        "amount": 20.0,
        "timestamp": "time_of_transaction"
    }
  ]
}
```

---

### 3. Afficher les transactions d'une personne

Récupère toutes les transactions où une personne est impliquée (émetteur ou receveur).

**Endpoint**
```http
GET /transactions/{person}
```

**Réponse (200 OK)**
```json
{
    "person": "user1",
    "total": 1,
    "transactions": [
    {
        "id": 1,
        "emitter": "user1",
        "receptor": "user2",
        "amount": 10.0,
        "timestamp": "time_of_transaction"
    }
  ]
}
```

---

### 4. Afficher le solde d'une personne

Calcule et affiche le solde d'une personne (montants reçus - montants envoyés).

**Endpoint**
```http
GET /solde/{person}
```

**Réponse (200 OK)**
```json
{
  "person": "Alice",
  "solde": -10.0,
  "transactions_count": 1
}
```


```python
import requests

person = "Alice"
response = requests.get(f'http://localhost:5000/solde/{person}')
print(response.json())
```

---

### Structure d'une transaction

```json
{
  "id": 1,                                    // Identifiant unique auto-généré
  "emitter": "nom",                           // Personne qui envoie
  "receptor": "nom",                          // Personne qui reçoit
  "amount": 50.0,                             // Montant de la transaction
  "timestamp": "2024-03-15T14:30:00.123456",  // Date et heure
}
```


## Points d'améliorations

- Les données sont stockées en **mémoire** uniquement
- Les transactions sont **perdues** au redémarrage du serveur
- Aucune authentification n'est implémentée
- Les montants doivent être **positifs**

