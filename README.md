# TCHAI-ELYES-MATHIEU
chaine de transaction

## Tchaî v3

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

### 5. Vérifier les transactions
Vérifier l’intégrité des données en recalculant les hashs à partir des données et en les comparant
avec les hashs stockés précédemment.

**Endpoint**
```http
GET /verify
```

**Réponse (200 OK)**
```json
{
{
  "message": "Toutes les transactions sont justes.",
  "status": "Ok",
  "total_transactions": 1
}
}
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
  "hash": "9c9a78db16d62293b59bcb4c7b6fecfc982e874b1c8d6c31b9d93556ad01d247" // Hash de la transaction
}
```


## Points d'améliorations

- Aucune authentification n'est implémentée
- Pas de tracabilité des transactions (entre elles)
- au lieu de copier la nouvelle liste de transactions (couteux si très grosse) "remplacer" et ajouter par rapport à la première difference
Exemple: Si la transaction numéro 567 et différente alors prendre la bonne numéro 567 et toute celles d'après pas les 566 avant.


## Utilisation

Ne pas lancer de deuxième serveur pour une utilisation "normal"

## Tests
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'API principale

# 3. Dans un autre terminal, exécuter les tests
chmod +x tests/run_tests.sh
./tests/run_tests.sh

# Ou exécuter un test spécifique
python tests/modif_fichier.py
```

### Modifier transaction
On attaque le fichier qui sauvegarde les transactions en modifiant notamment le montant Tchai_v1 y est vulnérable.
Avec un hash l'attaque ne fonctionne plus dans Tchai_v2 la transactions peut être supprimé (pour l'instant sauvegardé à part dans transactions_corrupted)

On a que les transactions non corrompues (non attaqué), il faudrait ne pas perdre les transactions effectué mais pour cela il faut un système ou plusieurs machines ont leur sauvegarde de transactions et se les partagent régulièrement. Il sera difficile pour l'attaquant de modifier plusieurs fois la même transactions sur des machines dispersés.

Sinon la version simple c'est accepter de perdre des transactions

### Supprimer transaction
On supprime une transactions stockés dans le fichier. Puis on vérifie qu'elle est bien supprimé. Le danger c'est dans le cas où il faut avoir le solde pour faire une transaction, exemple Alice doit avoir un solde de 100 pour donner 100 à Bob, alors si on supprime la ou les transactions qui ont permis à Alice d'avoir 100, mais que les transactions d'après d'Alice reste alors il y a un problème car elle aurait payé avec de l'argent qu'elle n'a pas, on peut voir après l'attaque le solde d'Alice est négatif. Par conséquent il faut supprimer toutes les transactions après la transaction attaqué (et supprimé). C'est ce que permet tchai_v3 avec le hash des transactions précédentes. A noter que seulement considérer les id (comme elles sont modifiable par attaque) n'est pas suffisant. Alors que le hash comme il dépend du timestamp impossible de le fausser.

Le problème actuellement est que si il y a une attaque sur le systeme de sauvegarde des transactions on peut perdre toutes les transactions effectué et donc recommencer de zéro une chaine.

Avec Tchai_B si il y a deux serveurs, et que un est attaqué alors au redémarrage il compare avec la liste de l'autre serveur et récupère si il y a plus de transactions honnêtes.

### Ajouter une transaction frauduleuse
Avec tchai_v3 cela fonctionne donc une personne peut être débité à tort.