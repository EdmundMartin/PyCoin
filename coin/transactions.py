

class UnspentTransactionOutputs:

    def __init__(self, transaction_out_id, transaction_out_id_index, address, amount):
        self.transaction_out_id = transaction_out_id
        self.transaction_out_id_index = transaction_out_id_index
        self.address = address
        self.amount = amount


class TransactionInputs:

    def __init__(self, transacction_out_id, transaction_out_index, signature):

        self.transaction_out_id = transacction_out_id
        self.transaction_out_index = transaction_out_index
        self.signature = signature


class TransactionOutputs:

    def __init__(self, address, amount):
        assert isinstance(address, str)
        assert isinstance(amount, (float, int))

        self.address = address
        self.amount = amount


class Transaction:

    def __init__(self, id, transactions_in, transactions_out):
        assert isinstance(id, str)
        assert isinstance(transactions_in, list)
        assert isinstance(transactions_out, list)

        self.id = id
        self.transactions_in = transactions_in
        self.transactions_out = transactions_out