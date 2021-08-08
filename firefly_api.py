import json
import requests
import datetime
import tzlocal


class Firefly:
    def __init__(self, config):
        with open(config) as cnf:
            config = json.load(cnf).get('firefly')
        self.host = config['host']
        self.token = config['token']
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {self.token}'}

    def get_transactions(self, **kwargs):
        url = self.host + '/transactions'
        url += self.kwargs_to_params(**kwargs)
        return requests.get(url=url, headers=self.headers)

    def get_transaction(self, tr_id):
        url = self.host + f'/transactions/{tr_id}'
        return requests.post(url=url, headers=self.headers)

    def edit_transaction(self, tr_id, trans):
        url = self.host + f'/transactions/{tr_id}'
        payload = json.dumps(trans)
        return requests.put(url=url, headers=self.headers, data=payload)

    def delete_transaction(self, tr_id):
        url = self.host + f'/transactions/{tr_id}'
        return requests.delete(url=url, headers=self.headers)

    def add_transaction(self, trans):
        url = self.host + '/transactions'
        payload = json.dumps(trans)
        return requests.post(url=url, headers=self.headers, data=payload)

    def add_transaction_list(self, transactions):
        for t in transactions:
            self.add_transaction({'transactions': [t]})

    @staticmethod
    def kwargs_to_params(**kwargs):
        params = ''
        c = 0
        for k, v in kwargs.items():
            if c == 0:
                params += '?'
            elif c < len(kwargs):
                params += '&'
            if v:
                params += f'{k}={v}'
            c += 1
        return params


class Transaction:
    """
    Wrapper class to allow for easy creation of transaction dicts from a set of parameters
    """
    def __init__(self, type="withdrawal", date=None, amount=0.0,
                 description=None, currency_code="EUR", budget_name=None,
                 category_name=None, source_name="UNKNOWN", destination_name=None,
                 tags=None, foreign_currency_code=None, foreign_amount=None):

        if date is None:
            date = datetime.datetime.now()
        date = format_date(date).strftime('%Y-%m-%dT%H:%M:%S%z')

        # lazy way of getting all non-null parameters
        self.params = {k: v for k, v in locals().items() if v is not None and v is not self}

    def to_json(self):
        return json.dumps(self.params)


def format_date(date):
    tz = tzlocal.get_localzone()
    return tz.localize(date)
