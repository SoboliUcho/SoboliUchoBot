
from login import login
from bot8 import *
from readvedator import *

from bot_readRules1 import *
from bot_runComand2 import *

import multiprocessing

# channel = "333_stribrnych_strikacek"
# channel = "vedator_cz"
# channel = "bratrhood"
# channel = "akrej"
# channel = "selick1"
# channel = "akcelcz"
# channel = "patrikturi"
# channel = "conducteir77"
# channel = "gastronebe"
# channel = "fluffcz"
# channel = "mrgawkygamer"
# channel = "tartak_daario"
# channel = "miselinacz"
# channel = "whikarol"
# channel = "haiset"
channel = "soboliucho"

tokeny = login()
nickname = 'soboliuchobot'
join_mesage = "Ahoj HeyGuys já jsem hodný robot a byl bych rád kdybyste mi zadali nějaký složitý matematický příklad ve formátu: =1+2"
join_mesage = "Ahoj já jsem hodný robot a právě jsem se k vám připojil HeyGuys"
join_mesage = ""
out_mesage = "Za chvíli jsem zpátky HeyGuys"
out_mesage = "Tak zase někdy HeyGuys"
# out_mesage = ""
shutdown_comand = "@SoboliUchoBot vypnout"
pravidla = "vedator.txt"
# pravidla = "zpravyIlu.txt"
pravidla = "zprav_pokus.txt"
# pravidla = "SUcomands.txt"
tyde_url = "https://vedator.org/2024/02/oh-yeah-tyden-ve-vede-5-az-11-unora-2024/"

# tyde_url = input ("Zadej odkaz na Týden ve vědě: ")

botik = bot(channel, tokeny, nickname, join_mesage)
zprava = zpravy(pravidla)
anelize = run_chat_comands(botik, zprava)
vedator_page = vedator(tyde_url, anelize, 6)
vedator_page.read_page()
# print (anelize.pravidla)


botik.connect_to_server()
botik.connect_to_chanel(channel)
# botik.send_mesag("=1+2", channel)
counter = 0

    
while True:
    botik.read_mesage()
    if anelize.mesage_start("!reload"):
        anelize.reload()
        botik.send_mesag("reload", channel)
    # print("ahoj")
    # botik.savemesage()
    # print ("zapsáno")
    # for i in range (20):
    #     pokoj = "!pokoj" + str(i)
    #     botik.send_mesag(pokoj)
    #     botik.send_mesag(pokoj)
    # break 
    # if anelize.mesage_contain("Dotaz") or anelize.mesage_contain("dotaz"):
    #     with open('dotazy.txt', 'a', encoding='utf-8') as file:
    #         file.write('\n')
    #         file.write(botik.mesage["message"])
    #         botik.send_mesag("dotaz byl zazanmenán")
    # if anelize.mesage_contain("mekac"):
    #     counter+=1
    #     botik.send_mesag(f"Mekáč byl zmíněn již: {counter}")

    if botik.vypnout(shutdown_comand,out_mesage):
        break
    anelize.run_chat_comands()
    if botik.mesage["mesage_type"] == "WHISPER":
        botik.send_wisp_mesag(botik.mesage["message"])
    # print (botik.tags)


        


    