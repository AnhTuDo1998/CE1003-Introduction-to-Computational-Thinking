#####Improvements V.5.0
#1. Add in error handling for wrong index group (Done by Jesslyn already lmao)
#2. Add in Converter and script for converting our csv to ics file (1 - variable declare
#3. Fix error in switching tab ([-1] to always select newest window or tab)
#4. Slow computer solved by wait implicitly 5s, can adjust to other time if needed.
#5 Problem worth solving : How to send file via telegram, how to restart the program after the user is finish and keep it for next user ?
#6 Resolve issue of other modules than SCSE
#7 Fixed send Document
import sys
sys.path.append('.')
sys.path.append('../')
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException 
import numpy as np
import csv
from datetime import datetime, timedelta
from convert import Convert

# 1. Naming and Setting Variables
###########################################################################
ModulesData = []                                    # To contain every module timetable in list format
ModulesName = []                                    # To contain the names of modules
ClassIndexName = []

# Set all flags to false
def reset_flags():
    global getCal_flag, CourseCode_flag, CheckCourse_flag, ClassIndex_flag,\
           ExtraOptions_flag, Remove_flag, Generate_flag
    getCal_flag = CourseCode_flag = CheckCourse_flag = ClassIndex_flag =\
                  ExtraOptions_flag = Remove_flag = Generate_flag = False

reset_flags()                                       # Ensure all flags are initialized and set to false

#Initializing Converter for CSV to ICS file,
#each variable equivalent to a column in the csv file generated
convert = Convert()
convert.CSV_FILE_LOCATION = 'calendar.csv'
convert.SAVE_LOCATION = 'calendar.ics'
convert.HEADER_COLUMNS_TO_SKIP = 0

convert.NAME = 0
convert.START_DATE = 2
convert.END_DATE = 4
convert.DESCRIPTION = 6
convert.LOCATION = 7

# 2. Telebot Functions A
###########################################################################

# For every message through telegram, it gets filter out here (according to message type)
def handle(msg):
    global content_type, chat_type, chat_id, flavor
    global ExtraOptions_markup
    flavor = telepot.flavor(msg)
    content_type, chat_type, chat_id = telepot.glance(msg, flavor=flavor)
    summary = (flavor, content_type, chat_type, chat_id )
    print (summary)
    ExtraOptions_markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Add modules', callback_data='ADD')],
                        [InlineKeyboardButton(text='Remove modules', callback_data='REMOVE')],
                        [InlineKeyboardButton(text='Check modules', callback_data='CHECK')],
                        [InlineKeyboardButton(text='Continue and retrieve ICal', callback_data='CONTINUE')]
                        ])

    if flavor == "chat":
        on_chat_message(msg)

    elif flavor == "callback_query":
        on_callback_query(msg)

    else:
        return

def on_chat_message(msg):
    global getCal_flag, CourseCode_flag, CheckCourse_flag, ClassIndex_flag,\
           ExtraOptions_flag, Remove_flag, Generate_flag
    global Selenium_Extraction
    global ModulesName, ModulesData, ClassIndexName
    
    #Step 0: "/start" command to introduce bot to user
    if msg["text"] == "/start":
        bot.sendMessage(chat_id, """ Hello there! I am ICalBot, and I am here to simplify your life in NTU.
        You can use me to retrieve an electronic calendar for Your Modules (You will need to give me your course code and group index) or NTU Key Events. 
        To begin, type or click /getCal """)
        reset_flags()

    #Step 1: "/getCal" command for options of ICal
    elif msg["text"] == "/getCal":
        getCal_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Get ICal for Specific Course(s)', callback_data='Course')],
            [InlineKeyboardButton(text='Get ICal for NTU Key Events', callback_data='NTUEvent')]
            ])
        message_with_inline_keyboard = bot.sendMessage(chat_id, "Which ICal would you like to generate?", reply_markup=getCal_markup)
        reset_flags()
        getCal_flag= True

    #Step 3: After receiving Course Code, check whether the retrieved data is correct
    elif CourseCode_flag == True:
        bot.sendMessage(chat_id, "Please wait for moment, this may take awhile...")
        CourseInput = msg["text"]
        Selenium_Extraction = timetable_extract(CourseInput)
        if Selenium_Extraction == False:
            bot.sendMessage(chat_id, "Can't find your course. Please retry: ")
            reset_flags()
            CourseCode_flag = True
        else:
            bot.sendMessage(chat_id, Selenium_Extraction[0])
            YesNo_markup = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text='Yes', callback_data='Y')],
                [InlineKeyboardButton(text='No', callback_data='N')]
                ])
            bot.sendMessage(chat_id, "Is this the course you are looking for? (Yes/No)", reply_markup=YesNo_markup)
            reset_flags()
            CheckCourse_flag = True


    #Step 5: After class index input, get timetable and extra options(Add,Remove,Output)
    elif ClassIndex_flag == True:
        try:
            ClassInput = msg["text"]
            timetable_extract2(Selenium_Extraction[1], ClassInput)
            bot.sendMessage(chat_id, (Selenium_Extraction[0] + " Added."))
            bot.sendMessage(chat_id, "Would you like to:", reply_markup=ExtraOptions_markup)
            ClassIndexName.append(ClassInput)
            print (ModulesData,ModulesName,ClassIndexName)
            reset_flags()
            ExtraOptions_flag = True
        except:
            bot.sendMessage(chat_id, "Can't find your class index. Please retry: ")
            reset_flags()
            ClassIndex_flag = True

