import requests, sys, warnings
from typing import List, Union
from .backtest import Backtest

API_KEY = None

def push(backtests: Union[Backtest, List[Backtest]], api_key=None) -> None:
    if not isinstance(api_key, str):
        if not isinstance(API_KEY, str):
            raise ValueError("Must pass a valid API key")
        else:
            api_key = API_KEY

    url = 'https://us-central1-jefferson-street-analytics.cloudfunctions.net/backtest-upload'

    if isinstance(backtests, Backtest):
        bks = [backtests]
    elif isinstance(backtests, list):
        bks = backtests
    else:
        raise TypeError(f"Invalid type for backtest: {type(backtests)}")
    
    for bk in bks:
        params = {'api_key': api_key}
        additional_data = bk.additional_data

        if 'tags' in additional_data:
            tags = additional_data['tags']
            if isinstance(tags, str):
                params['tags'] = tags
            else:
                params['tags'] = ','.join(tags)

        data = bk.to_json()
        size_mb = sys.getsizeof(data)/(1024**2)
        if size_mb > 100: #for reference, 50 securities and 20 years of daily prices results in a ~35MB upload
            warnings.warn(
                "You are pushing a backtest larger than 100MB. "
                "You may experience long wait times and possibly "
                "a timeout error. We are working to improve this "
                "in the future."
            )
        response = requests.post(url, data=data, params=params)
        if response.status_code != 201:
            warnings.warn(
                f"There was an error pushing backtest named '{bk.name}': {response.text}"
            )
        

