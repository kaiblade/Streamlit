import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os
import pprint
from dotenv import load_dotenv

load_dotenv()

key=os.environ.get('CMC_API_KEY')
url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': key,
}
parameters = {
'symbol':'LUNA'

}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    print(data)
    # pp.pprint(data)
    cir_supply = f"{(data['data']['LUNA']['circulating_supply']):,}"
    tot_supply = f"{(data['data']['LUNA']['total_supply']):,}"

except (ConnectionError, Timeout, TooManyRedirects) as e:
    data = json.loads(response.text)
    pp.pprint(data)

