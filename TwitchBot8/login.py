import requests
import json
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pathlib import Path


class login:
    def __init__(self) -> None:
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.code = None
        self.refresh_token = None
        self.expires_time = 0
        self.load_bot_login()
        if self.validate_token(self.access_token) != True:
            self.get_token()

    def returnToken(self):
        return self.access_token

    """načte date ze souboru"""
    def load_bot_login(self):
        print ("loading login")
        with open(Path(__file__).with_name("login.json"), "r") as soubor:
            content = json.load(soubor)
            self.client_id = content["client_id"]
            self.client_secret = content["client_secret"]
            self.code = content["code"]
            self.access_token = content["access_token"]
            self.refresh_token = content["refresh_token"]
            self.expires_time = content["expires_time"]

    """uloží data do souboru"""
    def save_login(self):
        with open(Path(__file__).with_name("login.json"), "w") as soubor:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "access_token": self.access_token,
                "code": self.code,
                "refresh_token": self.refresh_token,
                "expires_time":self.expires_time
            }
            soubor.write(json.dumps(data))
    "zkontroluje zda je access token platný"
    def validate_token(self, token):
        print ("validate access token")
        if self.access_token == None:
            return False
        url = "https://id.twitch.tv/oauth2/validate"
        r = requests.get(url, headers={"Authorization": f"Oauth {token}"})
        if r.status_code == 200:
            r = r.json()
            self.expires_time = time.time() + int(r['expires_in'])
            return True
        elif r.status_code == 401:
            return False
        else:
            raise Exception(f"Unrecognised status code on validate {r.status_code}")
    """získá user code pro získání access tokenu dle nastavených scope"""
    def get_code(self):
        print("autetntizacion")
        # self.access_token = None
        # self.refresh_token = None
        # self.expires_time = None
        options = Options()
        firefox_profile = FirefoxProfile(
            "C:/Users/sobol/AppData/Roaming/Mozilla/Firefox/Profiles/sxf74908.default-release"
        )
        options.profile = firefox_profile
        options.add_argument("user-agent=your_user_agent_string")
        driver = webdriver.Firefox(options=options)
        request_data = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": "https://bot.soboliucho.cz/response.php",
            "scope": "channel:bot channel:moderate chat:edit chat:read channel:read:polls channel:manage:polls channel:read:predictions channel:manage:predictions channel:manage:raids clips:edit user:manage:whispers whispers:read whispers:edit",
            # "analytics:read:extensions analytics:read:games bits:read channel:manage:ads channel:read:ads channel:manage:broadcast channel:read:charity channel:edit:commercial channel:read:editors channel:manage:extensions channel:read:goals	channel:read:guest_star	channel:manage:guest_star channel:read:hype_train channel:read:subscriptions channel:read:vips channel:manage:vips channel:manage:moderators channel:read:redemptions channel:manage:redemptions channel:manage:schedule	channel:read:stream_key	channel:manage:videos ",
        }
        request_data = urlencode(request_data)
        driver.get(f"https://id.twitch.tv/oauth2/authorize?{request_data}")
        try:
            WebDriverWait(driver, 120).until(EC.url_contains("bot.soboliucho.cz"))
            print("Successfully navigated to bot.soboliucho.cz")

        except TimeoutError:
            print(
                "Timeout: Unable to navigate to bot.soboliucho.cz within the specified time"
            )
            return None
        code = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "code"))
        )
        code = code.text
        self.code = code
        self.save_login()
        # token = None
        driver.quit()
        return code
    """sízká access token a uloží jej, pokud není code tak jej získá taky"""
    def get_token(self):
        if self.code == None:
            self.get_code()
        if self.refresh_token == None:
            print("get new token")
            url = "https://id.twitch.tv/oauth2/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": self.code,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:1000",
            }
            request = requests.post(url, data=data).json()
            # request = json.loads(request)
            try:
                self.access_token = request['access_token']
                self.refresh_token = request['refresh_token']
                self.expires_time = time.time() + int(request['expires_in'])
            except:
                print("Unexpected response on redeeming auth code:")
                print(request)
        else:
            self.refresh_token_fun()
        self.save_login()
    """aktualizuje re"""
    def refresh_token_fun(self):
        print("refresh token")
        url = "https://id.twitch.tv/oauth2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        request = requests.post(url, data=data).json()
        try:
            self.access_token = request['access_token']
            self.refresh_token = request['refresh_token']
            # self.expires_time = time.time() + int(request['expires_in'])
            self.validate_token(self.access_token)
        except:
            print("Unexpected response on redeeming auth code:")
            print(request)
            self.get_code()
            self.refresh_token = None
            self.get_token()

    def get_user_id(self, name):
        url = "https://api.twitch.tv/helix/users"
        hearder = {
            "Client-Id": self.client_id,
            'Authorization': f'Bearer {self.access_token}',
        }
        data = {
            "login": name
        }
        request = requests.get(url, params=data, headers=hearder).json()
        return int(request["data"][0]["id"])

# log = login()
# print(log.get_user_id("soboliuchobot")["data"][0]["id"])
# log.code = None
# log.refresh_token = None
# log.get_token()
# with open("login.json", "w") as soubor:
#     data = {
#         "client_id": "oty1mh8mk8bagm19nv1ypkgzmxx0ls",
#         "client_secret": "4zf09y7p50780gp0wbskvqoq4l7wuz",
#         "access_token": None,
#     }
#     soubor.write(json.dumps(data))
# log.client_id="oty1mh8mk8bagm19nv1ypkgzmxx0ls"
# log.client_secret="4zf09y7p50780gp0wbskvqoq4l7wuz"
# log.save_login()