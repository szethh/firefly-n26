# firefly-n26
Tool to import CSV files from N26 to Firefly-III.

## Install

First, clone this repo: `git clone https://github.com/MateoPeri/firefly-n26`

And install the required dependencies:
`pip install -r requirements.txt`

## Config
By default, the config filename is `config.json`, but the name can be changed in the `main.py` script.

The `watchdir` folder will be scanned for new CSV files, which will be moved to `archive` after processing.

`transactions_file` is a CSV that will contain all transactions processed. It is used to determine which transactions are already in Firefly's database.
It will be created if non existent.

An example config is:
```json
{
  "n26":
  {
    "watchdir": "data/watchdir",
    "archive": "data/archive",
    "transactions_file": "data/transactions.csv",
    "default_account_name": "N26"
  },
  "firefly":
  {
    "host": "http://firefly.my-domain.com:8080/api/v1",
    "token": "BIG TOKEN HERE"
  }
}
```

Then just run the main script:
`python main.py`
