import requests
import time
from math import log2
import hashlib


class Miner:

    def __init__(self, node, wallet):

        self.node_address = node.rstrip('/')
        self.wallet = wallet
        self.session_total_mined = 0
        self.session_started = time.time()

    def get_last_block(self):
        try:
            res = requests.get('{}{}'.format(self.node_address, '/last-chain')).json()
            return res
        except requests.RequestException as e:
            print(e)
            return

    def get_difficulty(self):
        try:
            res = requests.get('{}{}'.format(self.node_address, '/current-difficulty')).json()
            return res
        except requests.RequestException:
            return

    def post_block(self, block):
        try:
            res = requests.post(self.node_address + '/mine', json=block).json()
            if res.get('message') == 'Coin mined':
                time_taken = time.time() - self.session_started
                self.session_total_mined += 1
                print('Mined: {} coin, in {} seconds, {} coin per second'.format(self.session_total_mined, time_taken, (self.session_total_mined / time_taken)))
        except requests.RequestException as e:
            return

    def mine_block(self):
        previous_block = self.get_last_block()
        difficulty = self.get_difficulty()
        if previous_block and difficulty:
            next_index = previous_block['index'] + 1
            next_timestamp = int(time.time())
            new_block = self.find_block(next_index, previous_block['hash'], next_timestamp, self.wallet,
                                        difficulty['difficulty'])
            self.post_block(new_block)

    def find_block(self, index, previous_hash, timestamp, data, difficulty):
        nonce = 0
        while True:
            hash = self.calculate_hash(index, previous_hash, timestamp, data, difficulty, nonce)
            if self.hash_matches_diffuculty(hash, difficulty):
                return self.get_next_block(index, hash, previous_hash, timestamp, data, difficulty, nonce)
            nonce += 1

    def hash_matches_diffuculty(self, hash, difficulty):
        num_of_bits = len(hash) * log2(16)
        hash_in_binary = bin(int(hash, 16))[2:].zfill(int(num_of_bits))
        required_prefix = '0' * difficulty
        return hash_in_binary.startswith(required_prefix)

    def get_next_block(self, index, hash, previous_hash, timestamp, data, difficulty, nonce):
        assert isinstance(index, int)
        assert isinstance(hash, str)
        assert isinstance(previous_hash, str)
        assert isinstance(timestamp, int)
        assert isinstance(data, str)
        assert isinstance(difficulty, int)
        assert isinstance(nonce, int)
        return {'index': index, 'hash': hash, 'data': data, 'timestamp': timestamp,
                'previous_hash': previous_hash, 'difficulty': difficulty, 'nonce': nonce}

    def calculate_hash(self, index, previous_hash, timestamp, data, difficulty, nonce):
        hash_string = '{}{}{}{}{}{}'.format(index, previous_hash, timestamp, data, difficulty, nonce)
        return hashlib.sha256(bytes(hash_string, 'utf-8')).hexdigest()

    def mining(self):
        while True:
            self.mine_block()


if __name__ == '__main__':
    miner = Miner('http://127.0.0.1:5000', 'edmartin101@googlemail.com')
    miner.mining()