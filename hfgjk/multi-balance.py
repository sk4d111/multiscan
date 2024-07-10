import csv
import requests
import time
from tqdm import tqdm

# Замените на ваш API ключ Etherscan и BscScan
ETHERSCAN_API_KEY = '7PE3BRYX7QEH3HPZMZDSSVXX6TE65W7SGY'
BSCSCAN_API_KEY = 'HIVCUJU6K5MZWVU732C5RPEKB7KGV5NDSV'
ETHERSCAN_API_ENDPOINT = 'https://api.etherscan.io/api'
BSCSCAN_API_ENDPOINT = 'https://api.bscscan.com/api'
ETH_PRICE_URL = 'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD'
BNB_PRICE_URL = 'https://min-api.cryptocompare.com/data/price?fsym=BNB&tsyms=USD'

def get_balance(address, chain):
    if chain == 'ethereum':
        api_key = ETHERSCAN_API_KEY
        api_endpoint = ETHERSCAN_API_ENDPOINT
    elif chain == 'bsc':
        api_key = BSCSCAN_API_KEY
        api_endpoint = BSCSCAN_API_ENDPOINT
    else:
        return None

    params = {
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': api_key
    }
    response = requests.get(api_endpoint, params=params)
    if response.status_code == 200:
        result = response.json()
        if result['status'] == '1':
            # Конвертируем баланс из Wei в Ether или BNB
            balance = int(result['result']) / 1e18
            return balance
    return None

def get_exchange_rate(url):
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        usd_rate = result.get('USD')
        if usd_rate is None:
            print("Error: Missing 'USD' key in response")
        return usd_rate
    else:
        print(f"Error: Failed to fetch exchange rate, status code: {response.status_code}, response: {response.text}")
    return None

def process_wallets(input_file, output_file):
    eth_usd_rate = get_exchange_rate(ETH_PRICE_URL)
    bnb_usd_rate = get_exchange_rate(BNB_PRICE_URL)
    if eth_usd_rate is None or bnb_usd_rate is None:
        print("Error: Could not retrieve exchange rates")
        return

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        writer.writerow(['Адрес', 'Общий Баланс (USD)'])  # Заголовок

        addresses = list(reader)
        for row in tqdm(addresses, desc='Processing wallets', unit='wallet'):
            address = row[0].strip()
            eth_balance = get_balance(address, 'ethereum')
            bsc_balance = get_balance(address, 'bsc')

            if eth_balance is not None:
                eth_usd_value = eth_balance * eth_usd_rate
            else:
                eth_usd_value = 0

            if bsc_balance is not None:
                bnb_usd_value = bsc_balance * bnb_usd_rate
            else:
                bnb_usd_value = 0

            total_usd_value = eth_usd_value + bnb_usd_value
            writer.writerow([address, total_usd_value])

            # Задержка чтобы не превысить ограничения API
            time.sleep(0.2)

# Использование функции
input_file = 'input_addresses.csv'  # Замените на имя вашего входного файла
output_file = 'output_balances.csv'  # Имя выходного файла

process_wallets(input_file, output_file)
print(f"Результаты записаны в {output_file}")
