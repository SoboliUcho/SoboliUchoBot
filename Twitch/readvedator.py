from bs4 import BeautifulSoup
import requests


class vedator:
    def __init__(self, url, run_chat_comands, number_of_rule ) -> None:
        self.url = url
        self.number_of_rule = 1 + number_of_rule
        self.run_chat_comands = run_chat_comands
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        
    def read_page(self):
        content = self.soup.find("div", {"id":"primary"})
        podnadpis = content.find("div", {"class":"entry-content"})
        podnadpis = podnadpis.find_all("p")
        self.make_tvrule(podnadpis[0].text)
        rule = 1
        for podnadpiss in podnadpis:
            if podnadpiss.find("a")!=None:
                self.make_tvxrule(rule, podnadpiss)
                rule +=1 
            if rule == self.number_of_rule:
            # if rule ==9:
                break


    def make_tvrule(self,text):
        pravidlo = [0,["!tv","!tvv"],0,[text + " " + self.url],0]
        self.run_chat_comands.pravidla.append(pravidlo)
        # print(f"{self.run_chat_comands.pravidla}\n")
        
    def make_tvxrule(self, poradi, text):
        poradi = str(poradi)
        textodkkazu  = text.find("a").text
        textodkkazu = textodkkazu.replace("\n", " ")
        odkaz = text.find("a")['href']
        textprazdny = ''.join([str(content) for content in text.contents if not content.name == 'a'])
        textprazdny = textprazdny.replace("<em>", "")
        textprazdny = textprazdny.replace("</em>", "")
        textprazdny = textprazdny.replace("<br/>", "")
        textprazdny = textprazdny.replace("\n", " ")
        input_text = textodkkazu + " "+ textprazdny
        while len(input_text)>500:
            input_text = input_text.split('.')
            input_text = '.'.join(input_text[:-1])
        pravidlo = [0,["!tv"+poradi,"!tvv"+poradi],0,[textodkkazu + " " +odkaz, input_text+"."],0]
        self.run_chat_comands.pravidla.append(pravidlo)
        print (pravidlo)

