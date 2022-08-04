from calendar import isleap, leapdays, month
from operator import indexOf
from tkinter import CENTER, filedialog as fd
from tkinter import ttk
from tkinter.messagebox import showinfo
import tkinter as tk
import time
import datetime
import webbrowser
import calendar

import shutil
from xml.etree.ElementTree import tostring

# A small note from me if your are looking at the source code.
# If you see anything that could cause my software to fail, please leave a GitHub issue on this repository with the piece of code and the problem!
# This is a program designed to backup files, so it really needs to be bug-free! I've done my best to make it bug-free and I really hope there isn't some major unforeseen problem.
# Thanks, Gitko :)

# A note on how this system works.
# If you set a backup on a leap year before Feb 29th, and let's say you set it to a day after Feb 29th, a day will be subtracted bc of Feb 29th.
# So, say it is Feb 28th and you set a backup in 2 days. It will backup on March 1st rather than March 2nd. If repeat is true, when it backups on March 1st, it will backup on the 3rd.

# Max delay: 1 year
# If y'all want a higher max delay, I can program it but it will need a reworked system because of leap years.

# If you are setting a schedule on Feb 29th, it will set it for Feb 28th.

# shutil used to copy files

root = tk.Tk()
root.title("PyBackup")
root.geometry("520x630")
root.iconbitmap('assets/logo.ico')
     
title = tk.Label(root, text="PyBackup")

directoryToBackup = ''
directoryToBackupTo = ''

override = tk.BooleanVar()
override.set(True)

repeat = tk.BooleanVar()
repeat.set(True)

temp = -1
tempday = 0
tempyear = 0
timeTilCompletion = 0

hour = tk.StringVar()
minute = tk.StringVar()

hour.set('00')
minute.set('00')


def setup(output, error):
    root.geometry("520x630")
    root.resizable(False, False)
    
    openFile = ttk.Button(root, text="Open a Folder to Backup", command=lambda: select_file(1))
    openFile.grid(row=1, column=1)
    
    openFile = ttk.Button(root, text="Open a Folder to Backup To", command=lambda: select_file(2))
    openFile.grid(row=3, column=1)
    
    hourEntry = ttk.Entry(root, width=3, font=("Arial", 18, ""), textvariable=hour)
    hourEntry.grid(row=6, column=1)
    hourText = ttk.Label(root, text='Hours:')
    hourText.grid(row=5, column=1)
    
    minuteEntry = ttk.Entry(root, width=3, font=("Arial", 18, ""), textvariable=minute)
    minuteEntry.grid(row=8, column=1)
    minuteText = ttk.Label(root, text='Minutes:')
    minuteText.grid(row=7, column=1)
    
    submitBackup = ttk.Button(root, text='Submit/Cancel Backup', command=lambda: submitBackupSchedule())
    submitBackup.grid(row=9, column=1)
    
    overrideFiles = ttk.Checkbutton(root, text='Override files', variable=override, onvalue=True, offvalue=False)
    overrideFiles.grid(row=10, column=1)
    
    overrideFiles = ttk.Checkbutton(root, text='Repeat', variable=repeat, onvalue=True, offvalue=False)
    overrideFiles.grid(row=11, column=1)
    
    helpButton = ttk.Button(root, text='Help', command=openHelp)
    helpButton.grid(row=13, column=1)
    
    aboutButton = ttk.Button(root, text='About', command=openAbout)
    aboutButton.grid(row=14, column=1)
    
    warningLabel = ttk.Label(root, wraplength=510, justify=CENTER, text='Please note that this is NOT a perfect piece of software, and it could fail to backup your files or the files may not be backed up properly. I am a pretty new developer, so my software is not the best! Use at your own risk! ', padding=(0,5))
    warningLabel.grid(row=15, column=1)
    
    versionLabel = ttk.Label(root, text='PyBackup v1.0.0', padding=(0,5))
    versionLabel.grid(row=16, column=1)
    
    set_output1(output, error)
    set_output2(output, error)
    set_output3(output, error)
    
    root.after(1000, updateBackupSchedule)

def openHelp():
    helpWindow = tk.Toplevel(root)
    helpWindow.title("PyBackup Help")
    helpWindow.geometry("520x420")
    helpWindow.iconbitmap('assets/logo.ico')
    
    helpWindow.resizable(False, False)
    
    root.helpPhoto = tk.PhotoImage(file='assets/help-photo.png')
    helpPhotoLabel = ttk.Label(helpWindow, image=root.helpPhoto).pack()
    
def openURL(url):
    webbrowser.open_new_tab(url)

