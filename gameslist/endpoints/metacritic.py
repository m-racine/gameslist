import urllib2
import sys
from bs4 import BeautifulSoup
import requests
import re
import os
#swapMonth function works better as a dict in python
month_dict = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04",
              "May":"05","Jun":"06","Jul":"07","Aug":"08",
              "Sep":"09","Oct":"10","Nov":"11","Dec":"12"}

#https://www.crummy.com/software/BeautifulSoup/bs4/doc/

def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')

#https://stackoverflow.com/questions/3931541/how-to-check-if-all-of-the-following-items-are-in-a-list
def user_score_class(tag):
    return "class" in tag.attrs and  set(["metascore_w", "user", "large", "game"]).issubset(tag['class'])

def fixSystem(system):
    #faster to do this first
    system = "-".join(system.lower().split(" "))
    if system in ["steam","gog","origin","humble","uplay","twitch","battle.net","itch.io"]:
        return "pc"
    elif system in ["kindle","android"]:
        return "ios"
    #system = "-".join(system.lower().split(" "))
    return system
    #unsure if going to use these base don how systems are stored in the db
#     if (system == "gba"){
#        system = "game-boy-advance";
#     }else if (system == "gbc"){
#        system = "game-boy-color";
#     }else if (system == "n64"){
#        system = "nintendo-64";
#     }else if (system == "vita"){
#        system = "playstation-vita";
#     }

def fixGame(game):
    # to replace \ that's what you need in the re, \\\\
    game = re.sub("[:\/\?'\(;\.\)#&$,\\\\']","",game)
    game = game.replace("<","lt").replace(">","gt")
    return game.replace(" ","-").lower();

def fixDateFormat(unformatted_date):
#   looks like "Jun 12, 2001"
#   should be "2001-06-12"
#   Logger.log(date);
    initial = unformatted_date.split(", ")
    second = initial[0].replace("  "," 0").split(" ")
    return initial[1] + "-" + month_dict[second[0]] + "-" + second[1]



#https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
class MetaCritic():
    def __init__(self,game,system):
        headers={'User-Agent': 'Mozilla/5.0'}
        url = "http://www.metacritic.com/game/"+fixSystem(system)+"/"+ fixGame(game)
        #print url
        request = requests.get(url,headers=headers)
        self.raw_data = BeautifulSoup(request.text,"html.parser")
        self.metacritic = self.raw_data.find("span",attrs={"itemprop":"ratingValue"}).text
        self.userscore = self.raw_data.find(user_score_class).text
        self.publisher = self.raw_data.find('li',attrs={"class":"summary_detail publisher"}).find("span",attrs={'itemprop':'name'}).text.strip()
        #can be a list, may need to refactor
        self.developer = self.raw_data.find("li",attrs={"class":"summary_detail developer"}).find("span",attrs={"class":"data"}).text.strip()
        self.release_date = fixDateFormat(self.raw_data.find("span",attrs={"class":"data","itemprop":"datePublished"}).text)
        self.players  = self.raw_data.find("li",attrs={"class":"summary_detail product_players"}).find("span",attrs={"class":"data"}).text.strip()
        #can be a list
        self.genre = self.raw_data.find("li",attrs={"class":"summary_detail product_genre"}).findall("span",attrs={"class":"data","itemprop":"genre"}).text.strip()

class ExampleMetaCritic():
    def __init__(self,game,system):
        self.raw_data = BeautifulSoup(open(os.path.join(os.getcwd(),"gameslist/endpoints/example.html")),"html.parser")
        self.metacritic = self.raw_data.find("span",attrs={"itemprop":"ratingValue"}).text
        self.userscore = self.raw_data.find(user_score_class).text


meta = ExampleMetaCritic("Deus Ex: Mankind Divided","Steam")
link = meta.raw_data.find("li",attrs={"class":"summary_detail product_genre"})
print link
#links = link.find_all("span",attrs={"class":"data","itemprop":"genre"})
#print links
#.findall("span",attrs={"class":"data","itemprop":"genre"}).text.strip()
#print fixDateFormat(meta.raw_data.find("span",attrs={"class":"data","itemprop":"datePublished"}).text)
#(tests??)
#print normalizeSystem("itch.io")
#print fixGame(":?'\;.><#&,'Master of Orion (1993)")
#print fixDateFormat("Jun 12, 2001")

# //getGenres()
# /*
# <li class="summary_detail product_genre"><span class="label">Genre(s): </span><span class="data" itemprop="genre">Action</span>,                                            <span class="data" itemprop="genre">Shooter</span>,                                            <span class="data" itemprop="genre">Shooter</span>,                                            <span class="data" itemprop="genre">Third-Person</span>,                                            <span class="data" itemprop="genre">Sci-Fi</span>,                                            <span class="data" itemprop="genre">Sci-Fi</span>,                                            <span class="data" itemprop="genre">Arcade</span>                                    </li>
# */

#print meta.raw_data
#meta = MetaCritic("virginia","pc")
#print meta.metacritic
#print meta.userscore
#link = meta.raw_data.find('li',attrs={"class":"summary_detail publisher"}).find("span",attrs={'itemprop':'name'}).text.strip()
#print link

#might need to use children/descendants to find the inner span
# len(list(soup.children))
# # 1
# len(list(soup.descendants))
# # 25

#link = meta.raw_data.find("li",attrs={"class":"summary_detail developer"}).find("span",attrs={"class":"data"}).text.strip()
#print link
#link = link.find("span",attrs={"class":"data"})
#print link
#     var fromText = '<span class="label">Developer:</span>';
#     var toText = 'an>';
#          developer = Parser.data(developer).from('<span class="data">').to("</sp").build();

# print meta.raw_data.find(user_score_class)
            
