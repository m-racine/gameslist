import csv

    # with open(os.path.join("input","feed_comment.csv"), 'rb') as csvfile:
    #     with open(os.path.join("input","feed_comment_a.csv"), 'wb') as csv2file:
    #         spamreader = csv.DictReader(csvfile, delimiter=',')
    #         spamwriter = csv.DictWriter(csv2file, delimiter=',',fieldnames=['ID','PARENTID','TYPE','COMMENTBODY','CREATEDBYID','CREATEDDATE'])
    #         spamwriter.writeheader()
    #         for row in spamreader:
    #             #check for comment body
    #             if row['COMMENTTYPE'] == "ContentComment":
    #                 #print row
    #                 try:
    #                     attach = attachment_record[row['RELATEDRECORDID']]
    #                     if isImageFile(attach):
    #                         row['COMMENTBODY'] = row['COMMENTBODY'] + "\n !{0}|thumbnail!".format(attach)
    #                         print row['COMMENTBODY']
    #                     else:
    #                         row['COMMENTBODY'] = row['COMMENTBODY'] + "\n[^{0}]".format(attach)
    #                 except KeyError as e:
    #                     print e
    #                     logging.error("missing attachemnt")
    #                     logging.error(e)
                    
    #             temp = {'ID':row['ID'],'PARENTID':row['PARENTID'],'TYPE':row['COMMENTTYPE'],'COMMENTBODY':row['COMMENTBODY'],'CREATEDBYID':row['CREATEDBYID'],'CREATEDDATE':row['CREATEDDATE']}
    #             spamwriter.writerow(temp)
def yes_no_true_false(answer):
    if answer == "Yes":
        return "TRUE"
    else: 
        return "FALSE"

def system_sub(system):
    systems_dict = {'Nintendo 3DS':"3DS",
                    '3DS':'3DS',
                    'Android': "AND",
                    'Atari': "ATA",
                    'Battle.net':'BNT',
                    'Digipen':'DIG',
                    'Nintendo DS':'NDS',
                    'DS':'NDS',
                    'Gamecube':'GCN',
                    'GameCube':'GCN',
                    'Game Boy':'GB',
                    'GB':'GB',
                    'Game Boy Color':'GBC',
                    'GBC':'GBC',
                    'Game Boy Advance':'GBA',
                    'GBA':'GBA',
                    'GameGear':'GG',
                    'GoG':'GOG',
                    'Humble':'HUM',
                    'IndieBox':'IND',
                    'Itch.io':'IIO',
                    'Kindle':'KIN',
                    'Nintendo Entertainment System':'NES',
                    'NES':'NES',
                    'Nintendo 64':'N64',
                    'N64':'N64',
                    'Origin':'ORN',
                    'PC':'PC',
                    'Playstation':'PSX',
                    'PlayStation':'PSX',
                    'Playstation 2':'PS2',
                    'PlayStation 2':'PS2',
                    'Playstation 3':'PS3',
                    'PlayStation 3':'PS3',
                    'Playstation 4':'PS4',
                    'PlayStation Portable':'PSP',
                    'PSP':'PSP',
                    'Super Nintendo Entertainment System':'SNS',
                    'SNES':'SNS',
                    'Steam':'STM',
                    'Switch':'NSW',
                    'Twitch':'TWH',
                    'Uplay':'UPL',
                    'UPlay':'UPL',
                    'Vita':'VIT',
                    'Wii':'WII',
                    'Wii U':'WIU',
                    'WiiU':'WIU',
                    'Xbox':'XBX',
                    'Xbox 360':'360',
                    'Xbox One':'XB1'}
    if system in systems_dict:
        return systems_dict[system]
    else:
        print "{0} not in dictionary!".format(system)
        return system

def format_sub(form):
    format_dict ={'Physical':'P',
         'Digital':'D',
         'Missing':'M',
         'Borrowed':'B',
         'None':'N',
         'Returned':'R',
         'Lent':'L',
         'Expired':'E'}
    if form in format_dict:
        return format_dict[form]
    else:
        print "{0} not in dictionary!".format(form)
        return form

with open("/home/jracine/Downloads/Games Tracker - Owned or Beaten.csv",'r') as to_Clean:
    with open("/home/jracine/Downloads/cleaned.csv",'w') as cleaned:
        spamreader = csv.DictReader(to_Clean,delimiter=',')
        spamwriter = csv.DictWriter(cleaned, delimiter=',',fieldnames=['name','system','played','beaten',
                                                                       'location','game_format','notes','purchase_date',
                                                                       'finish_date','abandoned','perler','reviewed',
                                                                       'aging','play_aging'])
        spamwriter.writeheader()
        for row in spamreader:
            #print row
            #do the filtering
            cleaned_row = {}
            cleaned_row['name'] = row['Game']
            cleaned_row['system'] = system_sub(row['System'])
            cleaned_row['played'] = yes_no_true_false(row['Played'])
            cleaned_row['beaten'] = yes_no_true_false(row['Beaten'])
            cleaned_row['location'] = system_sub(row['Location'])
            cleaned_row['game_format'] = format_sub(row['Format'])
            cleaned_row['notes'] = row['Notes']
            cleaned_row['purchase_date'] = row['PurchaseDate']
            cleaned_row['finish_date'] = row['CompletionDate']
            cleaned_row['abandoned'] = yes_no_true_false(row['Abandoned'])
            cleaned_row['perler'] = yes_no_true_false(row['Perler'])
            cleaned_row['reviewed'] = yes_no_true_false(row['Review/Article'])
            cleaned_row['aging'] = row['Aging']
            cleaned_row['play_aging'] = row['PlayAging']

            spamwriter.writerow(cleaned_row)