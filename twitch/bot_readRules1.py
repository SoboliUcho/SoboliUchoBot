import re
import json
from pathlib import Path

class zpravy:
    def __init__(self, soubor) -> None:
        self.soubor = soubor
        self.cesta = Path(__file__).with_name(soubor)
        self.zpravy = open(self.cesta,"a+",encoding="utf-8")
        self.zpravy.seek(0)
        self.Lines = None

    def return_Rules (self):
        self.open_File()
        self.lines_To_Rules()
        return self.Lines

    def line_to_rule(self, line):
        line = line.rstrip("\n")
        # print (line)
        rule = json.loads(line)
        # print(rule[0])
        return rule
    
    def open_File(self):
        self.zpravy.seek(0)
        self.Lines = self.zpravy.readlines()

    def lines_To_Rules(self):
        for i in range (len(self.Lines)):
            pravidlo = self.line_to_rule(self.Lines[i])
            self.Lines[i] = pravidlo
            print (self.Lines[i])
    
    def new_Rule (self, podmínka, pravidlo, random, odpoved, opravneni):
        self.zpravy.seek(0,2)
        json_string = json.dumps([podmínka,pravidlo, random ,odpoved,opravneni])
        self.zpravy.write(json_string)