def on_callback_query(msg):
    global getCal_flag, CourseCode_flag, CheckCourse_flag, ClassIndex_flag,\
           ExtraOptions_flag, Remove_flag, Generate_flag
    global ModulesName, ModulesData, ClassIndexName

    if getCal_flag == True:
    #Step 2a: Choosing option for getting course ICal => input CourseCode
        if chat_id == "Course":
            bot.sendMessage(chat_type, "Please enter your course code/name:")
            reset_flags()
            CourseCode_flag = True
        
    #Step 2b: Choosing option for getting ntu general ICal [End]
        elif chat_id == "NTUEvent":
            bot.sendMessage(chat_type, """All ICal for NTU Key Events are available on this website:
            http://www.ntu.edu.sg/Students/Undergraduate/AcademicServices/AcademicCalendar/Pages/AY2016-17.aspx """)
            reset_flags()

    elif CheckCourse_flag == True:
        #Step 4a: If course is correct, get class index input
        if chat_id == "Y":
            bot.sendPhoto(chat_type, open('class_index.png', 'rb'))
            bot.sendMessage(chat_type, "Please enter your class index:")
            reset_flags()
            ClassIndex_flag = True

        #Step 4b: IF course is wrong, get another course input    
        if chat_id == "N":
            bot.sendMessage(chat_type, "Please enter your CORRECT course code:")
            ModulesName = ModulesName[:-1]
            reset_flags()
            CourseCode_flag = True

    elif ExtraOptions_flag == True:
        #Step 6a: ADD more modules
        if chat_id == "ADD":
            bot.sendMessage(chat_type, "Please enter your course code/name:")
            reset_flags()
            CourseCode_flag = True

        #Step 6b: REMOVE modules
        if chat_id == "REMOVE":
            markup_code = "InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Return', callback_data='NONE')],"
            modulecounter = 0
            for Modules in ModulesName:
                code_segment = "[InlineKeyboardButton(text='{}', callback_data='{}')],".format(Modules,modulecounter)
                markup_code = markup_code + code_segment
                modulecounter += 1
            markup_code = markup_code[:-1] + "])"
            markup_code = eval (markup_code)
            bot.sendMessage(chat_type, "Which module would you like to remove?", reply_markup=markup_code)
            reset_flags()
            Remove_flag = True
            
        #Step 6c: Check Modules in list  
        if chat_id == "CHECK":
            ModuleNumber = len(ModulesName)
            for N in range(0,ModuleNumber):
                bot.sendMessage(chat_type, ("{} [Group index:{}]".format(ModulesName[N],ClassIndexName[N])))
            bot.sendMessage(chat_type, "Would you like to:", reply_markup=ExtraOptions_markup)
            reset_flags()
            ExtraOptions_flag = True
            
        #Step6d : Export ICal
        if chat_id == "CONTINUE":
            global ModulesData
            bot.sendMessage(chat_type, "Please wait for moment, this may take awhile...")
            document = ICal_Generator(ModulesData)
            bot.sendDocument(chat_type, open('calendar.ics'))
            bot.sendMessage(chat_type, "Here is the ICal you wanted! If you want to obtain a different ICal, click or type /getCal")
            reset_flags()
            Generate_flag = True

    #Step6bi : After Remove Module   
    elif Remove_flag == True:
        if chat_id == "NONE":
            bot.sendMessage(chat_type, "Would you like to:", reply_markup=ExtraOptions_markup)
            reset_flags()
            ExtraOptions_flag = True
        else:
            mod_number = int(chat_id)
            bot.sendMessage(chat_type, (ModulesName[mod_number] + " Removed."))
            del(ModulesData[mod_number])
            del(ModulesName[mod_number])
            del(ClassIndexName[mod_number])
            bot.sendMessage(chat_type, 'Would you like to:', reply_markup=ExtraOptions_markup)
            reset_flags()
            ExtraOptions_flag = True

