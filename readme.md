# Ethereum Sync Estimator

This is a super simple script to get a time estimation for syncing an ethereum chain.

## Installation

- Make a [python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
- Install the dependencies with pip. `pip install -r requirements.txt`

## Usage

`python main.py`

## Options

### Ethereum Client RPC port

You can set the ethereum client's RPC port with `python main.py --ethrpc-port 8545`

### Interval

You can set the interval in seconds in which to check the ethereum client for sync progress with `python main.py --interval 60`

### Averages Window

You can set the number of past checks to take into account for the average calculation with `python main.py --average-window 10`.



