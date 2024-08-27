#Dylan Dang Lab 3
#lab3front

import urllib.request as ur
import requests
from bs4 import BeautifulSoup 
import re
import time
import pickle
import json
import sqlite3
import tkinter as tk


class DisplayWin(tk.Toplevel) :
    def __init__(self, master, destName, destText) :
        super().__init__(master)

        self.grab_set()
        self.configure(bg="Maroon")

        #Create and display destination name label
        self._destLabel = tk.Label(self, text=destName, fg="white", bg="Maroon")
        self._destLabel.pack(pady=5)


        #Create and display description label
        self._descTextLabel = tk.Label(self, text=destText, fg="white", bg="black", wraplength=200)
        self._descTextLabel.pack(pady=5, padx=10)




class ResultWin(tk.Toplevel) :
    def __init__(self, master, mode, search, places) :
        super().__init__(master)

        self._search = search
        self.grab_set()
        self.configure(bg="Maroon")

        #Query SQL Data for choices
        self._conn = sqlite3.connect('travels.db')
        self._cur = self._conn.cursor()


        #Create head label and display
        if mode == "month" :
            self._headLabel = tk.Label(self, text=f"Top destinations for {self._search.capitalize()} in ranking order")
            self._headLabel.pack(pady=2)
        elif mode == "rank" :
            self._headLabel = tk.Label(self, text=f"Destinations with rank {self._search} for the listed months")
            self._headLabel.pack(pady=2)
        else :
            self._headLabel = tk.Label(self, text=f"Destinations starting with {self._search}")
            self._headLabel.pack(pady=2)

        
        self.createListBox(places)


    def createListBox(self, places) :
        '''Create listbox of destinations'''

        self._LB = tk.Listbox(self)

        #Create each element in listbox accordingly
        for place in places :
            res = ' '.join(map(str, place))
            self._LB.insert(tk.END, res)
        
        #Bind listbox to command, display listbox
        self._LB.bind('<<ListboxSelect>>', lambda event: self.openDisplayWin(self._LB.curselection()[0], places))
        self._LB.pack(pady=5)
    

    def openDisplayWin(self, ind, places) :
        '''Open display window of given place'''
        place = places[ind]
        destName = place[1] if isinstance(place[0], int) else place[0]

        self._cur.execute('''SELECT desc FROM Travels WHERE name = ?''', (destName,))
        self._descText = self._cur.fetchall()

        #Create windows for each description
        for desc in self._descText :
             DisplayWin(self, destName, desc[0])


class DialogWin(tk.Toplevel) :
    def __init__(self, master, type) :
        super().__init__(master)

        #Set background color and create header label
        self.configure(bg="Maroon")
        self._headerLabel = tk.Label(self, text=f"Click on {type} to select", fg="white", bg = "Maroon")
        self._headerLabel.pack(pady=5)
        self.grab_set()

        #Variable to keep track of what button is , list of radiobuttons
        self._controlVar = tk.IntVar()
        self._rb_list = []

        #Query SQL Data for choices
        self._conn = sqlite3.connect('travels.db')
        self._cur = self._conn.cursor()

        #Call method based on type accordingly
        if (type == "month"):
            self.displayMonthRadios()
        elif (type == "rank") :
            self.displayRankRadios()
        else :
            self.displayNameRadios()


        
    def displayMonthRadios(self) :
        ''' Creates radio buttons for each month of database'''
        #Fetch data
        self._cur.execute('SELECT month FROM Months')
        all_list = self._cur.fetchall()

        #Create and display buttons
        for ele in enumerate(all_list) :
            rb = tk.Radiobutton(self, text=ele[1][0].capitalize(), variable=self._controlVar, value=ele[0], fg="white", bg="Maroon", command=lambda :self.openResWin("month", all_list[self._controlVar.get()][0]))
            rb.pack(pady=2.5)
            self._rb_list.append(rb)

    def displayRankRadios(self) :
        ''' Creates radio buttons for each of the ranks within database'''

        #Fetch data
        self._cur.execute('SELECT rank FROM Travels')
        all_list = sorted(set(self._cur.fetchall()))

        #Create and display buttons
        for ele in enumerate(all_list) :
            num = int(ele[1][0])
            rb = tk.Radiobutton(self, text=num, variable=self._controlVar, value=ele[0], fg="white", bg="Maroon", command= lambda: self.openResWin("rank", self._controlVar.get() + 1))
            rb.pack(pady=2.5)
            self._rb_list.append(rb)
        

    def displayNameRadios(self) :
        ''' Creates radio buttons for each starting letter of destinations within database'''

        #Fetch data
        self._cur.execute('SELECT name FROM Travels')
        names = self._cur.fetchall()

        #Get first letter of each destination, store accordingly
        letters = set()
        for name in names:
            letters.add(name[0][0].upper())
        letters = list(sorted(letters))
        
        #Create and display buttons
        for ele in enumerate(letters) :
            rb = tk.Radiobutton(self, text=ele[1], variable=self._controlVar, value=ele[0], fg="white", bg="Maroon", command= lambda: self.openResWin("name", letters[self._controlVar.get()]))
            rb.pack(pady=2.5)
            self._rb_list.append(rb)


    def openResWin(self, mode, search):
        #Display Result window and destroy
        self._mode = mode
        self._search = search
        self.destroy()
    

    '''Getters'''

    def getMode(self) :
        return self._mode
    
    def getSearch(self) :
        return self._search