# 3. Selenium Function
################################################################################################
#Step 3: Retrieve Course Timetable with selenium
def timetable_extract(Courseinput):
    global ModulesName
    # Problem 1: driver not working (Issue of path of driver)
    driver = webdriver.PhantomJS()                                             # Run chrome
    driver.implicitly_wait(5)
    driver.get("https://wish.wis.ntu.edu.sg/webexe/owa/aus_schedule.main")  # Chrome go to website
    
    #@@@@assert "Class Schedule" in driver.title@@@@@@@@@                   ## Check correct website

    Keyword = driver.find_element_by_name("r_subj_code")                    # Find the element for inputting course code
    Keyword.send_keys(Courseinput)                                          # Input Userinput to element found
    driver.find_element_by_xpath('//input[4]').click()                      # Find and select the "Enter" button
    # Problem 2: Enter the values was an issue, button was assigned an input value so cannot use 'select'

    # Switching Tabs:
    driver.implicitly_wait(5)                                               #Slow computer problem
    tabs = driver.window_handles                                            # Get list for all tab names
    driver.switch_to_window(tabs[-1])                                        # Switch to 2nd tab 
    #print (driver.current_url)                                             ## Check the focus tab is correct
    driver.save_screenshot('class_index.png')
    #@@@@@assert "Class Schedule" in driver.title@@@@@@@
    try:
        Retrieved_Course = driver.find_element_by_tag_name("tbody")             # Find the course code and name obtained
        Retrieved_Course = (Retrieved_Course.text)
        ModulesName.append(Retrieved_Course)                                    # Add course name to MAIN LIST

        Alltext = []                                                            # Create empty set
        tablecontents = driver.find_elements_by_xpath("/html/body/center/table[2]/tbody/tr/td")                  # Find element of "INDEX, TYPE, GROUP, DAY, TIME, VENUE, REMARK"

        for elements in tablecontents:                                          # Find each string:
            elements = elements.text                                            # Convert the retrieved element to text form
            Alltext.append(elements)                                            # Input all text into an array
        print(Alltext)                                                      
        print(Alltext)                                                          ## Check that list is correct

        driver.quit()                                                           # End selenium
        Selenium_Extraction = [Retrieved_Course, Alltext]
        return Selenium_Extraction
    except:
        driver.quit()
        return False
    
def timetable_extract2(Alltext,Classinput):
    global ModulesData, ModulesName
    length = len(Alltext)                           # To obtain total no. of elements in array
    subsetno = length / 7                           # Find total no. of rows
    Alltext = np.array(Alltext)
    Table = Alltext.reshape(int(subsetno),7)        # Create a "table" format of x rows and 5 columns
    newlist = []                                    # Create an empty set for valid rows only, aka "newlist"
    finallist = []

    # filter top half
    for row in Table:
        if (row[0] != Classinput):
            Table = np.delete(Table,[0],0)
        elif (row[0] == Classinput):
            break
    
    newlist.append(Table[0])                        # Move the first row to "newlist"

    # filter bottom half
    for row in Table[1:]:                               # Check EACH row
        if (row[0] == ""):                          # If first column is empty, then carry out:
            newlist.append(row)                     # Move row to "newlist"
        elif (row[0] != ""):                        # If first colum is not empty, stop loop
            break

    for rows in newlist:
        rows[0] = newlist[0][0]
        TIME = rows[4]
    
        TIME = TIME.split("-")
        StartTime = TIME[0]
        StartTime = str(StartTime[0:2]) + ":" + str(StartTime[2:4])
        EndTime = TIME[1]
        EndTime = str(EndTime[0:2]) + ":" + str(EndTime[2:4])

        rows = np.delete(rows, 4)
        rows = np.insert(rows, 4, EndTime)
        rows = np.insert(rows, 4, StartTime)
        finallist.append(rows)
        
    #print(finallist)                                  ## Check that "newlist" is correct
    ModulesData.append(finallist)

