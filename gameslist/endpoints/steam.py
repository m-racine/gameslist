#=ImportJSON("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=9D14EFB127C85C39448B89807C87EA99&steamid=76561198017111032&include_appinfo=1&include_played_free_games=1&format=json","/response/games/name,/response/games/playtime_forever","")


import json
import requests
import re



def get_all_games_for_user(APIKEY="9D14EFB127C85C39448B89807C87EA99", STEAMID="76561198017111032"):
    request = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={0}&steamid={1}&include_appinfo=1&include_played_free_games=1&format=json".format(APIKEY,STEAMID))#,"/response/games/name,/response/games/playtime_forever","")
    request_dict = json.loads(request.text)
    games_list = request_dict['response']['games']

    steam_games = []
    for game in games_list:
        steam_games.append([game['name'],game['playtime_forever'],get_score(game['appid']))

    return steam_games

def get_two_weeks_for_user(APIKEY="9D14EFB127C85C39448B89807C87EA99", STEAMID="76561198017111032"):
    request = requests.get("http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={0}&steamid={1}&include_appinfo=1&include_played_free_games=1&format=json".format(APIKEY,STEAMID))#,"/response/games/name,/response/games/playtime_forever","")
    request_dict = json.loads(request.text)
    games_list = request_dict['response']['games']

    steam_games = []
    for game in games_list:
        steam_games.append([game['name'],game['playtime_forever'],get_score(game['appid']))

    return steam_games

def get_score(APPID):
    request = requests.get("https://store.steampowered.com/appreviews/{0}".format(APPID))
    return json.loads(request.text)['query_summary']['review_score']
    #gets us review score- scale of 10 -- ['query_summary']['review_score']
    #https://store.steampowered.com/appreviews/12200

#returned data structure.
#{"appid":12200,"name":"Bully: Scholarship Edition","playtime_forever":0,
#"img_icon_url":"791f13dd4ea6c4cdf171670cc576682171c1eae5",
#"img_logo_url":"e2aad562be7e67c2477972fa738675e005cb73df","has_community_visible_stats":true,
#"playtime_windows_forever":0,"playtime_mac_forever":0,"playtime_linux_forever":0}

#so this can't get me purchase dates, so would depend on when it shows up to add it to the db
#pass it a key that's kept in config, and an id based on a USER object (so for now just a hardcoded id)
#and it returns a list of game, time lists?
#can do a FULL SEED and a recent flavor -- recent is what would run daily--only grabs last two weeks of data so going through it will be way faster.


#https://steamcommunity.com/profiles/76561198017111032/games/?tab=all -- can be  can be used to final last play date, in epoch time


#gets us review score- scale of 10 -- ['query_summary']['review_score']
#https://store.steampowered.com/appreviews/12200
#
# {"success":1,"query_summary":{"num_reviews":9,"review_score":6,"review_score_desc":"Mostly Positive","total_positive":3810,"total_negative":1012,"total_reviews":4822},"reviews":[{"recommendationid":"54981903","author":{"steamid":"76561198067359292","num_games_owned":423,"num_reviews":240,"playtime_forever":1357,"playtime_last_two_weeks":0,"last_played":1567733545},"language":"english","review":"First, if you plan playing this on Win10, you probably want to check the steam guides for the unnoficial patch guide, so it works correctly.\n\nI love this game, in a way is more fun being a small time school bully that a full blown crime kingpin like in GTA. I like the whole school town environment, classes add challenges and nice bonuses, the cutscenes and the voices are very varied and extensive and the story is quite nice.\n\nBe aware though, you want to save your game regularly as the game is still rough around the edges and there are certain bugs that can happen that will force you to reset the game, also sometimes the sounds around town get buggy or too loud, like you are hearing the car motors up close.\n\nDespite its few falls is one of my favorite games of the era and I hope some day Rockstar games decides to make a sequel with higher graphics and more highschool cliches.","timestamp_created":1567735794,"timestamp_updated":1567854792,"voted_up":true,"votes_up":12,"votes_funny":0,"weighted_vote_score":"0.667238056659698486","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"54940719","author":{"steamid":"76561198313292003","num_games_owned":52,"num_reviews":1,"playtime_forever":110,"playtime_last_two_weeks":0,"last_played":1567449730},"language":"english","review":"is not compatible with windows 10. crashes make game unplayable. really disappointing.","timestamp_created":1567462029,"timestamp_updated":1567462029,"voted_up":false,"votes_up":13,"votes_funny":4,"weighted_vote_score":"0.569225728511810303","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"55238396","author":{"steamid":"76561197971133301","num_games_owned":272,"num_reviews":13,"playtime_forever":351,"playtime_last_two_weeks":351,"last_played":1569187232},"language":"english","review":"Don't bother. PC port is bad - at least one mission was unfinishable and it crashes all the time.. Which sucks even more given the saving system which you should be familiar with if you've played other Rockstar titles: you have to go back to specific points on the map to save, which sometimes you won't do for a while so you can lose a lot of progress like that.\n\nI usually find endearing qualities in shitty games, hell I even got some enjoyment out of HDTF - but this is just bad.","timestamp_created":1569187411,"timestamp_updated":1569187411,"voted_up":false,"votes_up":2,"votes_funny":0,"weighted_vote_score":"0.54703831672668457","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"55080697","author":{"steamid":"76561198287703741","num_games_owned":113,"num_reviews":8,"playtime_forever":1452,"playtime_last_two_weeks":1111,"last_played":1569169017},"language":"english","review":"I've played this a lot more on XB360, so don't allow my playtime to concern you.\n\nThis is one of Rockstar's best games. Ever. \nIt did indeed get off on a rocky start, partly due to it's name. One highly misinformed individual branded it a \"Columbine Simulator\".\n\nIT. IS. NOT.\n\nGreat community, fun gameplay, nice story, great characters.\n\nThis specific version is a bit buggy though. From my experience there's no issues whatsoever with running it on Windows 10 (as of September 2019).\n\nUnplayable without a controller. Make sure you have an Xbox controller of somesorts before playing. The game also doesn't accept any input from the controller if it's disconnected midway through so I've had to start saving after every mission\/class etc.\n\nAll in all a great game though, save for some minor bugs. \n8.5\/10","timestamp_created":1568316973,"timestamp_updated":1568316973,"voted_up":true,"votes_up":2,"votes_funny":0,"weighted_vote_score":"0.545454561710357666","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"54969077","author":{"steamid":"76561198271917687","num_games_owned":114,"num_reviews":4,"playtime_forever":1368,"playtime_last_two_weeks":0,"last_played":1567656623},"language":"english","review":"f a t t y  h a s  a r r i v e d !","timestamp_created":1567650176,"timestamp_updated":1567650176,"voted_up":true,"votes_up":2,"votes_funny":7,"weighted_vote_score":"0.545454561710357666","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"54954201","author":{"steamid":"76561198118840472","num_games_owned":165,"num_reviews":6,"playtime_forever":277,"playtime_last_two_weeks":0,"last_played":1567549019},"language":"english","review":"Dont buy it. It will propably crash every time you try to play.","timestamp_created":1567549061,"timestamp_updated":1567549061,"voted_up":false,"votes_up":2,"votes_funny":0,"weighted_vote_score":"0.52173912525177002","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"55224509","author":{"steamid":"76561198873570469","num_games_owned":4,"num_reviews":4,"playtime_forever":238,"playtime_last_two_weeks":238,"last_played":1569281636},"language":"english","review":"[h1]BULLY IS BROKEN\n\nI literally bought this game today and after not playing it for 3 hours all of the audio is gone.\nMy headphones are working, I tried to played other games with my headphones and that worked too so i guess bully is bugged. The audio is one of the main reasons i liked bully, it had fun music, voices and effects so playing it without audio just ruins it for me.\n\nOverall, bully is a great game and its a 7\/10 in my books, \nhighly recommend despite the crashing and bugs","timestamp_created":1569119355,"timestamp_updated":1569119355,"voted_up":true,"votes_up":1,"votes_funny":0,"weighted_vote_score":"0.509803950786590576","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"55247886","author":{"steamid":"76561198192685183","num_games_owned":703,"num_reviews":93,"playtime_forever":1001,"playtime_last_two_weeks":0,"last_played":1491013820},"language":"english","review":"The best Rockstar game.","timestamp_created":1569254887,"timestamp_updated":1569254887,"voted_up":true,"votes_up":1,"votes_funny":0,"weighted_vote_score":"0.508196711540222168","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false},{"recommendationid":"55224328","author":{"steamid":"76561198416679017","num_games_owned":186,"num_reviews":20,"playtime_forever":1297,"playtime_last_two_weeks":57,"last_played":1568694207},"language":"english","review":"One of my favourite Rockstar games!, and who can forget the amazing soundtrack :). Its cheaper now days and its worth the money! 10\/10","timestamp_created":1569117950,"timestamp_updated":1569117950,"voted_up":true,"votes_up":1,"votes_funny":0,"weighted_vote_score":"0.508196711540222168","comment_count":0,"steam_purchase":true,"received_for_free":false,"written_during_early_access":false}],"cursor":"AoIIPwIZM3iA1dIB"}
