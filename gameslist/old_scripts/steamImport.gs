function updateTimes() {
  var url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=9D14EFB127C85C39448B89807C87EA99&steamid=76561198017111032&include_appinfo=1&include_played_free_games=1&format=json';
  var response = UrlFetchApp.fetch(url, {'muteHttpExceptions': true});
  var json = response.getContentText();
  var game_data = JSON.parse(json).response;
  Logger.log(game_data);
  //column a for names, column P for current time
  var spreadSheet = SpreadsheetApp.openById('118X8AmxTSvciTREmJTMPvFGs8syXHitqlMVxzEL_pA0');
  var sheet = spreadSheet.getSheetByName('Owned or Beaten');
  var games = sheet.getRange("A2:A").getValues();
  //Logger.log(games)
  var times = new Array(games.length);
  //Logger.log(times.length);
  for (i=0;i<games.length;i++){
    Logger.log(game_data.games[i][0]) 
  }
}
