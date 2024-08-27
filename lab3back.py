#Dylan Dang Lab 3
#lab3back

import urllib.request as ur
import requests
from bs4 import BeautifulSoup 
import re
import time
import pickle
import json
import sqlite3

'''PART A'''
'''
#Get link name
rootURL = 'https://www.timeout.com'
linkName = rootURL + '/things-to-do/best-places-to-travel'
page = requests.get(linkName)


soup = BeautifulSoup(page.content, "lxml")
tags = soup.select('main section._main_content_1p4mq_7 div article.tile._article_142mc_1 a._imageLinkContainer_142mc_9')

destData = []

#Use soup to parse data and store it accordingly
for tag in tags:
    monthURL = rootURL + tag['href']
    monthPage = requests.get(monthURL)
    monthSoup = BeautifulSoup(monthPage.content, "lxml")

    curMonth = monthURL.rsplit('-')[-1].lower()
    ranks = monthSoup.select('main article.tile._article_kc5qn_1 h3._h3_cuogz_1 span')
    destNames = monthSoup.select('main article.tile._article_kc5qn_1 h3._h3_cuogz_1')
    descTexts = monthSoup.select('main article.tile._article_kc5qn_1 div._summary_kc5qn_21')

    for rank, destName, descText in zip(ranks, destNames, descTexts) :

        #Add data to dataset
        realRank = int(rank.text.strip("."))
        realDesc = descText.text.encode("ascii", "ignore").decode("ascii").strip().split("\n")[0]
        name = destName.text.encode("ascii", "ignore").decode("ascii").split(".")[1]
    
        destData.append((name, realRank, curMonth, realDesc))

#Dump data into json file
with open('travel_data.json', 'w') as f:
    json.dump(destData, f, indent=3);

'''

'''PART B'''

#Connect to database
conn = sqlite3.connect('travels.db')
cur = conn.cursor()

#Create Month table
cur.execute("DROP TABLE IF EXISTS Months")
cur.execute('''CREATE TABLE Months (
            mID INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL UNIQUE ON CONFLICT IGNORE
            )''')

#Create Travels table
cur.execute("DROP TABLE IF EXISTS Travels")
cur.execute('''CREATE TABLE Travels(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    monthID INTEGER NOT NULL,
                    desc TEXT,
                    FOREIGN KEY (monthID) REFERENCES Months (mID)
            )''')


#Read json file, store data accordingly
with open('travel_data.json', 'r') as f :
    travelsData = json.load(f)
    
    #For each place, store its data in database
    for place in travelsData :
        cur.execute("INSERT INTO Months (month) VALUES (?)", (place[2],))
        cur.execute("SELECT mID FROM Months WHERE month = ? ", (place[2],))
        month_id = cur.fetchone()[0]

        cur.execute('''INSERT INTO Travels
                    (name, rank, monthID, desc) 
                    VALUES (?, ?, ?, ?)''', (place[0], place[1], month_id, place[3]))


conn.commit()
conn.close()