class MainWin(tk.Tk) :
    def __init__(self):
        super().__init__()


        #For querying SQL Data
        self._conn = sqlite3.connect('travels.db')
        self._cur = self._conn.cursor()
        
        #Set title and create title label
        self.configure(bg="coral")
        self.title("Travel")
        self._titleLabel = tk.Label(self, text="Best Places to Travel in 2024", fg="FireBrick", bg = "coral")
        self._titleLabel.pack(pady=10)

        #Create the search by text label and the three rank buttons
        self._searchByLabel = tk.Label(self, text="Search by", fg="FireBrick", bg="Coral")
        self._searchByLabel.pack(pady=5, side="left")
        
        self._rankButton = tk.Button(self, text="Rank", fg="Maroon", command=self.displayRank)
        self._rankButton.pack(side="right")

        self._monthButton = tk.Button(self, text="Month", fg="Maroon", command=self.displayMonth)
        self._monthButton.pack(side="right")

        self._nameButton = tk.Button(self, text="Name", fg="Maroon", command=self.displayName)
        self._nameButton.pack(side="right")


    def displayRank(self) :
        '''Open Dialog window displaying the different ranks, once selected displays result window'''

        self._dWin = DialogWin(self, "rank")
        self.wait_window(self._dWin)
        self.searchRanks(self._dWin.getMode(), self._dWin.getSearch())

    def displayMonth(self) :
        '''Open Dialog window displaying the different months, once selected displays result window'''

        self._dWin = DialogWin(self, "month")
        self.wait_window(self._dWin)
        self.searchMonths(self._dWin.getMode(), self._dWin.getSearch())


    def displayName(self) :
        '''Open Dialog window displaying the different starting letters, once selected displays result window'''

        self._dWin = DialogWin(self, "letter")
        self.wait_window(self._dWin)
        self.searchNames(self._dWin.getMode(), self._dWin.getSearch())


    def searchRanks(self, mode, search) :
        '''Query and fetch destinations that fall have searched rank'''


        #Query data accordingly
        self._cur.execute('''SELECT name FROM Travels WHERE rank = ?''',(search,))
        ResultWin(self, mode, search, sorted(self._cur.fetchall()))


    def searchMonths(self, mode, search):
        '''Query and fetch destinations that fall under searched month'''

        #Query data accordingly
        self._cur.execute('''SELECT T.rank, T.name 
                          FROM Travels T 
                          JOIN Months M ON T.monthID = M.mID 
                          WHERE M.month = ?''',(search,))
        ResultWin(self, mode, search, sorted(self._cur.fetchall()))

    

    def searchNames(self, mode, search) :
        '''Query and fetch destinations with names that start with searched letter'''

        #Query data accordingly
        self._cur.execute('''SELECT name FROM Travels''')
        searchList = list(set(sorted([name for name in self._cur.fetchall() if name[0][0] == search])))
        ResultWin(self, mode, search, searchList)





app = MainWin()
app.mainloop()