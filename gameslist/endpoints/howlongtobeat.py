# -*- coding: utf-8 -*-
import urllib2
import sys
from bs4 import BeautifulSoup, Tag, NavigableString
import requests
import re
import traceback
import logging

logger = logging.getLogger('MYAPP')

class HowLongToBeat():
    def __init__(self,game):
        headers={'User-Agent': 'Mozilla/5.0'}
        form_data = {"queryString": game,"t": "games",
                    "sorthead": "popular", "sortd": "Normal Order","length_type": "main"}
        url = "https://howlongtobeat.com/search_results.php?page=1"
        #print url
        #print form_data
        request = requests.post(url,data=form_data)
        self.game = game
        self.raw_data = BeautifulSoup(request.text,"html.parser")
        #print self.raw_data
        self.raw_time = game
        self.fulltime = -1
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
                                for l in self.raw_time[1].contents:
                                    if isinstance(l,Tag):
                                        if re.search("--",l.text):
                                            self.fulltime = -1.0
                                            self.units = "Hours"
                                            self.found = True
                                    #else, probably a bs4.element.Tag
                                break
                    if self.found:
                        break
                else:
                    logger.info(u"NOT FOUND: {0}.".format(game))
                    logger.info(u"Did you mean: {0}?".format(link.find("a")["title"]))
                    pass
                    #raise Exception
            #self.found = True
            if self.found:
                pass
            else:
                u"{0} not found.".format(game)
        except: 
            logger.error(traceback.print_exc())
            self.id = 0
            logger.error(sys.exc_info()[0])
            logger.error(sys.exc_info()[1])
            raise Exception
    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.found:
            return u"{0} - {1} {2}".format(self.game,self.fulltime,self.units)
        else:
            return unicode(self.game) + u" - Not Found"

class ExampleHowLongToBeat():
    def __init__(self,game):
        headers={'User-Agent': 'Mozilla/5.0'}
        form_data = {"queryString": game,"t": "games",
                    "sorthead": "popular", "sortd": "Normal Order","length_type": "main"}
        url = "https://howlongtobeat.com/search_main.php?page=1"
        #print url
        #request = requests.post(url,data=form_data)
        self.game = game

        self.raw_data = BeautifulSoup(open("examplehtlb.html"),"html.parser")
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
            logger.error(sys.exc_info()[0])
            logger.error(sys.exc_info()[1])
            logger.error(sys.exc_info()[2])
            self.id = 0
            self.fulltime = -1
            self.found = False
            raise Exception
    def __str__(self):
        if self.found:
            return self.game + " - " + str(self.fulltime) + " Hours"
        else:
            return self.game + " - Not Found"

# #def clean_titles():
# with open("titles.txt","r") as f:
#     #with open("systems.txt","r") as g:
#         with open("output.txt","w+") as h:
#             title = True
#             while title:
#                 title = f.readline().strip("\n")
#                 #system = g.readline()
#                 hltb = HowLongToBeat(title)
#                 if hltb.found:
#                     print hltb
#                     h.write(str(hltb))
#                     h.write("\n")
#                 else:
#                     #temp = hltb.raw_data.find("h3",attrs={"class":"head_padding shadow_box back_blue center"}) 
#                     #print (temp if temp else "{0} not found.".format(title))
#                     pass

hltb = HowLongToBeat("Sunset Overdrive")
print ExampleHowLongToBeat("Sunset Overdrive")
print hltb

#<li class='global_padding back_white shadow_box'>No results for <strong>a mini falafa</strong> in <u>games</u>.</li>


#search_list_details
#temp = requests.get("https://howlongtobeat.com/game.php?id=21278",headers={'User-Agent': 'Mozilla/5.0'})
#temp = BeautifulSoup(temp.text,"html.parser")
#print temp

