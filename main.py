from gevent import monkey
monkey.patch_all()

import argparse
from collections import deque
from web3 import Web3, HTTPProvider
import gevent

import logging
logger = logging.getLogger(__name__)


def calc_units(estimate_seconds):
    if estimate_seconds <= 60:
        unit = 'seconds'
        value = estimate_seconds
    elif estimate_seconds <= 3600:
        unit = 'minutes'
        value = estimate_seconds / 60
    elif estimate_seconds <= 86400:
        unit = 'hours'
        value = estimate_seconds / 60 / 60
    else:
        unit = 'days'
        value = estimate_seconds / 60 / 60 / 24

    return value, unit


def print_estimate(
        estimate_seconds,
        average_estimate_seconds,
        estimate_block_speed,
        avg_block_speed,
        average_n
):
    value1, unit1 = calc_units(estimate_seconds)
    value2, unit2 = calc_units(average_estimate_seconds)

    print(
        '==Sync Estimation== latest: {} {} with {} blocks/sec || average '
        '(last {}): {} {} with {} blocks/sec'.format(
            value1, unit1, estimate_block_speed,
            average_n, value2, unit2, avg_block_speed,
        )
    )


class Ethchain(object):
    def __init__(self, ethrpc_port, averages_limit, attempt_connect=True):
        self.last_block = 0
        self.latest_estimates = deque([], averages_limit)
        self.latest_speed_estimates = deque([], averages_limit)
        self.web3 = None
        self.rpc_port = ethrpc_port
        self.connected = False
        if attempt_connect:
            self.attempt_connect(ethrpc_port)

    def attempt_connect(self, ethrpc_port, mainnet_check=True):
        if self.rpc_port == ethrpc_port and self.connected:
            # We are already connected
            return True, 'Already connected to an ethereum node'

        if self.web3:
            del self.web3

        self.web3 = Web3(HTTPProvider('http://localhost:{}'.format(ethrpc_port)))

    def check_syncing(self, seconds_passed):
        result = self.web3.eth.syncing

        if not result:
            print('Already Synced!')
            return

        current = result['currentBlock']
        if self.last_block != 0:
            processed_blocks = current - self.last_block
            top = result['highestBlock']
            top_diff = top - current
            estimate_seconds = (seconds_passed * top_diff) / processed_blocks
            estimate_block_speed = processed_blocks / seconds_passed
            self.latest_estimates.appendleft(estimate_seconds)
            self.latest_speed_estimates.appendleft(estimate_block_speed)

            average_length = len(self.latest_estimates)
            print_estimate(
                estimate_seconds,
                sum(self.latest_estimates) / average_length,
                estimate_block_speed,
                sum(self.latest_speed_estimates) / average_length,
                average_length
            )
        else:
            print('Doing lots of super complicated Math (for realsies!), have patience.')

        self.last_block = current


def main():
    p = argparse.ArgumentParser(description='ethereum syncestimator script')
    p.add_argument(
        '--ethrpc-port',
        help="The port on which to communicate with an ethereum client's RPC.",
        default=8545,
        type=int,
    )
    p.add_argument(
        '--interval',
        help="The interval in seconds in which to check sync progress",
        default=60,
        type=int,
    )
    p.add_argument(
        '--average-window',
        help="How many paste estimates should the sliding average window contain",
        default=10,
        type=int,
    )
    args = p.parse_args()
    chain = Ethchain(args.ethrpc_port, args.average_window)

    while True:
        chain.check_syncing(args.interval)
        gevent.sleep(args.interval)


if __name__ == '__main__':
    main()
