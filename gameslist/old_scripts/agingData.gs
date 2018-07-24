function agingData() {
  var spreadSheet = SpreadsheetApp.openById('118X8AmxTSvciTREmJTMPvFGs8syXHitqlMVxzEL_pA0');
  var sheet = spreadSheet.getSheetByName('Owned or Beaten');
  var today = new Date();
  today = new Date(today.getYear(), today.getMonth(), today.getDate(), 0);
  var cell = sheet.getRange('AF1');
  var aging = cell.getValue();
  cell = sheet.getRange('AH1')
  var remaining = cell.getValue()
  //a2 and a6 from stats next
  sheet = spreadSheet.getSheetByName('Stats')
  cell = sheet.getRange('B2')
  var total = cell.getValue()
  cell = sheet.getRange('B6')
  var beaten = cell.getValue()
  sheet = spreadSheet.getSheetByName('Aging Record')
  sheet.appendRow([today,aging,remaining,beaten,total])
}
