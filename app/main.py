from typing import Iterable

import os
import requests
import sys
import time
import traceback
import yaml

from captcha import get_token


def configured_bool(it) -> bool:
    """Returns False is arg is literally 'false' in any casing, else True"""
    # This is used in case a boolean config parameter is given as a string env var.
    if it is None:
        return None
    return str(it).lower().strip() != 'false'


class Lifeguard:
    base_url = 'https://api.usmobile.com/web-gateway/api/v1'

    config_types = {
        'dryrun': configured_bool,
        'username': str,
        'password': str,
        'pool_id': str,
        'check_interval_minutes': float,
        'max_errors': int,
        'top_up_threshold_gb': float,
        'top_up_gb': float,
        'top_up_delay_seconds': float,
        'max_gb': float
    }

    def __init__(self) -> None:
        self.consecutive_errors = 0
        self.token = None

    def load_config(self) -> None:
        self.config = {}

        if os.path.exists('config.yaml'):
            self.config = yaml.safe_load(open('config.yaml'))

        try:
            for attr in self.config_types.keys():
                # env var first, then config file, else raise exception
                val = os.environ.get(f'lifeguard_{attr}'.upper())
                if val is None:
                    val = self.config.get(attr)
                    if val is None:
                        raise Exception(f'Config file or env var must specify "{attr}" attribute.')

                # set attribute & ensure it's convertible to expected type
                setattr(self, attr, self.config_types[attr](val))
        except Exception as e:
            raise Exception('config error') from e

    def get_pool_ids(self) -> Iterable[str]:
        # Currently supports only one
        return [ self.config['pool_id'] ]

    def poll(self) -> None:
        # Reload config on each iteration in case it changes
        self.load_config()

        for pool_id in self.get_pool_ids():
            pool = Pool(self, pool_id)
            if pool.get_pool_data():
                pool.perform_topup()


class Pool:
    def __init__(self, lifeguard: Lifeguard, pool_id: str) -> None:
        self.lifeguard = lifeguard

        self.base_topups = None
        self.topups_added = 0

        self.pool_id = pool_id
        self.get_pool_data_url = f'{lifeguard.base_url}/pools/{pool_id}'
        self.topup_url = f'{self.get_pool_data_url}/topUpAndBasePlan'

    def get_pool_data(self) -> bool:
        lifeguard = self.lifeguard

        try:
            if not lifeguard.token:
                lifeguard.token = get_token(lifeguard.username, lifeguard.password)
            response = None
            response = requests.get(
                self.get_pool_data_url,
                headers={
                    'USMAuthorization': 'Bearer ' + lifeguard.token,
                }
            )
            pool_data = response.json()
            response.raise_for_status()
            self.pool_data = pool_data
        except Exception as err:
            # The occasional 500 error is not *really* unexpected
            if response is None or response.status_code != 500:
                print(f'Unexpected {err=}, {type(err)=}')
                lifeguard.token = None
            lifeguard.consecutive_errors += 1
            if lifeguard.consecutive_errors >= lifeguard.max_errors:
                raise Exception('Too many errors. Giving up.')
            self.pool_data = None
            return False

        lifeguard.consecutive_errors = 0
        return True

    def perform_topup(self) -> None:
        lifeguard = self.lifeguard

        # Safety check. Make sure the topups we're buying are getting credited.
        if self.base_topups is None:
            self.base_topups = len(self.pool_data['topups'])
        if self.topups_added > len(self.pool_data['topups']) - self.base_topups:
            raise Exception('Missing topups - check your account!!!')

        balance_in_gb = self.pool_data['balanceInMB'] / 1024
        credit_card_token = self.pool_data['creditCardToken']
        current_data_limit = self.pool_data['basePlanInGB'] + sum(
            topup['topUpSizeInGB'] for topup in self.pool_data['topups']
        )

        if current_data_limit <= 0:
            print(f'Current data limit could not be retrieved, will retry.', file=sys.stderr)
            return

        if balance_in_gb >= lifeguard.top_up_threshold_gb:
            print(
                'You still have enough data: '
                f'Data remaining {balance_in_gb}, '
                f'Threshold {lifeguard.top_up_threshold_gb}'
            )
        elif current_data_limit >= lifeguard.max_gb:
            print(
                "You've exceeded your maximum quota: "
                f'Current data limit {current_data_limit}, '
                f'Max data limit {lifeguard.max_gb}'
            )
        else:
            if lifeguard.dryrun is True:
                print('Not actually buying more data - dryrun is true')
            else:
                delay = lifeguard.config['top_up_delay_seconds']
                if delay > 0:
                    print(f'Buying more data in {delay} seconds.')
                    time.sleep(delay)
                try:
                    response = requests.post(
                        self.topup_url,
                        headers={
                            'USMAuthorization': 'Bearer ' + lifeguard.token,
                        },
                        json={
                            'creditCardToken': credit_card_token,
                            'topUpSizeInGB': lifeguard.top_up_gb,
                        }
                    )
                    response.raise_for_status()
                except Exception as err:
                    if lifeguard.consecutive_errors > lifeguard.max_errors:
                        raise Exception('Too many errors. Giving up.')
                    print(f'Unexpected {err=}, {type(err)=}')
                    lifeguard.consecutive_errors += 1
                else:
                    self.topups_added += 1


def main() -> None:
    try:
        lifeguard = Lifeguard()
        while True:
            lifeguard.poll()

            if lifeguard.config["check_interval_minutes"] <= 0:
                break

            print(f'Sleeping for {lifeguard.check_interval_minutes} minutes.')
            time.sleep(lifeguard.check_interval_minutes * 60)

        sys.exit(0)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
    # Main doesn't return