# ICAL Generator
#################################################################################################################
def ICal_Generator(finallist):
    for list in finallist:
        First_monday = "14/8/2017" #supposed to be input value from telegram
        dcol = 0 #initial column (course code)
        wk = 0 #including recess wk as wk 6
        total_wks = 13 #to equate to the input of button, if special term thn 5, norm is 13

        #open calendar.csv file
        with open("calendar.csv", "w") as c:
            headers = ("Subject", "StartDate", "StartTime", "EndDate", "EndTime", "AllDayEvent", "Description", "Location")
            writer = csv.DictWriter(c, fieldnames = headers)
            writer.writeheader()
    
        #write data into calendar.csv file
            for row in list:
            
                #define variables here
                subject = row[0]                #subject located at this current row and first column
                starttime = row[4]              #start time located at this current row and column 5th
                endtime = row[5]                #end time located at this current row and column 6th
                alldayevent = "False"           #all day event is set to false
                description = " Type: %s \n Group: %s \n %s" %(row[1],row[2],row[7]) #type of lession and group number is located at 2nd, 3rd, 8th column
                location = row[6]               #location located at this current row and 7th column
        
                #----assigning values to days of wk and changing date accordingly ----#  
                if(row[3] == str("MON")):
                    b = 0
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))

                elif(row[3] == str("TUE")):
                    b = 1
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))

                elif(row[3] == str("WED")):
                    b = 2
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))

                elif(row[3] == str("THU")):
                    b = 3
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))
                
                elif(row[3] == str("FRI")):
                    b = 4
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))
                ### What about lesson on weekend?
                #----assigning values to days of wk and changing date accordingly ---- #

                #----while loop to print/insert all possible dates into array----#
                dates_list = [date]

                for wk in range(0,13):
                    if(wk != 6):
                        date = datetime.strptime(date,'%m/%d/%Y') + timedelta(days=7)
                        date = str(datetime.strftime(date, '%m/%d/%Y'))
                        dates_list.append(date)
                        print(dates_list)
                    else:
                        date = datetime.strptime(date,'%m/%d/%Y') + timedelta(days=14)
                        date = str(datetime.strftime(date, '%m/%d/%Y'))
                        dates_list.append(date)
                        print(dates_list)


        
                #----while loop to print/insert all possible dates into array----#
                for dcol in range(0,13):
                    start_end_date = dates_list[dcol]
                    writer.writerow({"Subject" : subject, "StartDate" : start_end_date , "StartTime" : starttime , \
                                     "EndDate" : start_end_date , "EndTime" : endtime , "AllDayEvent" : alldayevent , \
                                     "Description" : description, "Location" : location })


        convert.read_csv()
        print (convert.csv_data)

        i = 0
        while i < len(convert.csv_data):
            row = convert.csv_data[i]
            start_date = str(row[1]) + '-'+ str(row[convert.START_DATE])
            end_date = str(row[1]) + '-' + str(row[convert.END_DATE])
            try:
                row[convert.START_DATE] = datetime.strptime(start_date, '%m/%d/%Y-%H:%M')
                row[convert.END_DATE] = datetime.strptime(end_date, '%m/%d/%Y-%H:%M')
                i += 1
                #print("Added something")            #Debug print test
            except:
                convert.csv_data.pop(i)
                #print('popped')                     #Debug print test
            row[convert.NAME] = 'Class '+row[convert.NAME]

        convert.make_ical()
        #print (convert.cal)                        #Debug check for ical file
        convert.save_ical()

# Telebot Function 2
################################################################################################
Token = "388718978:AAEUppjISCz8eVq_j3b8owag04-E95y1PRk"             # Token from command line
bot = telepot.Bot(Token)
MessageLoop(bot, handle).run_as_thread()

print ('Listening ...')

while 1:                                                            # Keep the program running.
    time.sleep(10)
