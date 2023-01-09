import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import os
import msal
import time

email = "weddingAudioBook@outlook.com"
password = "fiverrRPi2023!"
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def generate_access_token(app_id, scopes):
    # Save Session Token as a token file
    access_token_cache = msal.SerializableTokenCache()

    # read the token file
    if os.path.exists('ms_graph_api_token.json'):
        access_token_cache.deserialize(open("ms_graph_api_token.json", "r").read())
        token_detail = json.load(open('ms_graph_api_token.json',))
        token_detail_key = list(token_detail['AccessToken'].keys())[0]
        token_expiration = datetime.fromtimestamp(int(token_detail['AccessToken'][token_detail_key]['expires_on']))
        if datetime.now() > token_expiration:
            os.remove('ms_graph_api_token.json')
            access_token_cache = msal.SerializableTokenCache()

    # assign a SerializableTokenCache object to the client instance
    client = msal.PublicClientApplication(client_id=app_id, token_cache=access_token_cache)

    accounts = client.get_accounts()
    if accounts:
        # load the session
        token_response = client.acquire_token_silent(scopes, accounts[0])
    else:
        # authenticate your account as usual
        flow = client.initiate_device_flow(scopes=scopes)
        print(flow)
        print('user_code: ' + flow['user_code'])

        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--no-sandbox')
        # driver = webdriver.Chrome(options=options)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get('https://microsoft.com/devicelogin')

        xpath_token = '/html/body/div/form/div/div/div[1]/div[3]/div/div/div/div[4]/div/input'
        xpath_username = '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[3]/div[2]/div/input[1]'
        xpath_password = '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[4]/div/div[2]/input'
        xpath_allow = '/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/input'
        token_input = WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH, xpath_token)))
        token_input.send_keys(flow['user_code'])
        token_input.send_keys(Keys.RETURN)
        uid_input = WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH, xpath_username)))
        uid_input.send_keys(email)
        uid_input.send_keys(Keys.RETURN)
        pwd_input = WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH, xpath_password)))
        pwd_input.send_keys(password)
        pwd_input.send_keys(Keys.RETURN)
        allow_input = WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH, xpath_allow)))
        allow_input.send_keys(Keys.RETURN)
        time.sleep(3)
        driver.close()

        token_response = client.acquire_token_by_device_flow(flow)

    with open('ms_graph_api_token.json', 'w') as _f:
        _f.write(access_token_cache.serialize())

    return token_response