def openAbout():
    aboutWindow = tk.Toplevel(root)
    aboutWindow.title("PyBackup About")
    aboutWindow.geometry("520x125")
    aboutWindow.iconbitmap('assets/logo.ico')
    
    aboutWindow.resizable(False, False)
    
    aboutLabelStart = tk.Label(aboutWindow, text="PyBackup v1.0.0\nDeveloped by Chace, aka Gitko").pack()
    
    githubLink = tk.Label(aboutWindow, text="GitHub: https://github.com/Gitko01/pybackup", fg="blue", cursor="hand2")
    githubLink.pack()
    githubLink.bind("<Button-1>", lambda e: openURL("https://github.com/Gitko01/pybackup"))
    
    websiteLink = tk.Label(aboutWindow, text="Website: https://gitko01.github.io/website", fg="blue", cursor="hand2")
    websiteLink.pack()
    websiteLink.bind("<Button-1>", lambda e: openURL("https://gitko01.github.io/website"))
    
    aboutLabelEnd = tk.Label(aboutWindow, justify=CENTER, wraplength=520, text="If you find any bugs or have any feature requests, PLEASE add an issue to the GitHub repository with your suggestions and/or bugs!").pack()


def getTime():
    currentHour = int(time.ctime()[11:13])
    currentMinute = int(time.ctime()[14:16])
    currentSecond = int(time.ctime()[17:19])
    
    currentTimeInSeconds = (currentHour * 3600) + (currentMinute * 60) + currentSecond
    
    return currentTimeInSeconds

def getDayAndYear():
    currentDay = datetime.datetime.now().timetuple().tm_yday
    currentYear = datetime.datetime.now().timetuple().tm_year
    
    # Returns day and year
    return currentDay, currentYear

def getLeapYearDayCount():
    yearDayCount = 365
    
    currentDayOfTheYear = getDayAndYear()[0]
    currentYear = getDayAndYear()[1]
    
    # Day number of February 29th is 60 (ON A LEAP YEAR)
    # This may be false!!! It is an educated guess...
    
    feb29 = 60
    
    leapYear = False
    bfFeb29 = False
    onFeb29 = False
    
    nextYearLeap = False
    nextYearBfFeb29 = False
    
    # Current year
    if calendar.isleap(currentYear):
        leapYear = True
        
    if leapYear and currentDayOfTheYear < feb29:
        bfFeb29 = True
    
    if leapYear and currentDayOfTheYear == feb29:
        onFeb29 = True
    
    # Next year
    if calendar.isleap(currentYear + 1):
        nextYearLeap = True
    
    if nextYearLeap and tempday < feb29:
        nextYearBfFeb29 = True
    
    #--------------
    
    if bfFeb29 and leapYear:
        # 366 days
        yearDayCount = 366
    elif bfFeb29 == False and leapYear:
        # 365 days
        yearDayCount = 365
    
    # If you are setting a schedule on Feb 29th, it will set it for Feb 28th.
    if leapYear and onFeb29:
        # 364 days
        yearDayCount = 364
    
    if nextYearBfFeb29 and nextYearLeap:
        # 365 days
        yearDayCount = 365
    elif nextYearBfFeb29 == False and nextYearLeap:
        # 366 days
        yearDayCount = 366
    
    return yearDayCount

def submitBackupSchedule():
    global temp
    global tempday
    global tempyear
    global directoryToBackupTo
    global directoryToBackup
    
    global timeTilCompletion
    
    if timeTilCompletion > 0:
        set_output3('Backup schedule canceling...', True)
        temp = -2
        
        return
    
    try:
        int(minute.get())
        int(hour.get())
    except:
        set_output3('The hour or minute value needs to be a number!', True)
        return
    
    if int(minute.get()) <= 0 and int(hour.get()) <= 0:
        set_output3('The hour or minute value needs to be set to at least 1!', True)
        return

    if int(minute.get()) < 0 or int(hour.get()) < 0:
        set_output3('The hour or minute value needs to be set to at least 1!', True)
        return
    
    if directoryToBackup == '' and directoryToBackupTo == '':
        set_output3('Directory to backup or directory to backup to is blank!', True)
        return

    try:
        # print(time.ctime()[11:13]) hour
        # print(time.ctime()[14:16]) min
        # print(time.ctime()[17:19]) sec
        
        currentTimeInSeconds = getTime()
        currentDayOfTheYear = getDayAndYear()[0]
        currentYear = getDayAndYear()[1]
        
        temp = currentTimeInSeconds + int(hour.get())*3600 + int(minute.get())*60
        tempday = currentDayOfTheYear
        tempyear = currentYear

        
        # Temp = current time of day + hours and minutes set (So, 5:00 pm for example)
        # Tempday is current day of year (So, Jan 25th for example)
        # Tempyear is current year (So, 2022 for example)
        
        # Basically temp, temp day, and temp year is the time the backup should run.
        
        while temp >= 86400:
            temp -= 86400
            tempday += 1
        
        delayTooLong = False
        
        yearDayCount = getLeapYearDayCount()
        
        if tempday > yearDayCount:
            
            tempday -= yearDayCount
            tempyear += 1
            
            if tempday > currentDayOfTheYear:
                delayTooLong = True
                temp = -3
                updateBackupSchedule()
                    
        if delayTooLong == False:
            updateBackupSchedule()
            
            
    except Exception as err:
        set_output3('Failed to submit backup. This should never happen...  error: ' + str(err), True)
    
    
