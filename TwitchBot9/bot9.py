import math
import random
import socket
from pathlib import Path
from emoji import demojize
import re
import time
import multiprocessing
from login import *
import requests
from bot9_rule import *
from zpravy import *
import threading

# channels = [{"channel":"nazev", "rules":"url" "join_message":"join message", "out_message":"out message", "shutdown_comand":"shutdown_comand"}]


class bot(threading.Thread):
    def __init__(
        self, nickname, channel, rules: Rules, join_mesage, out_message, shutdown_comand
    ) -> None:
        super().__init__()
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.sock = socket.socket()
        self.join_mesage = join_mesage
        self.out_message = out_message
        self.nickname = nickname
        self.shutdown_comand = shutdown_comand
        self.login = login()
        self.id = self.login.get_user_id(self.nickname)

        self.channel = channel
        self.rules = rules
        end_rule = Rule(
            {
                "in_text": 0,
                "rule": [shutdown_comand],
                "send_all": True,
                "messages": [self.out_message],
                "message_type": "PRIVMSG",
                "funnction": "bot.vypnout",
                "number_of_use": -1,
                "counter": 0,
            }
        )
        self.rules.mesage_rules.append(end_rule)
        # print (self.rules)

        self.last_send = 0
        self.message_to_send = []
        self.whisper_to_send = []
        self.last_send_mesage = ""
        self.stop_event = threading.Event()
        self.start()

    def run(self):
        self.connect_to_server()
        self.connect_to_chanel(self.channel)
        self.read_thread = threading.Thread(target=self.read_chat)
        self.send_thread = threading.Thread(target=self.sending_messages)
        self.read_thread.start()
        self.send_thread.start()
        self.read_thread.join()
        self.send_thread.join()

    def read_chat(self):
        while not self.stop_event.is_set():
            self.read_mesage()

    def sending_messages(self):
        while not self.stop_event.is_set():
            if len(self.message_to_send) == 0:
                continue
            if self.last_send + 1.5 > time.time():
                time.sleep(self.last_send + 1.5 - time.time())
                continue
            # print (self.message_to_send)
            self.send_mesag(self.message_to_send[0])
            self.message_to_send.pop(0)

    def connect_to_server(self):
        """
        Connects to the IRC server using the access token obtained from #login.

        Returns:
            None
        """
        self.sock.connect((self.server, self.port))
        self.sock.send(f"PASS oauth:{self.login.returnToken()}\n".encode("utf-8"))
        self.sock.send(f"NICK {self.nickname}\n".encode("utf-8"))

    def connect_to_chanel(self, chanel):
        """
        Connect to a Twitch channel and join with a specified message.

        Parameters:
            channel (str): The name of the Twitch channel to connect to.
            join_message (str): The message to send upon joining the channel.

        Returns:
            None
        """
        self.sock.send(f"JOIN #{chanel}\n".encode("utf-8"))
        self.sock.send(f"CAP REQ :twitch.tv/commands\n".encode("utf-8"))
        self.sock.send(f"CAP REQ :twitch.tv/tags\n".encode("utf-8"))
        # self.sock.send(f"CAP REQ :twitch.tv/membership\n".encode('utf-8'))

        print(self.sock.recv(2048).decode("utf-8"))
        print(self.sock.recv(2048).decode("utf-8"))

        self.send_mesag(self.join_mesage)

    # TODO
    def conect_to_api(self):
        pass

    def send_api_request(self, type_of_request, params, data):
            url = "https://api.twitch.tv/helix/" + type_of_request
            login = {
                "Client-Id": self.login.client_id,
                "Authorization": f"Bearer {self.login.access_token}",
            }
            # encoded_data = json.dumps(data, ensure_ascii=False).encode('utf-8') 
            request = requests.post(
                url, params=params, headers=login, data=data
            )
            if request.status_code == 204:
                print("sent whisper")
            else:
                print(request.text)
            return request.status_code

    def read_mesage(self):
        """
        Reads messages from the connected channel.

        This method reads a message from the connected channel and processes it accordingly.
        If the received message is a PING request, it responds with a PONG and returns False.
        If the message contains "RECONNECT", it initiates reconnection and returns False.
        If the message is a USERNOTICE, it returns False. Otherwise, it processes the message
        and returns True if it is not empty.

        Returns:
            bool: True if a non-empty message is received, False otherwise.
        """
        resp = self.sock.recv(2048).decode("utf-8")
        resp = resp.replace(" \U000e0000", "")
        # print(resp)

        if resp.startswith("PING"):  # co 5 minut
            self.sock.send("PONG\n".encode("utf-8"))
            print("PING PONG")
            return False
        if "RECONNECT" in resp:
            print("RECONNECT")
            self.reconnect()
            return False
        elif len(resp) > 0:
            if "USERNOTICE" in resp:
                return False
            if "PRIVMSG" in resp or "WHISPER" in resp:
                self.get_mesage(resp)
            return True
        else:
            return False

    def get_mesage(self, message):
        zprava = Zprava(self, message)
        # print(zprava)

    def send_message(self, message):
        # print(message, "Zprava")
        if isinstance(message, list):
            for mess in message:
                self.message_to_send.append(mess)
        else:
            self.message_to_send.append(message)

    def send_whisper(self, message, user_name, user_id):
        """odešle zprávu pomoci WHISPER, můžete šeptat maximálně 40 unikátním příjemcům za den"""
        # Můžete šeptat maximálně 40 unikátním příjemcům za den.
        params = {"from_user_id": self.id, "to_user_id": user_id}
        if isinstance( message, list):
            for mess in message:
                response = self.send_api_request("whispers", params, {"message": mess})
        else:
            self.send_api_request("whispers", params, {"message": message})

    def send_mesag(self, message):
        """
        odeslání zprávy do kanálu, pokud zpráva odpovídá uživateli obsahuje @ tak oznaží posledního pisatele,
        * Pokud uživatel není vysílatelem nebo moderátorem kanálu, robot může odeslat maximálně 20 zpráv za 30 sekund.
        * Pokud je uživatel vysílatelem nebo moderátorem kanálu, bot může odeslat maximálně 100 zpráv za 30 sekund.

        Args:
            message (str): zpráva která má být odslána
            chanel (str, optional): _description_. Defaults to "".
        """
        print(self.sock.send(f"PRIVMSG #{self.channel} :{message} \n".encode("utf-8")))
        # print(message)
        time.sleep(1.5)
        print("send")

    def send_wisp_mesag(self, message, user=None):
        pass
    def reconnect(self):

        self.send_mesag("/disconnect", self.channel)
        if self.login.validate_token(self.token) != True:
            self.login.get_token()
        self.token = self.login.returnToken()
        self.connect_to_server()
        self.sock.send(f"JOIN #{self.channel}\n".encode("utf-8"))
        self.sock.send(f"CAP REQ :twitch.tv/commands\n".encode("utf-8"))
        self.sock.send(f"CAP REQ :twitch.tv/tags\n".encode("utf-8"))
        # self.sock.send(f"CAP REQ :twitch.tv/membership\n".encode('utf-8'))

        print(self.sock.recv(2048).decode("utf-8"))
        print(self.sock.recv(2048).decode("utf-8"))

    def vypnout(self):
        """bot se rozloučí a odpojí se od severu"""
        konec = "/disconnect"
        self.send_mesag(self.out_message, self.channel)
        self.send_mesag(konec, self.channel)
        self.stop_event.set()
        return True


class clovek:
    def __init__(self, nickname) -> None:
        self.nickname = nickname
        self.cesta = Path(__file__).with_name("odpovedi.txt")

    def save_mesage(self, mesage):
        textak = open(self.cesta, "a+", encoding="utf-8")
        cas = time.strftime("%H:%M:%S", time.localtime())
        mesage = cas + " - " + self.nickname + " - " + mesage + "\n"
        # print (mesage)
        textak.write(mesage)
