#=ImportJSON("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=9D14EFB127C85C39448B89807C87EA99&steamid=76561198017111032&include_appinfo=1&include_played_free_games=1&format=json","/response/games/name,/response/games/playtime_forever","")


import json
import requests

request = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=9D14EFB127C85C39448B89807C87EA99&steamid=76561198017111032&include_appinfo=1&include_played_free_games=1&format=json")#,"/response/games/name,/response/games/playtime_forever","")
request_dict = json.loads(request.text)
games_list = request_dict['response']['games']

for game in games_list:
    print game['name'] + "  " + str(game['playtime_forever'])