#YOUTUBE VIDEO ROULETTE
#CREATED BY SIDHARTA310312 ON GITHUB.COM
#FEEL FREE TO REUSE AND EDIT THIS PROJECT
#CHECK README.MD FOR GUIDE ON HOW TO USE THIS CODE

import pygame
import sys, os, json
import time
import random, math
import requests
import string
import webbrowser
from googleapiclient.discovery import build
from pathlib import Path
import pyperclip




#init screen
pygame.init()
screensize = (800,600)
centerPos = (screensize[0] // 2, screensize[1] // 2)
screen = pygame.display.set_mode(screensize)

clock = pygame.time.Clock() #make new clock object to control FPS

def MakeText(text, size, color, pos, thick):
    newText = pygame.font.SysFont("Consolas",size, bold=thick).render(text, True, color)
    newText_rect = newText.get_rect()
    newText_rect.center = pos
    screen.blit(newText, newText_rect)
    return newText_rect

def randomLink(API, Topic):
    url = "https://www.googleapis.com/youtube/v3/search"

    params_data = {
        "key": API,
        "maxResults": random.randint(10,30),
        "part":"snippet",
        "type":"video",
        "q": "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(1,5)))
    }

    if len(Topic) > 0:
        params_data["q"] = Topic

    response = requests.get(url, params=params_data).json()
    items = response.get("items", [])

    #print(response)

    if items:
        random_video = random.choice(items)
        return random_video['id']['videoId']
    print(response)
    return None

def getURL(ID):
    url = f"https://www.youtube.com/shorts/{ID}"
    if requests.head(url, allow_redirects=False).status_code == 200:
        return "https://www.youtube.com/shorts/" + ID

    return "https://www.youtube.com/watch?v=" + ID
    #Code 303 is long-form, Code 200 is YT Shorts

def SaveData(data):
    dihrectory = "D:/YTVideoRoulette_Data"
    filename = "RouletteHistory.json"

    full_path = os.path.join(dihrectory, filename) #Make full path directory

    
    os.makedirs(dihrectory, exist_ok=True) #Check directory existence

    # Write data using json.dump()
    with open(full_path, "w") as file:
        json.dump(data, file)

def FetchHistoryData():
    try:
        with open('D:/YTVideoRoulette_Data/RouletteHistory.json', 'r') as file:
            return json.load(file)
    except:
        return {}


#declare variables
creditTextPos = screensize[1]

kunci = "ADD API KEY HERE" #Guide on creating API key is written in README.md
page = "start"
arrowPos = 200
videoID = ""
loadProgress = 0

print("API key used : " , kunci)

youtube = build('youtube', 'v3', developerKey=kunci)
video_snippet = None
video_stats = None
video_contentDetails = None
channel_snippet = None
channel_stats = None
errorCode = 0

videoHistory = FetchHistoryData()


viewByHistory = False
history_TotalPages = math.floor(len(videoHistory) / 10)
history_SelectedPage = history_TotalPages
history_SelectedIndex = len(videoHistory) #(history_SelectedPage * 10) + len(list(videoHistory)[(history_SelectedPage * 10):(history_SelectedPage * 10)+10])
IndexSearch_input = ""
IndexSearch_msg = "Hit [ENTER] to view video based off the index"
IS_msg_cooldown = 0


thumbnailImage = None #placeholder lmao
Thumbnail_Temp_File = False
thumbnail_loadattempts = 0

greenLinePos = 0
lineCount = 10

copyBtnMSG = "Click me to copy URL!"
copyCooldown = 0

#settings-related variables
topic_input = ""
histErase_msg = "ERASE ROULETTE HISTORY"

#init colors
red = (255,0,0)
darkRed = (140,0,0)
green = (0,200,0)
darkGreen = (0, 100, 0)
blue = (0,0,255)
oceanBlue = (0, 119, 190)
yellow = (255, 255, 0)
darkYellow =  (139, 128, 0)
white = (255,255,255)
black = (0,0,0)

#init rect
startBtn = pygame.Rect(0,0,200,100)
playvidBtn = pygame.Rect(0,0,400,100)
cursor = pygame.Rect(0,0,20,20)
loadingBar = pygame.Rect(0,0,400,50)
thumbnailRect = pygame.Rect(0,0,320,10)
copyBtn = pygame.Rect(0,0,screensize[0] - 200, 40)
historyBtn = pygame.Rect(0,0,200,50)
pageBtns = (pygame.Rect(0,0,50,50), pygame.Rect(0,0,50,50))
history_confirmBtns = (pygame.Rect(0,0,300,75), pygame.Rect(0,0,300,75))
settingsBtn = pygame.Rect(0,0,200,50)

running = True


while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if startBtn.colliderect(cursor):
                if (page == "start" or page == "video"):
                    thumbnailImage = None #placeholder lmao
                    Thumbnail_Temp_File = False
                    loadProgress = 0
                    videoID = ""
                    page = {"True":"history","False":"load"}[str(viewByHistory)]
                    if page == "history":
                        history_TotalPages = math.floor(len(videoHistory) / 10)
                        history_SelectedPage = history_TotalPages
                        history_SelectedIndex = len(videoHistory)

                elif (page == "error" or page == "load"):
                    page = "start"
                    creditTextPos = screensize[1]
                    loadProgress = 0
            elif playvidBtn.colliderect(cursor) and page == "video":
                webbrowser.open_new_tab(getURL(videoID))

            elif copyBtn.colliderect(cursor) and page == "video":
                if copyBtnMSG == "Click me to copy URL!":
                    pyperclip.copy(getURL(videoID))
                    copyBtnMSG = "Successfully copied!"
                    copyCooldown = time.time() + 5

            elif historyBtn.colliderect(cursor) and (page == "start" or page == "historyIndexSearch") and len(videoHistory) > 0:
                history_TotalPages = math.floor(len(videoHistory) / 10)
                history_SelectedPage = history_TotalPages
                history_SelectedIndex = len(videoHistory)
                page = "history"

            elif page == "history":
                for i, button in enumerate(pageBtns):
                    if button.colliderect(cursor):
                        if [history_SelectedPage > 0, history_SelectedPage < history_TotalPages][i]:
                            history_SelectedPage += [-1,1][i]
                            history_SelectedIndex = (history_SelectedPage * 10) + len(list(videoHistory)[(history_SelectedPage * 10):(history_SelectedPage * 10)+10])

                            print(history_SelectedIndex)
                            print("CURRENT PAGE :" , history_SelectedPage , "/" , history_TotalPages)
                
                if historyBtn.colliderect(cursor): #Detect if Search By Index btn clicked in Roulette History page
                    page = "historyIndexSearch"
            
            elif page == "historyViewing":
                for i,btn in enumerate(history_confirmBtns):
                    if btn.colliderect(cursor) and pygame.mouse.get_pressed()[0]:
                        viewByHistory = [True, False][i]
                        page = ["loadThumbnail", "history"][i]
                        if page == "history":
                            history_TotalPages = math.floor(len(videoHistory) / 10)
                            history_SelectedPage = history_TotalPages
                            history_SelectedIndex = len(videoHistory)

            elif settingsBtn.colliderect(cursor) and page == "start" and len(videoHistory) > 0:
                page = "settings"

            elif page == "settings":
                if historyBtn.colliderect(cursor):
                    if histErase_msg == "ERASE ROULETTE HISTORY":
                        histErase_msg = "u sure bro?"
                    elif histErase_msg == "u sure bro?":
                        Path("D:/YTVideoRoulette_Data/RouletteHistory.json").unlink(missing_ok=True)
                        histErase_msg = "ERASE ROULETTE HISTORY"
                        videoHistory = FetchHistoryData()
                elif settingsBtn.colliderect(cursor):
                    creditTextPos = screensize[1]
                    page = "start"

        if event.type == pygame.KEYDOWN and page == "history":
            firstIndex = (history_SelectedPage * 10)
            lastIndex = firstIndex + len(list(videoHistory)[firstIndex:firstIndex+10])

            page_keys = ((event.key == pygame.K_LEFT or event.key == pygame.K_a), (event.key == pygame.K_RIGHT or event.key == pygame.K_d))

            #UP and DOWN movements
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and history_SelectedIndex > firstIndex + 1:
                history_SelectedIndex -= 1
            
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and history_SelectedIndex <= lastIndex - 1:
                history_SelectedIndex += 1
            
            for i,key in enumerate(page_keys):
                if [history_SelectedPage > 0, history_SelectedPage < history_TotalPages][i] and key:
                    history_SelectedPage += [-1,1][i]
                    history_SelectedIndex = (history_SelectedPage * 10) + len(list(videoHistory)[(history_SelectedPage * 10):(history_SelectedPage * 10)+10])
            
            if event.key == pygame.K_RETURN:
                videoID = videoHistory[str(history_SelectedIndex)]

                video_snippet = youtube.videos().list(part = "snippet", id=videoID).execute()['items'][0]['snippet']
                video_stats = youtube.videos().list(part = "statistics", id=videoID).execute()['items'][0]['statistics']
                channel_snippet = youtube.channels().list(part = "snippet", id = video_snippet['channelId']).execute()['items'][0]['snippet']
                channel_stats = youtube.channels().list(part = "statistics", id = video_snippet['channelId']).execute()['items'][0]['statistics']

                video_contentDetails = youtube.videos().list(part = "contentDetails", id=videoID).execute()['items'][0]['contentDetails']

                page = "historyViewing"
            
            if event.key == pygame.K_BACKSPACE:
                page = "start"
                creditTextPos = screensize[1]


            print("SELECTING : " , history_SelectedIndex)
            print("FIRST : " , firstIndex)
            print("LAST : " , lastIndex)
            print("CURRENT PAGE :" , history_SelectedPage , "/", history_TotalPages)
            #print(len(videoHistory)%10)
            print("\n")
        
        if event.type == pygame.KEYDOWN and page == "historyIndexSearch":
            for key in range(pygame.K_0, pygame.K_9 + 1):
                if event.key == key:
                    IndexSearch_input = IndexSearch_input + pygame.key.name(key)

            if event.key == pygame.K_BACKSPACE:
                IndexSearch_input = IndexSearch_input[0:len(IndexSearch_input) - 1]
            elif event.key == pygame.K_RETURN and len(IndexSearch_input) > 0:
                Intified_Input = int(IndexSearch_input)
                if Intified_Input > 0 and Intified_Input <= len(videoHistory):
                    print("VALID INDEX")
                    videoID = videoHistory[IndexSearch_input]

                    #retrieve video data
                    video_snippet = youtube.videos().list(part = "snippet", id=videoID).execute()['items'][0]['snippet']
                    video_stats = youtube.videos().list(part = "statistics", id=videoID).execute()['items'][0]['statistics']
                    channel_snippet = youtube.channels().list(part = "snippet", id = video_snippet['channelId']).execute()['items'][0]['snippet']
                    channel_stats = youtube.channels().list(part = "statistics", id = video_snippet['channelId']).execute()['items'][0]['statistics']

                    video_contentDetails = youtube.videos().list(part = "contentDetails", id=videoID).execute()['items'][0]['contentDetails']

                    viewByHistory = True
                    history_SelectedIndex = Intified_Input
                    page = "historyViewing"
                else:
                    print("INVALID INDEX")
                    IS_msg_cooldown = time.time() + 5
                    IndexSearch_input = ""

        if event.type == pygame.KEYDOWN and page == "settings":
            if event.key in range(pygame.K_0, pygame.K_z + 1) and len(topic_input) <= 40:
                topic_input += chr(event.key).upper()
                print(len(topic_input))
            
            if event.key == pygame.K_BACKSPACE:
                topic_input = topic_input[0:len(topic_input)-1]

            if event.key == pygame.K_SPACE:
                topic_input = topic_input + " "

        if page == "historyViewing":
            for i,btn in enumerate(history_confirmBtns):
                if btn.colliderect(cursor) and pygame.mouse.get_pressed()[0]:
                    viewByHistory = [True, False][i]
                    page = ["loadThumbnail", "history"][i]

    screen.fill(black)
    cursor.center = pygame.mouse.get_pos() #update cursor position

    


    if page == "start":
        startBtn.size = (200,100)
        thumbnailRect = pygame.Rect(0,0,320,10)
        thumbnailImage = None #placeholder lmao
        Thumbnail_Temp_File = False
        viewByHistory = False

        pygame.display.set_caption("Youtube Videos Roulette")
        MakeText("YT VIDEO ROULETTE", 50, green, (centerPos[0], centerPos[1] - 200), False) #make heading text
        MakeText("Made by sidharta310312 on GitHub", 20, yellow, (centerPos[0], centerPos[1] - creditTextPos), False)
        if creditTextPos > 150:
            creditTextPos -= creditTextPos/75
        
        print(creditTextPos)

        startBtn.center = centerPos
        if startBtn.colliderect(cursor):
            pygame.draw.rect(screen, darkGreen, startBtn)
            if arrowPos > 130:
                arrowPos -= 7
        else:
            pygame.draw.rect(screen, green, startBtn)
            if arrowPos < 200:
                arrowPos += 2


        MakeText("RANDOMIZE", 30, white, startBtn.center, False)

        arrowFontSize = int((centerPos[0] - arrowPos)/3)
        MakeText(">", arrowFontSize, white, (centerPos[0] - arrowPos, startBtn.center[1]), False)
        MakeText("<", arrowFontSize, white, (centerPos[0] + arrowPos, startBtn.center[1]), False)

        if len(videoHistory) > 0:
            historyBtn.center = centerPos[0], centerPos[1] + 100
            if historyBtn.colliderect(cursor):
                pygame.draw.rect(screen, blue, historyBtn)
            else:
                pygame.draw.rect(screen, oceanBlue, historyBtn)
            MakeText("ROULETTE HISTORY", 20, white, historyBtn.center, historyBtn.colliderect(cursor))

            settingsBtn.center = centerPos[0], centerPos[1] + 175
            if settingsBtn.colliderect(cursor):
                pygame.draw.rect(screen, darkYellow, settingsBtn)
            else:
                pygame.draw.rect(screen, yellow, settingsBtn)
            MakeText("SETTINGS", 20, black, settingsBtn.center, settingsBtn.colliderect(cursor))
    
    elif page == "load":
        thumbnailRect = pygame.Rect(0,0,320,10)
        pygame.display.set_caption("Youtube Videos Roulette (We're finding the video for you!)")

        unix = round(time.time()) % 4
        loadingText = f"LOADING{("." * unix)}"
        MakeText(loadingText, 30, white, (centerPos[0], centerPos[1] - 50), False)

        loadingBar.center = centerPos
        pygame.draw.rect(screen,darkGreen,loadingBar)

        loadedBar = pygame.Rect(loadingBar.x, loadingBar.y, loadProgress * 4, 50)
        pygame.draw.rect(screen, green, loadedBar)
        MakeText(f"{round(loadProgress)}%", 30, white, (loadedBar.x + loadProgress * 4 + 50, loadingBar.centery), False)

        MakeText({"True":f"Searching with topic : {topic_input}", "False":"Searching with randomized topic..."}[str(len(topic_input) > 0)], 20, green, (centerPos[0], screensize[1]-40),True)

        if loadProgress < 100:
            loadProgress += random.randint(0,200) * 0.01
            if loadProgress > 20:
                startBtn.center = loadingBar.center[0], loadingBar.center[1] + 100
                startBtn.size = (200,50)
                if startBtn.colliderect(cursor):
                    pygame.draw.rect(screen, darkRed, startBtn)
                else:
                    pygame.draw.rect(screen, red, startBtn)
                MakeText("CANCEL", 30, white, startBtn.center, False)
        else:
            videoID = randomLink(kunci, topic_input)
            if videoID == None:
                page = "error"
            else:
                video_snippet = youtube.videos().list(part = "snippet", id=videoID).execute()['items'][0]['snippet']
                video_stats = youtube.videos().list(part = "statistics", id=videoID).execute()['items'][0]['statistics']
                channel_snippet = youtube.channels().list(part = "snippet", id = video_snippet['channelId']).execute()['items'][0]['snippet']
                channel_stats = youtube.channels().list(part = "statistics", id = video_snippet['channelId']).execute()['items'][0]['statistics']

                video_contentDetails = youtube.videos().list(part = "contentDetails", id=videoID).execute()['items'][0]['contentDetails']

                #Update video history data
                videoHistory[str(len(videoHistory)+1)] = videoID
                SaveData(videoHistory)

                history_TotalPages = math.floor(len(videoHistory) / 10) 
                history_SelectedPage = history_TotalPages
                history_SelectedIndex = len(videoHistory)

                page = "loadThumbnail"
    
    elif page == "error":
        pygame.display.set_caption("Youtube Videos Roulette (Whoops)")

        MakeText("ERROR!!11!", 60, red, (centerPos[0], centerPos[1] - 200), False)
        MakeText("Unable to find video :(", 30, white, (centerPos[0], centerPos[1] - 50), False)

        loadingBar.center = centerPos
        pygame.draw.rect(screen,darkGreen,loadingBar)

        loadedBar = pygame.Rect(loadingBar.x, loadingBar.y, loadProgress * 4, 50)
        pygame.draw.rect(screen, red, loadedBar)
        MakeText(f"{round(loadProgress)}%", 30, white, (loadedBar.x + loadProgress * 4 + 50, loadingBar.centery), False)

        if loadProgress > 0:
            loadProgress -= (round(loadProgress) / 100)
        
        if loadProgress < 30:
            startBtn.center = centerPos[0], centerPos[1] + 100
            pygame.draw.rect(screen, green, startBtn)
            if startBtn.colliderect(cursor):
                pygame.draw.rect(screen, darkGreen, startBtn)
                MakeText("click me!", 30, white, startBtn.center, False)
            else:
                pygame.draw.rect(screen, green, startBtn)
                MakeText("RETRY", 30, white, startBtn.center, False)

    elif page == "loadThumbnail":
        startBtn.size = (200,100)

        MakeText("Loading Thumbnail", 60, white, centerPos, True)
        MakeText(f"[ID = {videoID}]", 20, white, (centerPos[0], centerPos[1] + 50), True)
        pygame.display.flip()

        thumbnail_fetchdata = requests.get(f"https://img.youtube.com/vi/{videoID}/mqdefault.jpg")

        thumbnailRect.center = centerPos[0] // 2, centerPos[1] // 2

        thumbnailDihrectory = "D:/YTVideoRoulette_Data"
        os.makedirs(thumbnailDihrectory, exist_ok=True)

        if thumbnail_fetchdata.status_code == 200 and not Thumbnail_Temp_File: #Create temporary thumbnail file if one hasn't been made
            with open(f"{thumbnailDihrectory}thumbnail_{videoID}.jpg", "wb") as f:
                print("CONSOLE : Making temporary Thumbnail File")

                f.write(thumbnail_fetchdata.content)
                
                Thumbnail_Temp_File = True #Set Thumbnail_Temp_File to true, so that the program only make temp file **once**

        elif Thumbnail_Temp_File:#if temp file already made then load img
            print("CONSOLE : Loading thumbnail")

            try:
                filepath = os.path.join(os.path.dirname(__file__), f"{thumbnailDihrectory}thumbnail_{videoID}.jpg")
                thumbnailImage = pygame.image.load(filepath).convert() #get thumbnail image data once

                page = "video"
                os.remove(filepath)
            except pygame.error as e:
                print("CONSOLE : Failed to load thumbnail")
                page = "loadThumbnail"
        else: #Thumbnail **not** available
            thumbnailImage = None
            page = "video"
        
    elif page == "video":
        pygame.display.set_caption(f"YouTube Videos Roulette (Here's your video! ID = {videoID})")

        thumbnailRect.center = centerPos[0] // 2, centerPos[1] // 2
        #thumbnailRect = pygame.Rect(0,0,320,10)

        if thumbnailRect.size[1] <= 180:
            thumbnailRect.size = thumbnailRect.size[0], thumbnailRect.size[1] + 10
            pygame.draw.rect(screen, green, thumbnailRect)
        else:
            if thumbnailImage == None: #If thumbnail error
                pygame.draw.rect(screen, green, thumbnailRect)
                MakeText("Thumbnail unfortunately unavailable :(", 40, white, thumbnailRect.center, False)
            else:
                screen.blit(thumbnailImage, thumbnailRect)
        

        title = video_snippet['title']
        if len(title) > 30:
            title = video_snippet['title'][:30] + "..."

        publish = video_snippet['publishedAt'][:10]
        views = video_stats['viewCount']
        likes, dislikes = video_stats.get('likeCount', 0), video_stats.get('dislikeCount', 0)
        comments = video_stats.get('commentCount', 0)
        duration = video_contentDetails['duration']

        channel =  channel_snippet['title']
        subbers = channel_stats['subscriberCount']
        videoIndex = {"True":history_SelectedIndex, "False":len(videoHistory)}[str(viewByHistory)]

        fullInfo = f"Title : {title}\n\nChannel : {channel}"
        sideInfo = f"[Views] : {views}\n[Likes:Dislikes] {likes}:{dislikes}\n[Comments] {comments}\n[ReleaseDate] {publish}\n\nDislike button kinda bugged btw"

        #dont mind the spaghetti code :)

        infoText = pygame.font.SysFont('Consolas', 30).render(fullInfo, True, green)
        infoText_rect = infoText.get_rect()
        infoText_rect.topleft = thumbnailRect.bottomleft[0], thumbnailRect.bottomleft[1] + 30
        screen.blit(infoText, infoText_rect)

        sideInfoText = pygame.font.SysFont('Consolas', 20).render(sideInfo, True, green)
        sideInfoText_rect = sideInfoText.get_rect()
        sideInfoText_rect.topleft = thumbnailRect.topright[0] + 30, thumbnailRect.topleft[1]
        screen.blit(sideInfoText, sideInfoText_rect)

        subCountText = pygame.font.SysFont('Consolas', 20).render(f"with {subbers} subscribers", True, green)
        subCountText_rect = subCountText.get_rect()
        subCountText_rect.topleft = infoText_rect.bottomleft[0], infoText_rect.bottomleft[1] + 10
        screen.blit(subCountText, subCountText_rect)

        indexText = pygame.font.SysFont('Consolas',10).render(f"Index of video in Roulette History : {videoIndex}", True, yellow)
        indexText_rect = indexText.get_rect()
        indexText_rect.topleft = sideInfoText_rect.bottomleft[0], sideInfoText_rect.bottomleft[1] + 30
        screen.blit(indexText, indexText_rect)

        #now lets make the buttons

        playvidBtn.center = centerPos[0] - 150, centerPos[1] + 200 #Open video btn
        if playvidBtn.colliderect(cursor):
            pygame.draw.rect(screen, darkGreen, playvidBtn)
        else:
            pygame.draw.rect(screen, green, playvidBtn)

        MakeText("OPEN VIDEO", 50, white, playvidBtn.center, True)


        startBtn.center = centerPos[0] + 200, centerPos[1] + 200 #Reroll btn
        if startBtn.colliderect(cursor):
            pygame.draw.rect(screen, {"True":darkYellow,"False":blue}[str(viewByHistory)], startBtn)
        else:
            pygame.draw.rect(screen, {"True":yellow,"False":oceanBlue}[str(viewByHistory)], startBtn)

        MakeText({"True":"BACK TO HISTORY", "False":"REROLL"}[str(viewByHistory)], {"True":20, "False":50}[str(viewByHistory)], {"True":black,"False":white}[str(viewByHistory)], startBtn.center, True)
        if not viewByHistory:
            MakeText(f"Rolls you've made : {len(videoHistory)}", 10, white, (startBtn.center[0], startBtn.center[1]+25), True)


        copyBtn.center = centerPos[0], centerPos[1] - 270 #Copy link btn
        if copyBtn.colliderect(cursor):
            pygame.draw.rect(screen, darkGreen, copyBtn)
            
        else:
            pygame.draw.rect(screen, green, copyBtn)

        MakeText(copyBtnMSG, 20, white, copyBtn.center, True)

        if time.time() > copyCooldown:
             copyBtnMSG = "Click me to copy URL!"
    
    elif page == "history":
        videoHistory = FetchHistoryData()
        #Lower i = Older
        #Higher i = Newer

        MakeText("ROULETTE HISTORY", 50, white, (centerPos[0], 50), True)
        if int(str(round(time.time(),1))[-1]) > 5:
            MakeText("Press [BACKSPACE] to go back to homepage :)", 20, green, (centerPos[0], 80), True)
        else:
            MakeText("Press [BACKSPACE] to go back to homepage :)", 20, white, (centerPos[0], 80), True)
        #MakeText("See what videos you've gotten before!", 20, white, (centerPos[0], 100), True)

        firstIndex = history_SelectedPage * 10
        lastIndex = firstIndex + len(list(videoHistory)[firstIndex:firstIndex+10])

        margin = 0
        #print(f"{history_SelectedPage}/{history_TotalPages}")

        for i in range(len(videoHistory), 0, -1):
            if i > firstIndex and i <= lastIndex:
                margin += 40
                vid_pos = (centerPos[0], centerPos[1] - 230 + margin)

                if history_SelectedIndex != i:
                    MakeText(f"({i})  ID = [{videoHistory[str(i)]}]", 20, white, vid_pos, False)
                else:
                    vid_rect = pygame.Rect(0,0,300,30)
                    vid_rect.center = vid_pos
                    pygame.draw.rect(screen, green, vid_rect)
                    MakeText(f"({i})  ID = [{videoHistory[str(i)]}]", 20, white, vid_pos, False)
                    MakeText(">",20,white,(vid_rect.x - 20, vid_rect.centery), not 1==1)

                    if int(str(round(time.time(),1))[-1]) > 5:
                        MakeText("Press [ENTER] to view!",15,yellow,(vid_rect.bottomright[0] + 100, vid_rect.centery), True)
                

                if i == firstIndex + 1:
                    MakeText("OLDEST",20,white,(vid_pos[0] - 250, vid_pos[1]), True)
                elif i == lastIndex:
                    MakeText("NEWEST",20,white,(vid_pos[0] - 250, vid_pos[1]), True)

        MakeText(f"{history_SelectedPage+1} / {history_TotalPages+1}", 30, white, (centerPos[0],screensize[1]-100),2==2) #Show page number

        historyBtn.center = centerPos[0],screensize[1]-50
        if historyBtn.colliderect(cursor):
            pygame.draw.rect(screen,darkYellow,historyBtn)
        else:
            pygame.draw.rect(screen,yellow,historyBtn)
        MakeText("SEARCH USING INDEX", 15, black, historyBtn.center, historyBtn.colliderect(cursor))
        
        for i,btn in enumerate(pageBtns):
            btn.center = centerPos[0] + [-150, 150][i], screensize[1] - 50
            if not btn.colliderect(cursor):
                pygame.draw.rect(screen, green, btn)
            else:
                pygame.draw.rect(screen, darkGreen, btn)
            MakeText(["<",">"][i], 30, black, btn.center, False)
            

        #print(list(videoHistory)[firstItem:lastItem])

    elif page == "historyViewing":
        MakeText("ROULETTE HISTORY", 50, white, (centerPos[0], 50), True)
        if int(str(round(time.time(),1))[-1]) > 5:
            proceedTitle = MakeText("WANNA PROCEED?", 40, yellow, (centerPos[0], 100), True)
            MakeText(f"URL you selected : https://www.youtube.com/watch?v={videoID}", 10, yellow, (proceedTitle.center[0], proceedTitle.center[1]+20), True)
        else:
            proceedTitle = MakeText("WANNA PROCEED?", 40, darkYellow, (centerPos[0], 100), True)
            MakeText(f"URL you selected : https://www.youtube.com/watch?v={videoID}", 10, darkYellow, (proceedTitle.center[0], proceedTitle.center[1]+20), True)
        
        for i, btn in enumerate(history_confirmBtns):
            btn.center = centerPos[0], centerPos[1] - (50,-50)[i]
            if btn.colliderect(cursor):
                pygame.draw.rect(screen, (darkGreen, darkYellow)[i], btn)
            else:
                pygame.draw.rect(screen, (green, yellow)[i], btn)
            MakeText(["YES", "NEVERMIND"][i], 30, [white,black][i],btn.center,btn.colliderect(cursor))

    elif page == "historyIndexSearch":
        MakeText("ROULETTE HISTORY", 50, white, (centerPos[0], 50), True)
        if int(str(round(time.time(),1))[-1]) > 5:
            proceedTitle = MakeText("SEARCH VIA INDEX", 40, yellow, (centerPos[0], 120), False)
        else:
            proceedTitle = MakeText("SEARCH VIA INDEX", 40, darkYellow, (centerPos[0], 120), False)
        
        if len(IndexSearch_input) == 0:
            inputText_rect = MakeText("Type index here...", 30, green, centerPos, False)
        else:
            inputText_rect = MakeText(IndexSearch_input, 30, green, centerPos, False)
        
        colorMSG = {"True":darkYellow, "False":red}[str(time.time() > IS_msg_cooldown)]
        
        MakeText(IndexSearch_msg, 10, colorMSG, (inputText_rect.center[0], inputText_rect.center[1] + 30), False)
        
        if int(str(round(time.time(),1))[-1]) > 5:
            underlineThingy = pygame.Rect(0,0,25,5)
            underlineThingy.bottomleft = inputText_rect.bottomright
            pygame.draw.rect(screen, green, underlineThingy)

        if time.time() > IS_msg_cooldown:
            IndexSearch_msg = "Hit [ENTER] to view video based off the index"
        else:
            IndexSearch_msg = "INVALID INDEX : Index out of range! :("
        

        historyBtn.center = centerPos[0], centerPos[1] + 200
        if historyBtn.colliderect(cursor):
            pygame.draw.rect(screen,darkRed,historyBtn)
        else:
            pygame.draw.rect(screen,red,historyBtn)
        MakeText("CANCEL",30,white,historyBtn.center,historyBtn.colliderect(cursor))
        
    elif page == "settings":
        MakeText("S E T T I N G S", 50, yellow, (centerPos[0], 50), int(str(round(time.time(),1))[-1]) > 5)

        topicConfig_title = MakeText("ROULETTE TOPIC\n[Find random videos based off the topic you chose]\n[Leave black for pure RANDOM topics]", 20, green, (300, centerPos[1]-150), False) #25 px margin from left side of screen
        inputBox = pygame.Rect(0,0,screensize[0]-100,50)
        inputBox.topleft = topicConfig_title.bottomleft[0],topicConfig_title.bottomleft[1] + 20
        pygame.draw.rect(screen,green,inputBox)

        decor_char = {"False":"","True":"_"}[str(int(str(round(time.time(),1))[-1]) > 5 and len(topic_input) < 40 )]

        inputText = pygame.font.SysFont("Consolas", 30).render(topic_input + decor_char,True,white)
        inputText_rect = inputText.get_rect()
        inputText_rect.topleft = inputBox.topleft[0], inputBox.center[1] - (inputBox.size[1]//4)
        screen.blit(inputText,inputText_rect)

        historyBtn.topleft = 25,300

        if len(videoHistory) > 0:
            pygame.draw.rect(screen,{"True":red,"False":darkRed}[str(not historyBtn.colliderect(cursor))],historyBtn)
            MakeText(histErase_msg, 15, black, historyBtn.center, historyBtn.colliderect(cursor))
        else:
            MakeText("NO HISTORY DATA FOUND", 15, red, historyBtn.center, True)

        settingsBtn.topleft = 25,400
        pygame.draw.rect(screen,{"True":green,"False":darkGreen}[str(not settingsBtn.colliderect(cursor))],settingsBtn)
        MakeText("IM DONE!", 30, black, settingsBtn.center, settingsBtn.colliderect(cursor))

    #green line effect thingy
    greenLinePos += 10
    if greenLinePos > screensize[1] + 30*lineCount:
        greenLinePos = 0
    
    for i in range(0,lineCount):
        lineRect =  pygame.Rect(0,0, screensize[0], lineCount - i)
        lineRect.center = centerPos[0], greenLinePos - (i * lineCount) - 30
        if lineRect.centery > (screensize[1] * 4) // 5 or lineRect.centery < screensize[1] // 5:
            pygame.draw.rect(screen, darkGreen, lineRect)
        else:
            pygame.draw.rect(screen, green, lineRect)

    pygame.display.flip()


#i sacrificed my sleep schedule to make ts
