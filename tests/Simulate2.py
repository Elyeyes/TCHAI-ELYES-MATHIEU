from time import time, sleep
from coincurve import PrivateKey, PublicKey
import json
import os
import sys
import requests 

# PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
# KEY_FILE = f"keys_{PORT}.json"
# neighbor_port = 5001 if PORT == 5000 else 5000
neighbor_url = f"http://127.0.0.1:"

def create_retrieve_keypair(port, new=False):
    key_file = f"keys_{port}.json"
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            try:
                keys_list = json.load(f)
            except json.JSONDecodeError:
                keys_list = []
    else:
        keys_list = []

    if new or not keys_list:
        private_key = PrivateKey()
        public_key = private_key.public_key

        key_entry = {
            "private_key": private_key.to_hex(),
            "public_key": public_key.format(compressed=True).hex(),
        }

        print(f"Private Key (hex): {key_entry['private_key']}")
        print(f"Public Key (hex): {key_entry['public_key']}")
        keys_list.append(key_entry)

        with open(key_file, "w") as f:
            json.dump(keys_list, f, indent=2)
    else:
        key_entry = keys_list[-1]
        private_key = PrivateKey(bytes.fromhex(key_entry["private_key"]))
        public_key = PublicKey(bytes.fromhex(key_entry["public_key"]))

    return private_key, public_key


def sign_transaction(private_key, transaction):
    transaction_bytes = json.dumps(transaction, sort_keys=True).encode()
    signature = private_key.sign(transaction_bytes)
    return signature.hex()


def ask_transaction(port, receptor, amount):
    emitter_private_key, emitter_public_key = create_retrieve_keypair(port)
    transaction = {
        "emitter": emitter_public_key.format(compressed=True).hex(),
        "amount": float(amount),
        "receptor": receptor.format(compressed=True).hex(),
    }

    signature = sign_transaction(emitter_private_key, transaction)
    transaction["signature"] = signature

    try:
        response = requests.post(f"{neighbor_url}{port}/transaction", json=transaction)
        print(response.status_code, response.text)
    except Exception as e:
        print("Erreur de connexion au serveur.", e)


if __name__ == "__main__":
    create_retrieve_keypair(0, new=False) # Si on veut être anonyme on peut générer autant de pairs qu'on veut
    receptor_5000 = create_retrieve_keypair(5000)[1]
    receptor_5001 = create_retrieve_keypair(5001)[1]
    # ask_transaction(5000, receptor_5000, 1.0)
    # ask_transaction(5000, receptor_5000, 1.0)
    ask_transaction(5000, receptor_5000, 100.0)
    # ask_transaction(5001, receptor_5001, 100.0)
    print("Transaction envoyée au port 5000")
