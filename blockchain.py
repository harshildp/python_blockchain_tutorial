import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        self.new_block(proof=100, previous_hash='1')

    def new_block(self, proof, previous_hash=None):
        # Creates a new Block and adds it to the chain
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
        
    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transactions
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        # Hashes a Block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        x = 0
        print('proofing')
        while self.validate_proof(last_proof, x) is False:
            print('x is ', x)
            x += 1

        return x

    @staticmethod
    def validate_proof(last_proof, x):
        guess = f'{last_proof}{x}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    print('last_blocked')
    last_proof = last_block['proof']
    print('last proofed')
    proof = blockchain.proof_of_work(last_proof)
    print('proofed')

    blockchain.new_transaction(sender='0', recipient=node_identifier, amount=1)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    res = {
        'message': 'Forged a new block',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(res), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    print('values', values)
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    res = {
        'message': f'Transaction will be added to block {index}'
    }
    return  jsonify(res), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    res = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(res), 200

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
app.run(debug=True)





