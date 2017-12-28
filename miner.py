import requests
import random
import time


def mine():
    count = 0
    while True:
        t = time.time()
        requests.post('http://127.0.0.1:5000/mine', json={'wallet': 'edmartin101@googlemail.com'})
        count += 1
        taken = time.time() - t
        print('Mined {} Coins, Time Taken: {}'.format(count, taken))


if __name__ == '__main__':
    mine()