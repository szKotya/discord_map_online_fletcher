
import discord
from datetime import datetime, date, time

BOT_TOKEN = ''
CHANNEL_FLETCH_ID = 
CHANNEL_RESPONCE_ID = 

DATE_A = datetime(2022, 3, 22)
DATE_B = None

IN_DISCORD = True
ONLY_TOP = True
SORT_TYPE_FIRST = 0
MAPS_LIMIT = 99999
PLAYERS_MIN = 16
PLAYTIME_MIN = 5

array_mapname = []
array_playtime = []
array_timeplays = []
array_online = []

g_iPlayers = 0
g_iMap_play = 0

client = discord.Client()
channel_fletch = None
channel_responce = None

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print()
    
    timecost = datetime.now()
    print('Init Start: ' + timecost.strftime("%m/%d/%Y, %H:%M:%S"))
    global channel_fletch
    channel_fletch = client.get_channel(CHANNEL_FLETCH_ID)
    global channel_responce
    channel_responce = client.get_channel(CHANNEL_RESPONCE_ID)
    timecost = str((datetime.now() - timecost).total_seconds())
    print('Init END: ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ' Seconds: ' + timecost)
    Message = None
    if IN_DISCORD == True:
        timecost = datetime.now()
        print('Clear Start' + timecost.strftime("%m/%d/%Y, %H:%M:%S"))
        Message = await channel_responce.history(limit=100).flatten()
        for message in Message:
            if message.author == client.user:
                await message.delete()
            else:
                break
        timecost = str((datetime.now() - timecost).total_seconds())
        print('Clear END: ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ' Seconds: ' + timecost)
    timecost = datetime.now()
    print('Data Fletch Start: ' + timecost.strftime("%m/%d/%Y, %H:%M:%S"))
    Message = await channel_fletch.history(after=DATE_A,before=DATE_B,limit=MAPS_LIMIT).flatten()
    timecost = str((datetime.now() - timecost).total_seconds())
    print('Data Fletch END: ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ' Seconds: ' + timecost)
    
    msgdate = -1
    filename = None 

    message = '-----------------------\n'
    message += 'Server: %s' % channel_fletch.name
    if DATE_A != None and DATE_B != None:
        message += '\n'
        message += ('after: %s' % DATE_A.strftime("%m/%d/%Y, %H:%M:%S"))
        message += '\n'
        message += ('before: %s' % DATE_B.strftime("%m/%d/%Y, %H:%M:%S"))

        filename = 'a' + DATE_A.strftime("%m-%d-%Y-%H-%M-%S") + 'b' + DATE_B.strftime("%m-%d-%Y-%H-%M-%S")
    elif DATE_A != None:
        message += (' after: %s' % DATE_A.strftime("%m/%d/%Y, %H:%M:%S"))
        filename = 'a' + DATE_A.strftime("%m-%d-%Y-%H-%M-%S")
    elif DATE_B != None:
        message += (' before: %s' % DATE_B.strftime("%m/%d/%Y, %H:%M:%S"))
        filename = 'b' + DATE_B.strftime("%m-%d-%Y-%H-%M-%S")
    message += '\n-----------------------'

    file = open(filename + '.txt', 'w')
    print(filename)
    print()
    
    print(message)
    file.write(message + '\n')
    await DiscordSendMessage(message)
    

    message = ''
    map_inday = 0
    for i in range(len(Message)):
        if Message[i].content != '' or Message[i].author.id != 230780946142593025:
            continue
        if ONLY_TOP == False:
            if msgdate != Message[i].created_at.day:
                if message != '':
                    await DiscordSendMessage(message)
                    message = ''

                map_inday = 0
                msgdate = Message[i].created_at.day
                
                temp = '-----------------------\n' + Message[i].created_at.strftime("%d %B") + '\n-----------------------'
                
                print(temp)
                file.write(temp + '\n')
                await DiscordSendMessage(temp)
        
        map_players = GetPlayersCount(Message[i].embeds[0].description)
        map_inday += 1

        map_playtime = GetTimePlayed(Message, i)

        global g_iPlayers
        g_iPlayers += map_players

        global g_iMap_play
        g_iMap_play += 1

        map_name = GetMapName(Message[i].embeds[0].description)

        if map_players > PLAYERS_MIN and map_playtime > PLAYTIME_MIN:
            CheckMap(map_name, map_playtime, map_players)   

        if ONLY_TOP == True:
            continue
        temp = format(str(map_inday) + ')', '<2s')
        map_name = format(map_name, '<45s')
        map_players = '(' + format(str(map_players) + '/64', '<5s') + ')'
        map_playtime = format(str(map_playtime) + ' min', '<6s')
        svalue = ('%s %s %s - %s - %s' % (temp, map_name, map_players, map_playtime, Message[i].created_at.strftime("%H:%M")))
        print(svalue)
        file.write(svalue + '\n')

        message += svalue + '\n'
        if len(message) > 1700:
            await DiscordSendMessage(message)
            message = ''
        

    if message != '':
        await DiscordSendMessage(message)
        message = ''

    for i in range(len(array_mapname)):
        array_online[i] = int(array_online[i] / array_timeplays[i])

    MySort1()
    
    if SORT_TYPE_FIRST == 0:
        message = ('\n-----------------------\nTop Maps by playtime\n')
    elif SORT_TYPE_FIRST == 1:
        message = ('\n-----------------------\nTop Maps by times\n')
    else:
        message = ('\n-----------------------\nTop Maps by online\n')

    message += ('Average Online: %i\n-----------------------' % (g_iPlayers/g_iMap_play))

    print(message)
    file.write(message + '\n')
    await DiscordSendMessage(message)
    
    message = ''
    for i in range(len(array_mapname)):
        map_inday = format(str(i + 1) + ')', '<2s')
        map_name = format(array_mapname[i], '<45s')
        map_players = '(' + format(str(array_online[i]) + '/64', '<5s') + ')'
        map_playtime = format(str(array_playtime[i]) + ' min', '<6s')

        temp = ('%s %s %s - %s - %i times' % (map_inday, map_name, map_players, map_playtime, array_timeplays[i]))
        print(temp)
        file.write(temp + '\n')
        
        message += temp + '\n'
        if IN_DISCORD == True:
            if len(message) > 1700:
                await DiscordSendMessage(message)
                message = ''
            else :
                if i == len(array_mapname)-1:
                    await DiscordSendMessage(message)
    file.close()

async def DiscordSendMessage(szMessage):
    if IN_DISCORD == True:
        szMessage = '```\n%s```' % szMessage
        await channel_responce.send(szMessage)

def MySort1():
    for i in range(len(array_mapname)-1):
        for j in range(len(array_mapname)-i-1):
            if MySort2(j):
                temp = array_mapname[j]
                array_mapname[j] = array_mapname[j+1]
                array_mapname[j+1] = temp

                temp = array_playtime[j]
                array_playtime[j] = array_playtime[j+1]
                array_playtime[j+1] = temp

                temp = array_timeplays[j]
                array_timeplays[j] = array_timeplays[j+1]
                array_timeplays[j+1] = temp

                temp = array_online[j]
                array_online[j] = array_online[j+1]
                array_online[j+1] = temp

def MySort2(j):
    if SORT_TYPE_FIRST == 0:
        if array_playtime[j] < array_playtime[j+1] or ((array_playtime[j] == array_playtime[j+1] and array_timeplays[j] < array_timeplays[j+1]) or (array_timeplays[j] == array_timeplays[j+1] and array_online[j] < array_online[j+1])):
            return True

    if SORT_TYPE_FIRST == 1:
        if array_timeplays[j] < array_timeplays[j+1] or ((array_timeplays[j] == array_timeplays[j+1] and array_playtime[j] < array_playtime[j+1]) or (array_playtime[j] == array_playtime[j+1] and array_online[j] < array_online[j+1])):
            return True

    if SORT_TYPE_FIRST == 2:
        if array_online[j] < array_online[j+1] or ((array_online[j] == array_online[j+1] and array_playtime[j] < array_playtime[j+1]) or (array_playtime[j] == array_playtime[j+1] and array_timeplays[j] < array_timeplays[j+1])):
            return True

    return False

def GetMapName(szString):
    szString = szString[13:szString.find('\n')]
    szString = szString.replace("\_", "_")
    szString = szString.replace("*", "")
    return szString.lower()
    

def GetTimePlayed(arrayMSG, ID):
    if ID == len(arrayMSG) - 1:
        return 0
    return int((arrayMSG[ID+1].created_at - arrayMSG[ID].created_at).total_seconds() / 60)

def GetPlayersCount(szString):
    return int(szString[szString.find('\n')+19:szString.find('/')])
    
def CheckMap(szMap, iMin, iOnline):
    if iMin > 0:
        i = MapInArray(szMap)
        if i == -1:
            array_mapname.append(szMap)
            array_playtime.append(iMin)
            array_timeplays.append(1)
            array_online.append(iOnline)
        else:
            array_playtime[i] += iMin
            array_timeplays[i] += 1
            array_online[i] += iOnline

def MapInArray(szMap):
    for i in range(len(array_mapname)):
        if array_mapname[i] == szMap:
            return i
    return -1

print('-----------------------')
client.run(BOT_TOKEN)
