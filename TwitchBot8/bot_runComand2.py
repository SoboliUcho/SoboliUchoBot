import random
import re

# mod only mesage TODO
# [["podminky"], "příkaz / v textu / příkaz a text", ["zpravy1", "zprava2" ], "polslat vše / náhodně", "zpráva/odpoveď", "user/mods", "zprava/akce", timer, repetation, autosend]

class run_chat_comands:
    def __init__(self, bot, pravidla) -> None:
        self.bot = bot
        self.pravidlaSoubor = pravidla
        self.pravidla = pravidla.return_Rules()

    def run_chat_comands(self):
        for i in range (len(self.pravidla)):
            self.analize_zprava(self.pravidla[i])
            
    def analize_zprava(self, pravidlo):
        if pravidlo[0]==0:
            self.mesage_start_analize(pravidlo)
        if pravidlo[0]==1:
            self.mesage_contain_analize(pravidlo)

    def reload(self):
        self.pravidla = self.pravidlaSoubor.return_Rules()

    #  vstup pole a pole opravit TODO - DONE 
    def mesage_start_analize(self, rule):
        if self.bot.mesage["message"] == None:
            return False
        for pravidlo in rule[1] :
            if rule[2] == 0 and self.mesage_start(pravidlo):
                for zprava in rule[3]:
                    self.bot.send_mesag(zprava)
                return True
            if rule[2] == 1 and self.mesage_start(pravidlo):
                self.bot.send_mesag(random.choice(rule[3]))
                return True
        return False

    def mesage_start (self, znak, zprava=""):
        if self.bot.mesage["message"] == None:
            return False
        
        if str(self.bot.mesage["message"]).startswith(znak) and len(self.bot.mesage["message"]) == len(znak):
            if zprava == "":
                return True
            self.bot.send_mesag(zprava) 
            # self.bot.send_wisp_mesag(zprava)           
            return True
        return False

    # dodělat pravidlo TODO
    def mesage_contain_analize(self, rule):
        if self.bot.mesage["message"] == None:
            return False
        for pravidlo in rule[1] :
            if rule[2] == 0 and self.mesage_contain(pravidlo):
                for zprava in rule[3]:
                    self.bot.send_mesag(zprava)
                return True
            if rule[2] == 1 and self.mesage_contain(pravidlo):
                self.bot.send_mesag(random.choice(rule[3]))
                return True
        return False
    
    def mesage_contain(self, znak, zprava=""):
        if self.bot.mesage["message"] == None:
            return False

        if znak in str(self.bot.mesage["message"]):
            if zprava == "":
                return True
            self.bot.send_mesag(zprava)
            return True   
        return False
    
    def add_rules(self, pravidla):
        for rule in pravidla:
            self.pravidla.append(rule)

    def mathe(self):
        if self.mesage["message"][0] == "=":
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
            self.send_mesag(result, self.channel)
            # self.mesage["message"]= ["","",""]
            return True
        return False

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