def updateBackupSchedule():
    global temp
    global tempday
    global tempyear
    global override
    global timeTilCompletion
    
    if temp == -2:
        set_output3('Backup canceled!', True)
        timeTilCompletion = 0
        return
    
    if temp == -3:
        set_output3('Backup canceled! Ensure your backup delay is less than one year.', True)
        timeTilCompletion = 0
        return

    if temp == -1:
        return
    
    timeTilCompletion = temp - getTime()
    
    if tempday > getDayAndYear()[0]:
        dayDif = tempday - getDayAndYear()[0]
        dayDifInSec = dayDif * 86400
        
        timeTilCompletion = (temp + dayDifInSec) - getTime()      
    
    if tempyear > getDayAndYear()[1]:
        # If Feb28th on a leap year and scheduled for 365 days, it should be 366 days til completion.
        # If Feb28th on a leap year and scheduled for 366 days, it should be 367 days til completion.
        dayDif = 0
        dayDifInSec = 0
        
        if tempday > getDayAndYear()[0]:
            dayDif = tempday - getDayAndYear()[0]
            dayDifInSec = dayDif * 86400
            
        elif tempday == getDayAndYear()[0]:
            if getLeapYearDayCount() == 366:
                dayDif = 1
                dayDifInSec = 86400
        
        yearDayCount = getLeapYearDayCount()
        
        timeTilCompletion = (temp + (yearDayCount * 86400) + dayDifInSec) - getTime()
        
    
    timeTilCompletionStr = str(datetime.timedelta(seconds=timeTilCompletion))
    
    correctDay = True
    correctYear = True
    
    if tempyear > getDayAndYear()[1]:
        correctYear = False
    
    if tempday > getDayAndYear()[0]:
        correctDay = False
     
    if getTime() >= temp and correctDay and correctYear:
        set_output3('BACKING UP FILES', False)
        
        try:    
            shutil.copytree(directoryToBackup, directoryToBackupTo, ignore=None, ignore_dangling_symlinks=False, symlinks=True, dirs_exist_ok=override)
            
        except Exception as err:
            set_output3('Failed to backup directory... err: ' + str(err), True)
            
            return
        
        set_output3('Backup finished on ' + str(time.ctime()[0:10]) + ' at ' + str(time.ctime()[11:20]), False)
        
        if repeat.get() == True:
            submitBackupSchedule()

        return
         
    set_output3('Dir to backup: ' + directoryToBackup + ', Dir to be backed up to: ' + directoryToBackupTo + ', Override: ' + str(override.get()) + ', Repeat: ' + str(repeat.get()) + ', Time left: ' + timeTilCompletionStr, False)
    
    root.after(1000, updateBackupSchedule)
    
    
    
def set_output1(text, error):
    for widget in root.winfo_children():
        if 'output1Text' in widget.winfo_name():
            widget.destroy()
        else:
            pass
        
    output1Text = tk.Text(root, height = 3, width = 65, name='output1Text')
    output = text
 
    if error == True:
        output1Text.config(fg="red")
    
    output1Text.grid(row=2, column=1)
    
    output1Text.insert(tk.END, output)
    output1Text.config(state=tk.DISABLED)
    

def set_output2(text, error):
    for widget in root.winfo_children():
        if 'output2Text' in widget.winfo_name():
            widget.destroy()
        else:
            pass
    
    output2Text = tk.Text(root, height = 3, width = 65, name='output2Text')
    output = text
    
    if error == True:
        output2Text.config(fg="red")
    
    output2Text.grid(row=4, column=1)
    
    output2Text.insert(tk.END, output)
    output2Text.config(state=tk.DISABLED)

def set_output3(text, error):
    for widget in root.winfo_children():
        if 'output3Text' in widget.winfo_name():
            widget.destroy()
        else:
            pass
    
    output3Text = tk.Text(root, height = 10, width = 60, name='output3Text')
    output = text
    
    if error == True:
       output3Text.config(fg="red")
    
    output3Text.grid(row=12, column=1)
    
    output3Text.insert(tk.END, output)
    output3Text.config(state=tk.DISABLED)

def select_file(output):
    
    dirname = fd.askdirectory(
        title='Open the folder you wish to backup',
        initialdir='/')
    
    if dirname == "":
        set_output1("no directory selected", True)   
        return

    showinfo(
        title='Selected Directory',
        message=dirname
    )
    
    global directoryToBackup
    global directoryToBackupTo
    
    if output == 1:
     
        if dirname == directoryToBackupTo:
            set_output1("Directory same as directory to backup to!",True)
            
            return
        
        try:
            set_output1(dirname, False)
            directoryToBackup = dirname
                
        except Exception as err:
            set_output1("Directory could not be set... error: \n\n" + str(err),True)
            
            return
    else:
     
        if dirname == directoryToBackup:
            set_output2("Directory same as directory to backup!",True)
            
            return
        
        try:
            set_output2(dirname, False)
            directoryToBackupTo = dirname
            
            directoryToBackupTo = directoryToBackupTo + "/backup"
                
        except Exception as err:
            set_output2("Directory could not be set... error: \n\n" + str(err),True)
            
            return
    
setup("", False)
root.mainloop()
