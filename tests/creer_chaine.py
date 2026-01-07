import requests
import json
import os
import time


API_URL = "http://localhost:5000"

def creer_chaine():
    transaction = {"emitter": "Alice", "receptor": "Bob", "amount": 100}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
    
    transaction = {"emitter": "Bob", "receptor": "Alice", "amount": 500}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
    
    transaction = {"emitter": "Victor", "receptor": "Bob", "amount": 1000}
    response = requests.post(f"{API_URL}/transaction", json=transaction)
    
    transaction = {"emitter": "Alice", "receptor": "Bob", "amount": 1000}
    response = requests.post(f"{API_URL}/transaction", json=transaction)

if __name__ == "__main__":
    creer_chaine()