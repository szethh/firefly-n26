from firefly_api import Firefly
from n26 import N26

if __name__ == '__main__':
    config = 'config.json'  # CHANGE ME
    # create N26 API object
    n26 = N26(config)
    ff = Firefly(config)
    # Scan the watchdir (set in your config file)
    transactions = n26.scan_watchdir()
    print(f'Adding {len(transactions)} transactions!')
    # add each transaction to Firefly
    ff.add_transaction_list(transactions)
