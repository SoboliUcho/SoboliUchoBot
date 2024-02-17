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

# mesage
# Username: self.mesage["username"]
# Channel self.mesage[channel]
# Message: self.mesage["message"]
# mesage_type: self.mesage[mesage_type]


class bot:
    def __init__(self, channel, login: login, nickname, join_mesage) -> None:
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.nickname = nickname
        self.login = login
        self.token = login.access_token
        # self.channel = "#" + channel
        self.channel = channel
        self.sock = socket.socket()
        self.join_mesage = join_mesage
        self.mesage = {
            "username": "",
            "channel": "",
            "message": "",
            "mesage_type": "",
        }
        self.tags = {}
        self.lide = []
        self.id = login.get_user_id(self.nickname)
        # self.soubor = "zpravy_grap5.txt"
        # self.cesta = Path(__file__).with_name(self.soubor)
        # self.zpravy = open(self.cesta,"a+",encoding="utf-8")
        # self.zpravy.seek(0)

    """
    pomocí acces tokenu získaného z #login se připojí na irc server
    """

    def connect_to_server(self):
        self.sock.connect((self.server, self.port))

        self.sock.send(f"PASS oauth:{self.token}\n".encode("utf-8"))
        self.sock.send(f"NICK {self.nickname}\n".encode("utf-8"))

    """
    připojení do kanálu kde naslouchá posíláným zprávám
    """

    def connect_to_chanel(self, chanel):
        self.sock.send(f"JOIN #{chanel}\n".encode("utf-8"))
        self.sock.send(f"CAP REQ :twitch.tv/commands\n".encode("utf-8"))
        self.sock.send(f"CAP REQ :twitch.tv/tags\n".encode("utf-8"))
        # self.sock.send(f"CAP REQ :twitch.tv/membership\n".encode('utf-8'))

        print(self.sock.recv(2048).decode("utf-8"))
        print(self.sock.recv(2048).decode("utf-8"))

        self.send_mesag(self.join_mesage, self.channel)

    # TODO
    def conect_to_api(
        self,
    ):
        pass

    """příjmání zpráv ze připojenéhjo kanálu, zde také příjmá WHISPER"""

    def read_mesage(self):
        resp = self.sock.recv(2048).decode("utf-8")
        # print("zprava:")
        resp = resp.replace(" \U000e0000", "")
        # print(resp)

        # self.zpravy.seek(0,2)
        # self.zpravy.write(resp)
        # self.zpravy.write("\n\n")

        if resp.startswith("PING"):  # co 5 minut
            self.sock.send("PONG\n".encode("utf-8"))
            print("PING PONG")
            self.mesage = {
                "username": "",
                "channel": "",
                "message": "",
                "mesage_type": "",
            }
            return self.mesage
        elif len(resp) > 0:
            self.take_tags(resp)
            if "USERNOTICE" in resp:
                self.mesage = {
                    "username": "",
                    "channel": "",
                    "message": "",
                    "mesage_type": "",
                }
                return self.mesage
            if "RECONNECT" in resp:
                self.mesage = {
                    "username": "",
                    "channel": "",
                    "message": "",
                    "mesage_type": "",
                }
                self.reconnect()
                return self.mesage
            if "WHISPER" in resp:
                self.take_privat_mesage(self.tags["mesage"])
            else:
                self.take_mesage(self.tags["mesage"])
                self.makepersone()
            print(
                f" Channel: {self.mesage['channel']} \n Username: {self.mesage['username']} \n Message: {self.mesage['message']} \n Type: {self.mesage['mesage_type']}"
            )
        else:
            self.mesage = {
                "username": "",
                "channel": "",
                "message": "",
                "mesage_type": "",
            }
            return self.mesage

    """odstranění tagu @SoboliUchoBot ze zprávy"""

    def remove_tag(self):
        if "@SoboliUchoBot" in self.mesage["message"]:
            self.mesage["message"] = str(self.mesage["message"]).replace(
                "@SoboliUchoBot", ""
            )
        if "@soboliuchobot" in self.mesage["message"]:
            self.mesage["message"] = str(self.mesage["message"]).replace(
                "@soboliuchobot", ""
            )

    """
    odeslání zprávy do kanálu, pokud zpráva odpovídá uživateli obsahuje @ tak oznaží posledního pisatele, 
    * Pokud uživatel není vysílatelem nebo moderátorem kanálu, robot může odeslat maximálně 20 zpráv za 30 sekund.  
    * Pokud je uživatel vysílatelem nebo moderátorem kanálu, bot může odeslat maximálně 100 zpráv za 30 sekund.
    """

    def send_mesag(self, message, chanel=""):
        chanel = self.channel
        if "@" in message and not "/@" in message:
            message = message.replace("@", "@" + self.mesage["username"] + " ")
            message = message.replace("  ", " ")
        if "/@" in message:
            message = message.replace("/@", "@")
        print(self.sock.send(f"PRIVMSG #{chanel} :{message} \n".encode("utf-8")))
        # print(message)
        time.sleep(1.5)
        print("send")

    """odešle zprávu pomoci WHISPER, můžete šeptat maximálně 40 unikátním příjemcům za den"""

    def send_wisp_mesag(self, message, user=None):
        # Můžete šeptat maximálně 40 unikátním příjemcům za den.
        url = "https://api.twitch.tv/helix/whispers"
        if user == None and "user-id" in self.tags:
            user_id = self.tags["user-id"]
        elif user != None:
            user_id = self.login.get_user_id(user)
        else:
            user_id = self.login.get_user_id(self.mesage["username"])
        params = {"from_user_id": self.id, "to_user_id": user_id}
        login = {
            "Client-Id": self.login.client_id,
            "Authorization": f"Bearer {self.login.access_token}",
        }
        request = requests.post(
            url, params=params, headers=login, data={"message": message}
        )
        if request.status_code == 204:
            print("sent whisper")
        else:
            print(request.text)
        
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

    """bot se rozloučí a odpojí se od severu"""

    def vypnout(self, znak, zprava):
        # self.remove_tag(znak)
        if self.mesage["message"] == None:
            return False
        if str(self.mesage["message"]).startswith(znak):
            konec = "/disconnect"
            self.send_mesag(zprava, self.channel)
            self.send_mesag(konec, self.channel)
            return True
        return False

    """vrátí poslední přijatou zprávu"""

    def zprava(self):
        return self.mesage

    """odebere tagy ze zprávy"""

    def take_tags(self, resp):
        tags = []
        tags_dic = {}
        resp = resp[1:]
        while True:
            location = resp.find(";")
            tag = resp[0:location]
            resp = resp[location + 1 :]
            tags.append(tag)
            # print(resp)
            if (
                resp.find(";") == -1
                or ("PRIVMSG" in resp and resp.find(";") > resp.find("PRIVMSG"))
                or ("WHISPER" in resp and resp.find(";") > resp.find("WHISPER"))
            ):
                location = resp.find(":")
                tag = resp[0:location]
                resp = resp[location:]
                key, value = tag.split("=")
                tags_dic[key] = value
                tags_dic["mesage"] = resp
                break
        for tag in tags:
            location = tag.find("=")
            key = tag[:location]
            value = tag[location + 1 :]
            tags_dic[key] = value

        self.tags = tags_dic
        return tags_dic

    """
    rozloží zprávu z chatu na     
    Username
    Channel  
    Message
    """

    def take_mesage(self, mesage):
        mesages = {}
        mesage = mesage[1:]
        location = mesage.find("!")
        user = mesage[0:location]
        mesages["username"] = user
        location = mesage.find("#")
        location2 = mesage.find(":")
        chanell = mesage[location + 1 : location2]
        mesages["channel"] = chanell
        mesage = mesage[location2 + 1 : -2]
        mesages["message"] = mesage
        mesages["mesage_type"] = "PRIVMSG"
        self.mesage = mesages
        # print(self.mesage)
        return mesages

    """
    rozloží zprávu z WHISPER na     
    Username
    Channel  
    Message
    """

    def take_privat_mesage(self, mesage):
        mesages = {}
        mesage = mesage[1:]
        location = mesage.find("!")
        user = mesage[0:location]
        mesages["username"] = user
        location = mesage.find("WHISPER")
        location2 = mesage.find(":")
        chanell = mesage[location + 8 : location2]
        mesages["channel"] = chanell
        mesage = mesage[location2 + 1 : -2]
        mesages["message"] = mesage
        mesages["mesage_type"] = "WHISPER"
        self.mesage = mesages
        # print(self.mesage)

        return mesages

    def makepersone(self):
        for i in range(len(self.lide)):
            if self.lide[i].nickname == self.mesage["username"]:
                return

        newpersone = clovek(self.mesage["username"])
        self.lide.append(newpersone)

    def savemesage(self):
        for i in range(len(self.lide)):
            if self.lide[i].nickname == self.mesage["username"]:
                self.lide[i].save_mesage(self.mesage["message"])


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
