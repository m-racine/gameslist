# -*- coding: utf-8 -*-
import urllib2
import sys
from bs4 import BeautifulSoup
import requests
import re


class HowLongToBeat():
    def __init__(self,game):
        headers={'User-Agent': 'Mozilla/5.0'}
        form_data = {"queryString": game,"t": "games",
                    "sorthead": "popular", "sortd": "Normal Order","length_type": "main"}
        url = "https://howlongtobeat.com/search_main.php?page=1"
        #print url
        request = requests.post(url,data=form_data)
        self.game = game
        self.raw_data = BeautifulSoup(request.text,"html.parser")
        try:
            self.id = self.raw_data.find("a",attrs={"title":game})['href'][12:]
            links = self.raw_data.find_all("div",attrs={"class":"search_list_details"})
            for link in links:
                inner_tag = link.find("a",attrs={"title":self.game})
                if inner_tag is not None:
                    #print link.prettify()
                    raw_time = link.find("div",attrs={"class":"search_list_tidbit center time_100"})
                    time_text = raw_time.text.replace(u"\xbd",'.5')
                    self.fulltime = float(re.search("([\d.\d]*)",time_text).group(1))
            self.found = True
        except: 
            self.id = 0
            self.fulltime = 0.0
            self.found = False
    def __str__(self):
        if self.found:
            return self.game + " - " + str(self.fulltime) + " Hours"
        else:
            return self.game + " - Not Found"

class ExampleHowLongToBeat():
    def __init__(self,game):
        headers={'User-Agent': 'Mozilla/5.0'}
        form_data = {"queryString": game,"t": "games",
                    "sorthead": "popular", "sortd": "Normal Order","length_type": "main"}
        url = "https://howlongtobeat.com/search_main.php?page=1"
        #print url
        #request = requests.post(url,data=form_data)
        self.game = game

        self.raw_data = BeautifulSoup(open("../../examplehtlb.html"),"html.parser")
        try:
            self.id = self.raw_data.find("a",attrs={"title":game})['href'][12:]
            links = self.raw_data.find_all("div",attrs={"class":"search_list_details"})
            for link in links:
                inner_tag = link.find("a",attrs={"title":self.game})
                if inner_tag is not None:
                    #print link.prettify()
                    raw_time = link.find("div",attrs={"class":"search_list_tidbit center time_100"})
                    time_text = raw_time.text.replace(u"\xbd",'.5')
                    self.fulltime = float(re.search("([\d.\d]*)",time_text).group(1))
            self.found = True
        except: 
            self.id = 0
            self.fulltime = 0.0
            self.found = False
    def __str__(self):
        if self.found:
            return self.game + " - " + str(self.fulltime) + " Hours"
        else:
            return self.game + " - Not Found"


hlto = ExampleHowLongToBeat("Sunset Overdrive")
print hlto
hlto = HowLongToBeat("Super Mario Bros.")
print hlto
hlto = HowLongToBeat("Halo Wars")
print hlto
hlto = HowLongToBeat("The Miskatonic")
print hlto

#search_list_details
#temp = requests.get("https://howlongtobeat.com/game.php?id=21278",headers={'User-Agent': 'Mozilla/5.0'})
#temp = BeautifulSoup(temp.text,"html.parser")
#print temp