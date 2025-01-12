"""
blockchain.py
Enhances the blockchain to identify which block is tampered and restore automatically.
Also can call a callback to alert admin (we store a simple 'tampering_alert' variable).
"""

import hashlib
import json
import time
import os
from config import BLOCKCHAIN_FILE

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        content = (
            str(self.index)
            + str(self.timestamp)
            + json.dumps(self.transactions, sort_keys=True)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        return hashlib.sha256(content.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.tampering_alert = False  # Will set True if tampering is detected
        self.chain_backup = None      # We store a backup to restore if tampering is found
        if os.path.exists(BLOCKCHAIN_FILE):
            self.load_chain()
        if len(self.chain) == 0:
            genesis = Block(0, time.time(), "Genesis Block", "0")
            self.chain.append(genesis)
            self.save_chain()

        # Keep a backup of the valid chain in memory
        self.chain_backup = self._clone_chain(self.chain)

    def _clone_chain(self, chain_list):
        # returns a deep copy of the chain
        import copy
        return copy.deepcopy(chain_list)

    def load_chain(self):
        with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for b in data:
                block = Block(
                    b["index"],
                    b["timestamp"],
                    b["transactions"],
                    b["previous_hash"],
                    b["nonce"]
                )
                block.hash = b["hash"]
                self.chain.append(block)

    def save_chain(self):
        data = []
        for b in self.chain:
            data.append({
                "index": b.index,
                "timestamp": b.timestamp,
                "transactions": b.transactions,
                "previous_hash": b.previous_hash,
                "nonce": b.nonce,
                "hash": b.hash
            })
        with open(BLOCKCHAIN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
        self.save_chain()
        # Update backup
        self.chain_backup = self._clone_chain(self.chain)

    def is_chain_valid(self, verbose=False):
        """
        Returns (bool, tampered_indices_list)
        If tampered_indices_list is not empty, we know which blocks are invalid.
        """
        tampered_indices = []
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            # recalc hash
            if curr.hash != curr.calculate_hash():
                tampered_indices.append(i)
            if curr.previous_hash != prev.hash:
                tampered_indices.append(i)

        is_valid = (len(tampered_indices) == 0)
        if not is_valid and verbose:
            print(f"[WARNING] Tampering detected in blocks: {tampered_indices}")
        return is_valid, tampered_indices

    def restore_chain(self):
        """
        Restores the chain from backup, overwriting any tampered changes.
        """
        if self.chain_backup is not None:
            self.chain = self._clone_chain(self.chain_backup)
            self.save_chain()
            print("[INFO] Blockchain restored to the last valid state.")
        else:
            print("[ERROR] No backup available to restore.")

    def mine_block(self, transactions, difficulty=2):
        index = len(self.chain)
        timestamp = time.time()
        new_block = Block(index, timestamp, transactions, self.get_latest_block().hash)

        while new_block.hash[:difficulty] != "0"*difficulty:
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        self.chain.append(new_block)
        self.save_chain()
        # update backup
        self.chain_backup = self._clone_chain(self.chain)
        return new_block

blockchain = Blockchain()

def record_transaction_in_blockchain(from_acc, to_acc, amount, status, category):
    tx = {
        "from_account": from_acc,
        "to_account": to_acc,
        "amount": amount,
        "status": status,
        "category": category,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    mined_block = blockchain.mine_block([tx], difficulty=2)
    return mined_block
