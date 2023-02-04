from typing import Iterable

import yaml
import time
import os

import requests

class Lifeguard:
    base_url = 'https://api.usmobile.com/web-gateway/api/v1'

    def __init__(self) -> None:
        self.config = {}
        self.consecutive_errors = 0

    def load_config(self) -> None:
        if os.path.exists('config.yaml'):
            self.config = yaml.safe_load(open('config.yaml'))

        for attr in [
            'dryrun',
            'token', 'pool_id',
            'check_interval_minutes',
            'max_errors',
            'top_up_threshold_gb', 'top_up_gb', 'max_gb'
        ]:
            if self.config.get(attr) is None:
                e = os.environ.get(f'lifeguard_{attr}'.upper())
                if e is None:
                    raise Exception(f'Config file or env var must specify "{attr}" attribute.')
                setattr(self, attr, e)
            setattr(self, attr, self.config[attr])

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
            response = requests.get(
                self.get_pool_data_url,
                headers={
                    'USMAuthorization': 'Bearer ' + lifeguard.token,
                }
            )
        except Exception as err:
            print(f'Unexpected {err=}, {type(err)=}')
            lifeguard.consecutive_errors += 1
            if lifeguard.consecutive_errors >= int(lifeguard.max_errors):
                raise Exception('Too many errors. Giving up.')
            self.pool_data = None
            return False

        lifeguard.consecutive_errors = 0
        pool_data = response.json()
        self.pool_data = pool_data
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
            print(f'Current data limit could not be retrieved, will retry.')
            return

        if balance_in_gb >= float(lifeguard.top_up_threshold_gb):
            print(
                'You still have enough data: '
                f'Data remaining {balance_in_gb}, '
                f'Threshold {lifeguard.top_up_threshold_gb}'
            )
        elif current_data_limit >= float(lifeguard.max_gb):
            print(
                "You've exceeded your maximum quota: "
                f'Current data limit {current_data_limit}, '
                f'Max data limit {lifeguard.max_gb}'
            )
        else:
            if bool(lifeguard.dryrun) is not False:
                print('Not actually buying more data - dryrun is true')
            else:
                print('Buying more data in 10 seconds.')
                time.sleep(10)
                try:
                    requests.post(
                        self.topup_url,
                        headers={
                            'USMAuthorization': 'Bearer ' + lifeguard.token,
                        },
                        json={
                            'creditCardToken': credit_card_token,
                            'topUpSizeInGB': str(lifeguard.top_up_gb),
                        }
                    )
                except Exception as err:
                    print(f'Unexpected {err=}, {type(err)=}')
                    lifeguard.consecutive_errors += 1
                    if lifeguard.consecutive_errors > lifeguard.max_errors:
                        raise Exception('Too many errors. Giving up.')
                else:
                    self.topups_added += 1

def main() -> None:
    lifeguard = Lifeguard()
    while True:
        lifeguard.poll()

        print(f'Sleeping for {lifeguard.check_interval_minutes} minutes.')
        time.sleep(float(lifeguard.check_interval_minutes * 60))

if __name__ == '__main__':
    main()
    # Main doesn't return
