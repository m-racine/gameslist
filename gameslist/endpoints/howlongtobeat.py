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
        #print form_data
        request = requests.post(url,data=form_data)
        self.game = game
        self.raw_data = BeautifulSoup(request.text,"html.parser")
        #print self.raw_data
        self.raw_time = "help"
        try:
            #print self.raw_data
            print self.raw_data["a"].title
            self.id = self.raw_data.findall("a")
            print self.id
            #self.id = self.raw_data.find("a",attrs={"title":game})['href']
            print "2"
            self.id = self.raw_data.find("a",attrs={"title":game})['href'][12:]
            print "huuuh"
            links = self.raw_data.find_all("div",attrs={"class":"search_list_details"})
            for link in links:
                inner_tag = link.find("a",attrs={"title":self.game})
                #print inner_tag
                print "whataa"
                if inner_tag is not None:
                    #print link.prettify()
                   # self.raw_time = link.findall("div",attrs={"class":"^search_list_tidbit center"})
                    print "temp"
                    self.raw_time = link.find("div",attrs={"class":"search_list_details_block"}).contents
                    print "what"
                    print self.raw_time
                    time_text = self.raw_time[1].text.replace(u"\xbd",'.5')
                    print re.search("([\d.\d]*)",time_text).group(1)
                    self.fulltime = float(re.search("([\d.\d]*)",time_text).group(1))
            self.found = True
        except: 
            self.id = 0
            self.fulltime = 0.0
            self.found = False
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            print "test"
            raise Exception
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


# hlto = ExampleHowLongToBeat("Sunset Overdrive")
# print hlto
# hlto = HowLongToBeat("Human Resource Machine")
# print hlto
# hlto = HowLongToBeat("7 Billion Humans")
# print hlto
# hlto = HowLongToBeat("Orwell")
# print hlto


with open("titles.txt","r") as f:
    with open("systems.txt","r") as g:
        with open("output.txt","w") as h:
            while(True):
                title = f.readline().strip("\n")
                system = g.readline()
                hltb = HowLongToBeat(title)
                if hltb.fulltime > 0.0:
                    print hltb
                else:
                    temp = hltb.raw_data.find("h3",attrs={"class":"head_padding shadow_box back_blue center"}) 
                    print (temp if temp else hltb.raw_time)


#search_list_details
#temp = requests.get("https://howlongtobeat.com/game.php?id=21278",headers={'User-Agent': 'Mozilla/5.0'})
#temp = BeautifulSoup(temp.text,"html.parser")
#print temp