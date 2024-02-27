import json
from bs4 import BeautifulSoup
import requests
import time


class rule:
    #{"in_text":0/1/2 - is / start / in,"rule":["",""],"send_all":true/false,"messages":["",""], "timer" = "", "message_type": "WHISPER" / "PRIVMSG", "mod": true / false, "autosend": true / false, "funnction": true / false, "number_of_use": -1-x},

    def __init__(self, asociative_array) -> None:
        self.rules = asociative_array
        self.LastUse = 0
        self.lastmessage = None
        self.number_of_use = 0

    def rule_can_be_send(self, message, tags=None):
        sent = False
        if not self.timer():
            return False
        if self.is_in_rule("number_of_use") and (self.rules["number_of_use"]>"number_of_use" and self.rules["number_of_use"] != -1):
            return False
        if self.is_in_rule("autosend", True):
            return True
        if self.is_in_rule("in_text", 0):
            sent = self.message_is(message)
        if self.is_in_rule("in_text", 1):
            sent = self.message_start(message)
        if self.is_in_rule("in_text", 2):
            sent = self.message_contain(message)
        if self.is_in_rule("mod", True) and tags != None:
            sent = self.is_mod(tags)
        return sent

    def timer(self):
        if (time.time() + int(self.rules["timer"])) > self.LastUse:
            return True
        return False

    def is_in_rule(self, variable, value=None):
        if variable in self.rules:
            if value != None and self.rules[variable] == value:
                return True
            if value == None:
                return True
        return False

    def message_is(self, message):
        for rule in self.rules["rule"]:
            if str(message).startswith(rule) and len(message) == len(rule):
                return True
        return False

    def message_start(self, message):
        for rule in self.rules["rule"]:
            if str(message).startswith(rule):
                return True
        return False

    def message_contain(self, message):
        for rule in self.rules["rule"]:
            if rule in str(message):
                return True
        return False

    def is_mod(self, tags):
        return False

    def message_to_send(self):
        if self.is_in_rule("send_all", True):
            return self.rules["messages"]
        message = []

        return message
    def rule_was_use(self):
        self.lastmessage = time.time()
        self.number_of_use += 1




class vedator:
    def __init__(self, url, run_chat_comands) -> None:
        self.url = url
        self.run_chat_comands = run_chat_comands
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")

    def read_page(self):
        content = self.soup.find("div", {"id": "primary"})
        podnadpis = content.find("div", {"class": "entry-content"})
        podnadpis = podnadpis.find_all("p")
        self.make_tvrule(podnadpis[0].text)
        rule = 1
        for podnadpiss in podnadpis:
            if podnadpiss.find("a") != None:
                self.make_tvxrule(rule, podnadpiss)
                rule += 1
            if rule == 7:
                break

    def make_tvrule(self, text):
        pravidlo = [0, ["!tv", "!tvv"], 0, [text + " " + self.url], 0]
        self.run_chat_comands.pravidla.append(pravidlo)
        # print(f"{self.run_chat_comands.pravidla}\n")

    def make_tvxrule(self, poradi, text):
        poradi = str(poradi)
        textodkkazu = text.find("a").text
        odkaz = text.find("a")["href"]
        textprazdny = "".join(
            [str(content) for content in text.contents if not content.name == "a"]
        )
        textprazdny = textprazdny.replace("<em>", "")
        textprazdny = textprazdny.replace("</em>", "")
        textprazdny = textprazdny.replace("<br/>", "")
        input_text = textodkkazu + " " + textprazdny
        while len(input_text) > 500:
            input_text = input_text.split(".")
            input_text = ".".join(input_text[:-1])
        pravidlo = rule(
            {
                "in_text": 0,
                "rule": ["!tv" + poradi, "!tvv" + poradi],
                "send_all": True,
                "messages": [textodkkazu + " " + odkaz, input_text + "."],
            }
        )
        self.run_chat_comands.pravidla.append(pravidlo)
        print(pravidlo)
