import re
import threading
# from bot9 import bot
# from bot9_rule import *

# mesage
# Username: self.mesage["username"]
# Channel self.mesage[channel]
# Message: self.mesage["message"]
# mesage_type: self.mesage[mesage_type]

class Zprava(threading.Thread):
    def __init__(self, bot, message) -> None:
        super().__init__()
        self.tags = {}
        self.message = message
        self.bot = bot
        self.rules = bot.rules.get_mesage_rules()
        self.start()
    
    def run(self):
        self.tags = self.take_tags()
        if "WHISPER" in self.message:
            self.message = self.take_privat_mesage(self.tags["mesage"])
        else:
            self.message = self.take_mesage(self.tags["mesage"])
        self.check_rules()
        print (self)
    
    def __str__(self) -> str:
        tags = ", ".join([f"{key}: {value}" for key, value in self.tags.items()])
        txt = f"""{tags}\n
        Channel: {self.mesage['channel']}\n
        Username: {self.mesage['username']}\n 
        Message: {self.mesage['message']}\n 
        Type: {self.mesage['mesage_type']}"""
        return txt
    
    def take_tags(self):
        """odebere tagy ze zprávy"""
        tags = []
        tags_dic = {}
        resp:str = self.message[1:]
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

    def take_mesage(self, mesage):
        """
        rozloží zprávu z chatu na
        Username
        Channel
        Message
        """
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

    def take_privat_mesage(self, mesage):
        """
        rozloží zprávu z WHISPER na
        Username
        Channel
        Message
        """
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
    
    def check_rules(self):
        for rule in self.rules:
            # rule:Rule
            # print (rule, "rule")
            if rule.can_be_send_text(self.message, self.tags):
                self.message_send(rule)
                rule.rule_was_use()
                locals()[rule.use_function()]

                if rule.is_unique():
                    break

    def message_send(self, rule):

        message = rule.message_to_send()
        if isinstance(message, list):
            for i in range(len(message)):
                message[i] = self.edit_message(message)
        else:
            message = self.edit_message(message)
        if self.message["message"]=="=":
            message = self.do_math()
        if rule.type_of_message() == "WHISPER":
            self.bot.send_whisper(message, self.mesage["username"], self.tags["user-id"])
        else:
            self.bot.send_message(message)
    
    def edit_message(self, message:str):
        if "@" in message and not "/@" in message:
            message = message.replace("@", "@" + self.mesage["username"] + " ")
            message = message.replace("  ", " ")
        if "/@" in message:
            message = message.replace("/@", "@")
        return message
    
    def do_math(self):
        self.mesage["message"] = self.mesage["message"].replace(" ", "")
        mesage = self.mesage["message"]
        mesage = mesage.replace("=", "")
        self.mesage_edit()
        if "math.comb" in self.mesage["message"]:
            index_start = self.mesage["message"].find("comb")
            index_end = self.mesage["message"].find(")", index_start)
            if index_start != -1 and index_end != -1:
                substring = self.mesage["message"][index_start : index_end + 1]
                modified_substring = substring.replace(".", ",")
                self.mesage["message"] = (
                    self.mesage["message"][:index_start]
                    + modified_substring
                    + self.mesage["message"][index_end + 1 :]
                )
        print(self.mesage["message"])
        elements = re.findall(
            r"\d+|\+|\-|\*\*|\/|\(|\)|\*|\,|\.|math\.sqrt|math\.log10|math\.factorial|math\.comb|math\.pi|math\.tau|math\.e|math\.sin|math\.cos|math\.tan|math\.radians|math\.degrees|math\.asin|math\.acos|math\.atan",
            self.mesage["message"],
        )
        try:
            result = eval("".join(elements))
            result = f"{result:,}".replace(",", " ")
            result = "@" + self.mesage["username"] + " " + mesage + " = " + str(result)
        except SyntaxError:
            try:
                result = self.repairMath(elements,mesage)
            except SyntaxError:
                result = "@" + self.mesage["username"] + " wrong format"
        except TypeError:
            try:
                result = self.repairMath(elements,mesage)
            except TypeError:
                result = "@" + self.mesage["username"] + " wrong format"
        except ZeroDivisionError:
            result = "@"+ self.mesage["username"] + " division by zero is not defined in ℝ"
        except IndexError:
            result = "@"+ self.mesage["username"] + " wrong format"
        except OverflowError as e:
            result = "#" + str(e)
        except ValueError:
            result = "# answer is too long"
        # else:
        #     result = "@"+ self.mesage["username"] + " wrong format"
        if (len(result) > 500):
            result = "# answer is too long"
        # result = random.randint(0, 1000000)
        return result

    def mesage_edit(self):
        # if "horty" in self.mesage["message"].lower():
        #     self.mesage["message"] = "=333"
        self.mesage["message"] = self.mesage["message"].replace("^", "**")
        self.mesage["message"] = self.mesage["message"].replace("Horty", "333")
        self.mesage["message"] = self.mesage["message"].replace("horty", "333")
        self.mesage["message"] = self.mesage["message"].replace("HORTY", "333")
        self.mesage["message"] = self.mesage["message"].replace("sqrt", "math.sqrt")
        self.mesage["message"] = self.mesage["message"].replace("comb", "math.comb")
        self.mesage["message"] = self.mesage["message"].replace("fact", "math.factorial")
        self.mesage["message"] = self.mesage["message"].replace("log", "math.log10")
        self.mesage["message"] = self.mesage["message"].replace("gamma", "math.gamma")
        self.mesage["message"] = self.mesage["message"].replace("pi", "math.pi")
        self.mesage["message"] = self.mesage["message"].replace("pí", "math.pi")
        self.mesage["message"] = self.mesage["message"].replace("π", "math.pi")
        self.mesage["message"] = self.mesage["message"].replace("tau", "math.tau")
        self.mesage["message"] = self.mesage["message"].replace("τ", "math.tau")
        self.mesage["message"] = self.mesage["message"].replace("e", "math.e")
        if "°" in self.mesage["message"]:
            self.mesage["message"] = self.mesage["message"].replace("sin(", "math.sin(math.radians(")
            self.mesage["message"] = self.mesage["message"].replace("cos(", "math.cos(math.radians(")
            self.mesage["message"] = self.mesage["message"].replace("tan(", "math.tan(math.radians(")
            self.mesage["message"] = self.mesage["message"].replace("sin-1(", "math.degrees(math.asin(")
            self.mesage["message"] = self.mesage["message"].replace("cos-1(", "math.degrees(math.acos(")
            self.mesage["message"] = self.mesage["message"].replace("tan-1(", "math.degrees(math.atan(")
        else:
            self.mesage["message"] = self.mesage["message"].replace("sin(", "math.sin(")
            self.mesage["message"] = self.mesage["message"].replace("cos(", "math.cos(")
            self.mesage["message"] = self.mesage["message"].replace("tan(", "math.tan(")
            self.mesage["message"] = self.mesage["message"].replace("sin-1(", "math.asin(")
            self.mesage["message"] = self.mesage["message"].replace("cos-1(", "math.acos(")
            self.mesage["message"] = self.mesage["message"].replace("tan-1(", "math.atan(")
        self.mesage["message"] = self.mesage["message"].replace("^", "**")
        self.mesage["message"] = self.mesage["message"].replace("x", "*")
        self.mesage["message"] = self.mesage["message"].replace("÷", "/")
        self.mesage["message"] = self.mesage["message"].replace(",", ".")
        self.mesage["message"] = self.mesage["message"].replace(";", ",")

    def repairMath(self, elements, mesage):
        try:
            zavork = elements.count("(")
            while zavork > elements.count(")"):
                elements.append(")")
                mesage = mesage + ")"
            e = 0
            while True:
                if e + 1 != len(elements) and e - 1 != -1:
                    if elements[e - 1].isdigit() and elements[e] == "(":
                        elements.insert(e, "*")
                if elements[e].isdigit() and elements[e - 1] == ")" and e - 1 != -1:
                    elements.insert(e, "*")
                if e == len(elements) - 1:
                    break
                e += 1
            result = eval("".join(elements))
            result = f"{result:,}".replace(",", " ")
            result = "@" + self.mesage["username"] + " " + mesage + " = " + str(result)
        except SyntaxError:
            result = "@" + self.mesage["username"] + " wrong format"
        
        return result

    def resul_format(self, result):
        if (len(result) > 500):
            result = "# answer is too long"
        else:
            result = f"{result:,}".replace(",", " ")
        return (result)
    
class Clovek:
    def __init__(self, username, tags) -> None:
        self.nick = username
        self.userId = tags["user-id"]
        self.tags = tags
    