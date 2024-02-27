import json
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import time
import random

class Rule:
    #{"in_text":0/1/2 - is / start / in,"rule":["",""],"send_all":true/false,"messages":["",""], "timer" = "", "message_type": "WHISPER" / "PRIVMSG", "mod": true / false, "autosend": true / false, "funnction": true / false, "number_of_use": -1-x,, "counter":0},

    def __init__(self, asociative_array) -> None:
        self.rules = asociative_array
        self.LastUse = 0
        self.lastmessage = None
        self.number_of_use = 0

    def __str__(self) -> str:
        tags = ", ".join([f"{key}: {value}" for key, value in self.rules.items()])
        return tags
    
    def can_be_send_text(self, message, tags=None):
        sent = False
        # timer 
        if not self.timer():
            # print ("timer")
            return False
        # number of use
        if self.is_in_rule("number_of_use") and (self.rules["number_of_use"]>self.number_of_use and self.rules["number_of_use"] != -1):
            # print("n of use")
            return False
        if self.is_in_rule("in_text", 0):
            # print("in text 0")
            sent = self.message_is(message)
        if self.is_in_rule("in_text", 1):
            # print("in text 1")
            sent = self.message_start(message)
        if self.is_in_rule("in_text", 2):
            # print("in text 2")
            sent = self.message_contain(message)
        if self.is_in_rule("mod", True) and tags != None:
            # print("mod")
            sent = self.is_mod(tags)
        # print("sent", sent)
        return sent

    def timer(self):
        if not "timer" in self.rules:
            return True
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
        if isinstance(message, dict):
            message = message["message"]
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
        if self.is_in_rule("send_all", False):
            return  random.choice(self.rules["messages"])
    
    def rule_was_use(self):
        self.lastmessage = time.time()
        self.number_of_use += 1
    
    def is_unique(self):
        if self.rules["in_text"] == 0:
            return True
        return False
    
    def type_of_message(self):
        if "message_type" in self.rules:
            return self.rules["message_type"]
        return  "PRIVMSG"
    
    def use_function(self):
        print("function was used")
        if "funnction" in self.rules:
            return self.rules["funnction"]
        else:
            return False

class Rules:
    def __init__(self, file_path) -> None:
        self.cesta = Path(__file__).with_name(file_path)
        self.mesage_rules = []
        self.auto_rules = []
        self.addid_rules = []
        self.load_rules()
    
    def __str__(self) -> str:
        text = ""
        for rule in self.mesage_rules:
            text += str(rule) + "\n"
        return text

    def get_mesage_rules(self):
        # self.load_rules()
        return self.mesage_rules
    def get_get_mesage_rules_reload(self):
        self.load_rules()
        return self.mesage_rules
    # def get
    def get_auto_rules(self):
        # self.load_rules()
        return self.auto_rules
    
    def load_rules(self):
        with open(self.cesta,"r",encoding="utf-8") as file:
            lines = json.load(file)
            for line in lines:
                pravidlo = Rule(line)
                print (pravidlo)
                if "autosend" in line and line["autosend"]:
                    self.auto_rules.append(pravidlo)
                self.mesage_rules.append(pravidlo)
        for rule in self.addid_rules:
            self.mesage_rules.append(rule)
            
    def add_mesage_rule(self, arary_of_rules:list):
        for rule in arary_of_rules:
            # print (rule)
            self.mesage_rules.append(rule)
            self.addid_rules.append(rule)

class vedator:
    def __init__(self, url) -> None:
        self.url = url
        # self.run_chat_comands = run_chat_comands
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.rules = []

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
        pravidlo = Rule ({"in_text":0, "rule":["!tv", "!tvv"],"send_all": True , "messages": [text + " " + self.url]})
        self.rules.append(pravidlo)
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
        pravidlo = Rule(
            {
                "in_text": 0,
                "rule": ["!tv" + poradi, "!tvv" + poradi],
                "send_all": True,
                "messages": [textodkkazu + " " + odkaz, input_text + "."],
            }
        )
        self.rules.append(pravidlo)
        print(pravidlo)
