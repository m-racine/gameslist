function fixSystem(system){
    var system = system.toString().toLowerCase().split(" ").join("-");
    if (system == "gba"){
       system = "game-boy-advance";
    }else if (system == "gbc"){
       system = "game-boy-color";
    }else if (system == "steam"){
       system = "pc";
    }else if (system == "gog"){
       system = "pc";
    }else if (system == "origin"){
       system = "pc";
    }else if (system == "humble"){
       system = "pc";
    }else if (system == "uplay"){
       system = "pc";
    }else if (system == "twitch"){
       system = "pc";
    }else if (system == "battle.net"){
       system = "pc";
    }else if (system == "n64"){
       system = "nintendo-64";
    }else if (system == "itch.io"){
       system = "pc";
    }else if (system == "kindle"){
       system = "ios";
    }else if (system == "android"){
       system = "ios";
    }else if (system == "vita"){
       system = "playstation-vita";
    }
    return system;
}

function fixGame(game){
   var game = game.toString().replace(/:/g,"").replace(/'/g,"").replace(/\./g,"").toLowerCase().replace(" & "," ").replace(/$/g,"").replace(/,/g,"");
   game = game.replace(/\//g,"").replace(/\(/g,"").replace(/\)/g,"").replace(/#/g,"");
   game = game.replace(/\?/g,"").replace(/;/g,"").replace(">","gt").replace("<","lt");
   return game.split(" ").join("-");
}

function getMetacritic(game, system) {
    Logger = BetterLog.useSpreadsheet("1OVWZs1izXutQ0JwhAxKdeUV-TfHUQvg6Io3FON53YjI");
    var game = fixGame(game)
    var system = fixSystem(system);
    var url = "http://www.metacritic.com/game/"+system+"/"+ game;
    Logger.log(url);
    var fromText = '<span itemprop="ratingValue">';
    var toText = '</span>';
    var options = {
    'contentType': 'application/json',
    'method': 'get',
    'muteHttpExceptions': true
    };
    try{
        var response = UrlFetchApp.fetch(url, options);
        if (response.getResponseCode() == 200){
           var content = response.getContentText();
           var metacritic = Parser
                           .data(content)
                           .from(fromText)
                           .to(toText)
                           .build();
        
        
        
        }else{
             Logger.log(game);
             return 0
        }
        Logger.log(metacritic);
      }catch(e){
        Logger.log(game);
        Logger.log(e);
        return e;
      }
   return +metacritic;
}

function getUserScore(game, system) {
    Logger = BetterLog.useSpreadsheet("1OVWZs1izXutQ0JwhAxKdeUV-TfHUQvg6Io3FON53YjI");
    var regExp = new RegExp("\\d\.\\d");
    var fromText = '<div class="metascore_w user large game';
    var toText = '</div>';
    var game = fixGame(game);
    var system = fixSystem(system);
    var url = "http://www.metacritic.com/game/"+system+"/"+ game;
    var options = {
    'contentType': 'application/json',
    'method': 'get',
    'muteHttpExceptions': true
    };
    try{
        var response = UrlFetchApp.fetch(url, options);
        if (response.getResponseCode() == 200){ 
          var content = response.getContentText();
          var userscore = Parser
                          .data(content)
                          .from(fromText)
                          .to(toText)
                          .build();
         userscore = regExp(userscore);
        }else{
             Logger.log(game);
             Logger.log(response.getResponseCode());
             return 0
        }
        Logger.log(userscore);
    }catch(e){
       Logger.log(game);
       Logger.log(e);
       return e;
    }
    return +userscore;
}

function getPublisher(game, system) {
    Logger = BetterLog.useSpreadsheet("1OVWZs1izXutQ0JwhAxKdeUV-TfHUQvg6Io3FON53YjI");
    var regExp = new RegExp("\\d\.\\d");
    var fromText = '<li class="summary_detail publisher"';
    var toText = '</li>';
    var game = fixGame(game);
    var system = fixSystem(system);
    var url = "http://www.metacritic.com/game/"+system+"/"+ game;
    var options = {
    'contentType': 'application/json',
    'method': 'get',
    'muteHttpExceptions': true
    };
    try{
        var response = UrlFetchApp.fetch(url, options);
        if (response.getResponseCode() == 200){ 
          var content = response.getContentText();
          var publisher = Parser
                          .data(content)
                          .from(fromText)
                          .to(toText)
                          .build();
          fromText = '<span itemprop="name">';
          toText = '</span>';
          publisher = Parser.data(publisher).from(fromText).to(toText).iterate();
          Logger.log(publisher);
          //https://stackoverflow.com/questions/19293997/javascript-apply-trim-function-to-each-string-in-an-array
          publisher = publisher.map(Function.prototype.call, String.prototype.trim)
          publisher = publisher.join();
        }else{
             Logger.log(game);
             Logger.log(response.getResponseCode());
             return "Unknown";
        }
        Logger.log(publisher);
    }catch(e){
       Logger.log(game);
       Logger.log(e);
       return e;
    }
    return publisher;
}

function getDeveloper(game, system) {
    Logger = BetterLog.useSpreadsheet("1OVWZs1izXutQ0JwhAxKdeUV-TfHUQvg6Io3FON53YjI");
    var regExp = new RegExp("\\d\.\\d");
    var fromText = '<span class="label">Developer:</span>';
    var toText = 'an>';
    var game = fixGame(game);
    var system = fixSystem(system);
    var url = "http://www.metacritic.com/game/"+system+"/"+ game;
    var options = {
    'contentType': 'application/json',
    'method': 'get',
    'muteHttpExceptions': true
    };
    try{
        var response = UrlFetchApp.fetch(url, options);
        if (response.getResponseCode() == 200){ 
          var content = response.getContentText();
          var developer = Parser
                          .data(content)
                          .from(fromText)
                          .to(toText)
                          .build();
         developer = Parser.data(developer).from('<span class="data">').to("</sp").build();
         developer = developer.trim();
        }else{
             Logger.log(game);
             Logger.log(response.getResponseCode());
             return "Unknown";
        }
        Logger.log(developer);
    }catch(e){
       Logger.log(game);
       Logger.log(e);
       return e;
    }
    return developer;
}

function getReleaseDate(game, system) {
    Logger = BetterLog.useSpreadsheet("1OVWZs1izXutQ0JwhAxKdeUV-TfHUQvg6Io3FON53YjI");
    var regExp = new RegExp("\\d\.\\d");
    var fromText = '<span class="data" itemprop="datePublished">';
    var toText = '</span>';
    var game = fixGame(game);
    var system = fixSystem(system);
    var url = "http://www.metacritic.com/game/"+system+"/"+ game;
    var options = {
    'contentType': 'application/json',
    'method': 'get',
    'muteHttpExceptions': true
    };
    try{
        var response = UrlFetchApp.fetch(url, options);
        if (response.getResponseCode() == 200){ 
          var content = response.getContentText();
          var date = Parser
                          .data(content)
                          .from(fromText)
                          .to(toText)
                          .build();
         //date = Parser.data(developer).from('<span class="data">').to("</sp").build();
         date = date.trim();
        }else{
             Logger.log(game);
             Logger.log(response.getResponseCode());
             return "Unknown";
        }
        Logger.log(date);
    }catch(e){
       Logger.log(game);
       Logger.log(e);
       return e;
    }
    return fixDateFormat(date);
}

//getGenres()
/*
<li class="summary_detail product_genre"><span class="label">Genre(s): </span><span class="data" itemprop="genre">Action</span>,                                            <span class="data" itemprop="genre">Shooter</span>,                                            <span class="data" itemprop="genre">Shooter</span>,                                            <span class="data" itemprop="genre">Third-Person</span>,                                            <span class="data" itemprop="genre">Sci-Fi</span>,                                            <span class="data" itemprop="genre">Sci-Fi</span>,                                            <span class="data" itemprop="genre">Arcade</span>                                    </li>
*/

function getPlayers(game, system) {
    Logger = BetterLog.useSpreadsheet("1OVWZs1izXutQ0JwhAxKdeUV-TfHUQvg6Io3FON53YjI");
    var regExp = new RegExp("\\d-?\\d?");
    var fromText = '<span class="label"># of players:</span>';
    var toText = '</span>';
    var game = fixGame(game);
    var system = fixSystem(system);
    var url = "http://www.metacritic.com/game/"+system+"/"+ game;
    var options = {
    'contentType': 'application/json',
    'method': 'get',
    'muteHttpExceptions': true
    };
    try{
        var response = UrlFetchApp.fetch(url, options);
        if (response.getResponseCode() == 200){ 
          var content = response.getContentText();
          var players = Parser
                          .data(content)
                          .from(fromText)
                          .to(toText)
                          .build();
         Logger.log(players);
         players = regExp(players);
         //players = players.trim();
        }else{
             Logger.log(game);
             Logger.log(response.getResponseCode());
             return "Unknown";
        }
        Logger.log(players);
    }catch(e){
       Logger.log(game);
       Logger.log(e);
       return e;
    }
    return players;
}

function fixDateFormat(date){
  //looks like "Jun 12, 2001"
  //should be "2001-06-12"
  Logger.log(date);
  var initial = date.split(", ");
  var second = initial[0].replace("  "," 0").split(" ");
  return initial[1] + "-" + swapMonth(second[0]) + "-" + second[1];
}

function swapMonth(month){
  if (month == "Jan"){
    return "01";
  }else if(month == "Feb"){
    return "02";
  }else if(month == "Mar"){
    return "03";
  }else if(month == "Apr"){
    return "04";
  }else if(month == "May"){
    return "05";
  }else if(month == "Jun"){
    return "06";
  }else if(month == "Jul"){
    return "07";
  }else if(month == "Aug"){
    return "08";
  }else if(month == "Sep"){
    return "09";
  }else if(month == "Oct"){
    return "10";
  }else if(month == "Nov"){
    return "11";
  }else if(month == "Dec"){
    return "12";
  }
}


function testGet(){
   //Logger.log(getPublisher("Runbow","Wii U"));
   Logger.log(getPlayers("SoulCalibur III","PlayStation 2"));
   
   //Logger.log(getUserScore("Dead Space","Origin"));
   return 'test';
}