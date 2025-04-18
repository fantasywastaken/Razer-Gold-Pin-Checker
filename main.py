from loguru import logger
import concurrent.futures
import tls_client
import capsolver
import random
import json
import time
import sys

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

EMAIL = config['EMAIL']
PASSWORD = config['PASSWORD']
CAPSOLVER_KEY = config['CAPSOLVER_KEY']

session = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=True,
)

COMMON_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://razerid.razer.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://razerid.razer.com/',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

def solve_captcha():
    capsolver.api_key = CAPSOLVER_KEY
    task_data = {
        "type": "ReCaptchaV2TaskProxyLess",
        "websiteKey": "6LcpNTsnAAAAAHwAEafqijTr6hku2UFZ8qxfmHG8",
        "websiteURL": "https://gold.razer.com"
    }
    solution = capsolver.solve(task_data)
    return solution['gRecaptchaResponse']

def get_client_id():
    response = session.get('https://razerid-assets.razerzone.com/static/js/10.332f6a7f.chunk.js')
    client_id = response.text.split('REACT_APP_RAZER_ID_CLIENT_ID:"')[1].split('",')[0]
    return client_id

login_token = None
user_id = None

def login():
    global login_token, user_id
    if login_token and user_id:
        return
    headers = COMMON_HEADERS.copy()
    json_data = {
        'data': f'<COP><User><email>{EMAIL}</email><password>{PASSWORD}</password></User><ServiceCode>0060</ServiceCode></COP>',
        'encryptedPw': 'rev1',
        'clientId': get_client_id(),
    }
    response = session.post('https://razerid.razer.com/api/emily/7/login/get', headers=headers, json=json_data)
    if "valid username and password" in response.text:
        logger.success(f"Successfully logged in to account: {EMAIL}")
        user_id = response.text.split('<User><ID>')[1].split('</ID>')[0]
        login_token = response.text.split('<Token>')[1].split('</Token>')[0]
    else:
        logger.error(f"Login failed for account: {EMAIL}. Please try again.")
        sys.exit(1)

gold = 0

def check_code(code):
    global login_token, user_id, gold
    headers = COMMON_HEADERS.copy()
    headers.update({
        'x-razer-accesstoken': login_token,
        'x-razer-language': 'tr',
        'x-razer-razerid': user_id,
    })
    json_data = {
        'paymentChannelId': 51,
        'regionId': '18',
        'currencyCode': 'TRY',
        'pinCode': code,
        'permalink': 'razer-gold-pin',
        'recaptchaToken': solve_captcha(),
    }
    logger.debug(f"Checking code: {code}")
    response = session.post('https://gold.razer.com/api/gold/reload/h2hvoucher', headers=headers, json=json_data)
    try:
        response_data = json.loads(response.text)
        if 'gold' in response_data and 'currencyCode' in response_data:
            gold += response_data['gold']
            logger.success(f"Code successfully redeemed [{response_data['gold']}{response_data['currencyCode']}] ({code})")
        else:
            logger.error(f"Code redemption failed ({code})")
            with open('wrong.txt', 'a') as file:
                file.write(f"{code}\n")
    except json.JSONDecodeError:
        logger.error(f"Code check failed ({code})")

def main():
    global login_token, user_id, gold
    login()
    with open('codes.txt', 'r') as file:
        codes = file.read().splitlines()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for code in codes:
            executor.submit(check_code, code)
            time.sleep(3)
    logger.debug(f"Total redeemed balance at end of process: {gold} TRY")
    headers = COMMON_HEADERS.copy()
    headers.update({
        'x-razer-accesstoken': login_token,
        'x-razer-language': 'tr',
        'x-razer-razerid': user_id,
    })
    response = session.get("https://gold.razer.com/api/gold/balance", headers=headers)
    logger.debug(f"Final account balance: {response.json()['walletGold']['totalGold']}{response.json()['walletGold']['currencyCode']}")

if __name__ == "__main__":
    main()
