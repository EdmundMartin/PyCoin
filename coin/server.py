import asyncio
from aiohttp import web
from coin.blockchain import BlockChain
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class ChainServer:

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.block = BlockChain()
        self.peers = []
        self.loop = asyncio.get_event_loop()
        self.latest_block = self.block.get_last_block()['index']
        self.process_pool = ThreadPoolExecutor(max_workers=10)

    def update_peers(self, peer):
        try:
            url = 'http://{}:{}/updates'.format(peer.get('address'), peer.get('port'))
            chain = self.block.get_blockchain()
            requests.post(url, json={'blockchain': chain})
        except Exception as e:
            print(e)

    async def add_peers(self, request):
        data = await request.json()
        if data.get('address') and data.get('port'):
            self.peers.append({'address': data.get('address'), 'port': data.get('port')})
            return web.json_response({'message': 'peer added to network'}, status=200)
        return web.json_response({'message': 'unable to add peer to network'})

    async def broadcast_peers(self):
        while True:
            print('Broadcasting to peers')
            try:
                block_index = self.block.get_last_block()['index']
                if block_index > self.latest_block:
                    for peer in self.peers:
                        self.update_peers(peer)
            except Exception as e:
                print(e)
            await asyncio.sleep(10)

    async def receive_updates(self, request):
        data = await request.json()
        data = data.get('blockchain')
        try:
            self.block.replace_chain(data)
        except Exception as e:
            return web.json_response({'error': e}, status=400)

    async def get_chain(self, request):
        data = self.block.get_blockchain()
        return web.json_response(data)

    async def last_chain(self, request):
        data = self.block.get_blockchain()
        return web.json_response(data[-1])

    async def mine_coin(self, request):
        data = await request.json()
        try:
            coin_mined = self.block.validate_external_block(data)
            if coin_mined:
                return web.json_response({'message': 'Coin mined'})
            else:
                return web.json_response({'message': 'No coin mined'})
        except Exception:
            return web.json_response({'message': 'No coin mined'})

    async def current_difficulty(self, request):
        difficulty = self.block.get_difficulty(self.block.get_blockchain())
        return web.json_response({'difficulty': difficulty})

    async def start_background_tasks(self, app):
        app['broadcasts'] = app.loop.create_task(self.broadcast_peers())

    async def create_node(self, loop):
        app = web.Application()
        app.router.add_get('/chain', self.get_chain)
        app.router.add_get('/last-chain', self.last_chain)
        app.router.add_get('/current-difficulty', self.current_difficulty)
        app.router.add_post('/updates', self.receive_updates)
        app.router.add_post('/mine', self.mine_coin)
        return app

    def run_node(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_node(loop))
        app.on_startup.append(self.start_background_tasks)
        web.run_app(app, host=self.host, port=self.port)


if __name__ == '__main__':
    node = ChainServer(host='127.0.0.1', port=5000)
    node.run_node()