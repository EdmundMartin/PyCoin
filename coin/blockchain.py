import time
import hashlib
from math import log2


class BlockChain:

    def __init__(self):
        start_block = self.get_next_block(0, '816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7', '',
                                          1465154705, 'my genesis block!!', 0, 0)
        self.block_list = [start_block]
        self.block_generation_interval = 10
        self.block_difficulty_interval = 10

    def get_difficulty(self, block):
        assert isinstance(block, list)
        latest_block = block[len(self.block_list) - 1]
        if latest_block.get('index') % self.block_difficulty_interval == 0 and latest_block.get('index') != 0:
            return self.get_adjusted_difficulty(latest_block, block)
        else:
            return latest_block['difficulty']

    def get_adjusted_difficulty(self, latest_block, blockchain):
        prev_adjustment_block = blockchain[len(blockchain) - self.block_difficulty_interval]
        time_expected = self.block_generation_interval * self.block_difficulty_interval
        time_taken = latest_block['timestamp'] - prev_adjustment_block['timestamp']
        if time_taken < (time_expected / 2):
            return prev_adjustment_block['difficulty'] + 1
        if time_taken > (time_expected * 2):
            return prev_adjustment_block['difficulty'] - 1
        else:
            return prev_adjustment_block['difficulty']

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

    def get_blockchain(self):
        return self.block_list

    def get_last_block(self):
        return self.block_list[-1]

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

    def valid_block(self, previous_block, new_block):
        assert isinstance(new_block['index'], int)
        assert isinstance(new_block['hash'], str)
        assert isinstance(new_block['previous_hash'], str)
        assert isinstance(new_block['timestamp'], int)
        assert isinstance(new_block['data'], str)
        assert isinstance(new_block['difficulty'], int)
        assert isinstance(new_block['nonce'], int)
        if new_block['index'] != previous_block['index'] + 1:
            return False
        if new_block['previous_hash'] != previous_block['hash']:
            return False
        if new_block['hash'] != self.calculate_hash(new_block['index'], new_block['previous_hash'], new_block['timestamp'],
                                           new_block['data'], new_block['difficulty'], new_block['nonce']):
            return False
        if not self.has_valid_hash(new_block):
            return False
        if not self.is_valid_timestamp(previous_block, new_block):
            return False
        return True

    def generate_next_block(self, block_data):
        assert isinstance(block_data, str)
        previous_block = self.get_last_block()
        next_index = previous_block['index'] + 1
        next_timestamp = int(time.time())
        difficulty = self.get_difficulty(self.get_blockchain())
        new_block = self.find_block(next_index, previous_block['hash'], next_timestamp, block_data, difficulty)
        valid = self.valid_block(previous_block, new_block)
        if valid:
            self.block_list.append(new_block)
        else:
            print('Block invalid')

    def hash_matches_block_content(self, block):
        block_hash = self.calculate_hash(block['index'], block['previous_hash'], block['timestamp'], block['data'],
                                         block['difficulty'], block['nonce'])
        return block['hash'] == block_hash

    def has_valid_hash(self, block):
        if not self.hash_matches_block_content(block):
            return False

        if not self.hash_matches_diffuculty(block['hash'], block['difficulty']):
            return False

        return True

    def is_valid_timestamp(self, previous_block, new_block):
        return (previous_block['timestamp'] - 60) < new_block['timestamp'] and (new_block['timestamp']) - 60 < time.time()

    def get_accumlated_difficulty(self, blockchain):
        assert isinstance(blockchain, list)
        total_difficulty = 0
        for block in blockchain:
            diff = block['difficulty']
            total_difficulty += diff ** 2
        return total_difficulty

    def is_valid_chain(self, blockchain):
            assert isinstance(blockchain, list)
            for i, item in enumerate(blockchain):
                if i > 0:
                    if not self.valid_block(blockchain[i - 1], blockchain[i]):
                        return False
            return True

    def replace_chain(self, blockchain):
        if self.is_valid_chain(blockchain) and \
                self.get_accumlated_difficulty(blockchain) > self.get_accumlated_difficulty(self.get_blockchain()):
            self.block_list = blockchain
        else:
            print('Received invalid blockchain')


if __name__ == '__main__':
    b = BlockChain()
    while True:
        latest = b.get_last_block()
        t = time.time()
        b.generate_next_block('EDMUND')
        print(len(b.block_list))
        time_taken = time.time() - t
        print(time_taken)