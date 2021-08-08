import datetime
import json
import re

import pandas as pd
import glob
from pathlib import Path
from firefly_api import Transaction


class N26:
    def __init__(self, config):
        with open(Path(config)) as cnf:
            config = json.load(cnf).get('n26')
        self.default_account_name = config['default_account_name']
        self.watchdir = Path(config['watchdir'])
        self.archive = Path(config['archive'])
        self.data_f = Path(config['data'])
        try:
            self.data = pd.read_csv(self.data_f)
        except:  # FileNotFound, EmptyDataError, malformed data???
            self.data = pd.DataFrame()

    def add_csv(self, f):
        """
        Adds a csv to the existing data.
        :param f: File path to the csv file.
        :return: Diff between the two
        """
        d = self.read_csv(f)
        # get diff
        diff = d[~d.isin(self.data)].dropna()

        # merge new data with existing data
        cc = pd.concat([self.data, d])
        cc.drop_duplicates(inplace=True)
        self.data = cc
        return diff

    def scan_watchdir(self):
        files = glob.glob(str(Path(self.watchdir / '*.csv')))
        # select csv files, sort them by name (they should be date-named)
        new_transactions = []
        for f in files:
            new_transactions.append(self.add_csv(f))
            f = Path(f)
            f.rename(self.archive/f.name)

        # save new data to csv
        self.data.to_csv(str(self.data_f))

        # join all new transactions
        new = pd.concat(new_transactions).drop_duplicates()
        return self.add_transactions(new)

    def read_csv(self, path):
        # read & clean
        new_data = pd.read_csv(path)
        return self.clean_df(new_data)

    @staticmethod
    def clean_df(df):
        dff = df.copy()
        # select categorical
        d1 = dff.select_dtypes(include=['object'])
        # fill them
        dff[d1.columns] = dff[d1.columns].fillna('NONE')
        # fill number types
        dff.fillna(0, inplace=True)
        return dff

    def add_transactions(self, df):
        transactions = []
        for index, row in df.iterrows():  # iterate over each row
            transactions.append(self.add_transaction(row))
        # firefly API can accept a list of transactions
        # so send it (not actually sent from here,
        # just return JSON to be used in an external script)
        return transactions

    def add_transaction(self, trans):
        """
        Converts a N26 CSV transaction to a JSON for use with Firefly's API.
        :param trans: A row (Series) object of the N26 dataframe.
        :return: A JSON formatted to use with the Firefly API.
        """

        # select the amount column (name depends on currency code)
        amt_col = trans.loc[trans.index.str.contains(r'Amount \(.{3}\)')]
        # get value according to currency
        amount = amt_col.values[0]

        # get currency code (we need to match regex again, this time to get the code)
        curr = re.match(r'Amount \((.{3})\)', amt_col.index[0]).group(1)

        # get foreign currency data, set them to None if not applicable
        foreign_curr = trans['Type Foreign Currency']
        foreign_amt = trans['Amount (Foreign Currency)']
        if foreign_curr == 'NONE' or abs(foreign_amt - amount) > 0.05:
            foreign_amt = None
            foreign_curr = None

        destination_name = self.default_account_name
        source_name = trans['Payee'].strip('\n')
        # sometimes N26 gives money from referrals
        # if your account is also named 'N26' the transaction
        # won't make a difference (you would be paying yourself)
        # so we change the name
        if destination_name == source_name:
            source_name += '_Bank'
        # for now only 2 types
        type = 'withdrawal' if amount < 0 else 'deposit'
        if amount < 0:
            source_name, destination_name = destination_name, source_name

        desc = trans['Payment reference'] or trans['Transaction type']
        date = datetime.datetime.strptime(trans['Date'], '%Y-%m-%d')

        amount = str(abs(amount))
        if foreign_amt:
            foreign_amt = str(abs(foreign_amt))
        tr = Transaction(type=type, date=date, amount=amount,
                         description=desc, currency_code=curr,
                         foreign_currency_code=foreign_curr, foreign_amount=foreign_amt,
                         category_name=trans['Category'], source_name=source_name,
                         destination_name=destination_name, tags=['n26_bot'])
        return tr.params
