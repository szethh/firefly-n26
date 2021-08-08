# firefly-n26
Tool to import CSV files from N26 to Firefly-III. Since using the [API](https://github.com/femueller/python-n26) requires manual verification anyway, I opted for making a tool that would import directly from the CSV files.

## Install

First, clone this repo: `git clone https://github.com/MateoPeri/firefly-n26`

And install the required dependencies:
`pip install -r requirements.txt`

## Config
By default, the config filename is `config.json`, but the name can be changed in the `main.py` script.

The `watchdir` folder will be scanned for new CSV files, which will be moved to `archive` after processing.

`transactions_file` is a CSV that will contain all transactions processed. It is used to determine which transactions are already in Firefly's database.
It will be created if non existent.

`default_account_name` is used to set the destination name in firefly. Set this to the name of your account in Firefly.

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

## Usage
Go to [N26's website](https://app.n26.com/downloads), pick a date range and click on 'Download CSV'.

Move it into your `watchdir` folder and run the main script:

`python main.py`
