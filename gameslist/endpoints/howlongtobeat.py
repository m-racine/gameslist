# -*- coding: utf-8 -*-
import urllib2
import sys
from bs4 import BeautifulSoup, Tag
import requests
import re
import traceback


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
        self.raw_time = game
        self.fulltime = 0.0
        self.found = False
        self.units = "Hours"
        try:
            
            #self.id = self.raw_data.find("a",attrs={"title":game})['href'][12:]
            links = self.raw_data.find_all("div",attrs={"class":"search_list_details"})
            x = 0
            for link in links:
                x += 1
                #print x
                inner_tag = link.find("a",attrs={"title":self.game})
                if inner_tag is not None:
                    self.found = True
                    print game
                    title = self.raw_data.a
                    self.id = title['href'][12:]
                    self.raw_time = link.find("div",attrs={"class":"search_list_details_block"}).contents
                    for element in self.raw_time:
                        if isinstance(element, Tag):
                            time_text = element.text.replace(u"\xbd",'.5')
                            time_search = re.search("\d+\.?\d* \w*",time_text)
                            if time_search:
                                self.fulltime = float(re.search("\d+\.?\d*",time_text).group(0))
                                self.units = re.search("(\d+\.?\d*) (\w*)",time_text).group(2)
                                
                                break
                            else:
                                #print self.raw_time
                                #print time_text
                                pass
                    if self.found:
                        break
                else:
                    print "NOT FOUND: {0}.".format(game)
                    print u"Did you mean: {0}?".format(link.find("a")["title"])
                    pass
                    #raise Exception
            #self.found = True
            if self.found:
                pass
            else:
                "{0} not found.".format(game)
        except: 
            print traceback.print_exc()
            self.id = 0
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            raise Exception
    def __str__(self):
        if self.found:
            return self.game + " - " + str(self.fulltime) + " " + self.units
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
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            print sys.exc_info()[2]
            self.id = 0
            self.fulltime = 0.0
            self.found = False
            raise Exception
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

#def clean_titles():
with open("titles.txt","r") as f:
    with open("systems.txt","r") as g:
        with open("output.txt","w") as h:
            title = True
            while title:
                title = f.readline().strip("\n")
                system = g.readline()
                hltb = HowLongToBeat(title)
                if hltb.fulltime > 0.0:
                    h.write(hltb.__str__())
                    h.write("\n")
                else:
                    #temp = hltb.raw_data.find("h3",attrs={"class":"head_padding shadow_box back_blue center"}) 
                    #print (temp if temp else "{0} not found.".format(title))
                    pass


#<li class='global_padding back_white shadow_box'>No results for <strong>a mini falafa</strong> in <u>games</u>.</li>


#search_list_details
#temp = requests.get("https://howlongtobeat.com/game.php?id=21278",headers={'User-Agent': 'Mozilla/5.0'})
#temp = BeautifulSoup(temp.text,"html.parser")
#print temp


#Cth Saves The World 
#Typing of the Dead
#Lumanaries of The
#Japanese To Survive
