#########################################################################
#### NTU ICalendar Bot
# Function: By providing the user course code and class index, the bot will
#           an ICalendar
# Steps :
# 1.
# Limitation:
# 1) The bot can only work on this Semester
#Improvements: Working for other modules from other schools (like LG9001)
#########################################################################

import sys
import os
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
# Variables for Modules Name,Timetable,index group of every user respectively
ModulesData = []                                    
ModulesName = []                                   
ClassIndexName = []
# List that consists of names of all flags (flag are to ensure code runs in order)
All_flags = ["getCal_flag", "CourseCode_flag", "CheckCourse_flag", "ClassIndex_flag",\
             "ExtraOptions_flag", "Remove_flag", "Generate_flag"]
# Ensure all flags are initialized and empty
for flag in All_flags:
    set_empty = flag + " = []"
    exec (set_empty)


#2. Telebot Functions A
###########################################################################
#To identify which part of the list is the user data located
def UserData(index_UD):
    global ModulesName, ModulesData, ClassIndexName
    for UserModulesName_UD in ModulesName:                 # ModulesName can be replace with ModulesData                        
        counter_UD = 0
        if UserModulesName_UD[0] == index_UD:
            break
        else:
            counter_UD += 1
    return counter_UD

# Set all flags with a specific chat_id to empty
def reset_flags(index_RS):
    global getCal_flag, CourseCode_flag, CheckCourse_flag, ClassIndex_flag,\
           ExtraOptions_flag, Remove_flag, Generate_flag
    index_RS = int(index_RS)
    for flag_RS in All_flags:
        flag_type_RS = eval(flag_RS)
        if index_RS in flag_type_RS:
            command_RS = flag_RS + ".remove(index_RS)"
            eval (command_RS)
            
    

# To remove any data on modules for each user
def reset_data(chat_id_RD):
    global ModulesName, ModulesData, ClassIndexName
    try:
        index_RD = UserData(chat_id_RD)
        del(ModulesName[index_RD])
        del(ModulesData[index_RD])
        del(ClassIndexName[index_RD])
        print(ModulesName[index_RD], ModulesData[index_RD], ClassIndexName[index_RD])
        ModulesName.append([chat_id_RD])
        ModulesData.append([chat_id_RD])
        ClassIndexName.append([chat_id_RD])
    except:
        ModulesName.append([chat_id_RD])
        ModulesData.append([chat_id_RD])
        ClassIndexName.append([chat_id_RD])

# For every message through telegram, it gets filter out here (according to message type)
def handle(msg):
    global ModulesName, ModulesData, ClassIndexName
    global content_type, chat_type, chat_id, flavor
    global ExtraOptions_markup, return_markup
    flavor = telepot.flavor(msg)
    content_type, chat_type, chat_id = telepot.glance(msg, flavor=flavor)
    summary = (flavor, content_type, chat_type, chat_id )
    print (summary)
    return_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Return to Settings', callback_data='NONE')]])
    ExtraOptions_markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Add modules', callback_data='ADD')],
                        [InlineKeyboardButton(text='Remove modules', callback_data='REMOVE')],
                        [InlineKeyboardButton(text='Check modules', callback_data='CHECK')],
                        [InlineKeyboardButton(text='Continue and retrieve ICal', callback_data='CONTINUE')]
                        ])
    print (getCal_flag, CourseCode_flag, CheckCourse_flag, ClassIndex_flag,\
           ExtraOptions_flag, Remove_flag, Generate_flag)
    # When user input is in text, run on_chat_message(msg)
    if flavor == "chat":
        on_chat_message(msg)
    # When user input is in inlinekeyboard, run on_callbackquery(msg)
    elif flavor == "callback_query":
        on_callback_query(msg)
    else:
        return

def on_chat_message(msg):
    global getCal_flag, CourseCode_flag, CheckCourse_flag, ClassIndex_flag,\
           ExtraOptions_flag, Remove_flag, Generate_flag
    global ModulesName, ModulesData, ClassIndexName
    
    #Step 0: "/start" command to introduce bot to user
    if msg["text"] == "/start":
        bot.sendMessage(chat_id, """ Hello there! I am ICalBot, and I am here to simplify your life in NTU.
You can use me to retrieve an electronic calendar for Your Modules (You will need to give me your course code and group index) or NTU Key Events. 
May TheForce be with you.

To begin, click /getCal
click /help for more information """)
        reset_flags(chat_id)
        # Create "storage" space for the input/output for each user
        reset_data(chat_id)

    #Step 1: "/getCal" command for options of ICal
    elif msg["text"] == "/getCal":
        getCal_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Get ICal for Specific Course(s)', callback_data='Course')],
            [InlineKeyboardButton(text='Get ICal for NTU Key Events', callback_data='NTUEvent')]
            ])
        message_with_inline_keyboard = bot.sendMessage(chat_id, "Which ICal would you like to generate?", reply_markup=getCal_markup)
        getCal_flag.append(chat_id)
        
    #Step -1: "/reset" command to reset data and values
    elif msg["text"] == "/reset":
        bot.sendMessage(chat_id, "All data has been reset. Please type /getCal if you would like to begin once again")
        reset_data(chat_id)
        reset_flags(chat_id)
        
    #Step -2: "/help" to provide more commands
    elif msg["text"] == "/help":
        bot.sendMessage(chat_id, """ NTU_ICal_Bot is pretty easy to use, just follow the instructions!

Type /getCal if you would like to obtain an ICal
Type /reset if you accidentally end up the wrong place AND would like to remove all modules""")
        
    #Step 3: After receiving Course Code, check whether the retrieved data is correct
    elif chat_id in CourseCode_flag:
        bot.sendMessage(chat_id, "Please wait for moment, this may take awhile...")
        CourseInput_3 = msg["text"]
        Retrieved_Course_3 = timetable_extract(CourseInput_3) 
        if Retrieved_Course_3 == False:
            bot.sendMessage(chat_id, "Can't find your course. Please retry: ", reply_markup=return_markup)
            reset_flags(chat_id)
            Remove_flag.append(chat_id)
            CourseCode_flag.append(chat_id)
        elif Retrieved_Course_3 == True:
            bot.sendMessage(chat_id, """This module is an online course, thus there is no input for the timetable(aren't you glad).
Please select another module:""", reply_markup=return_markup)
            reset_flags(chat_id)
            Remove_flag.append(chat_id)
            CourseCode_flag.append(chat_id)
        else:
            bot.sendMessage(chat_id, Retrieved_Course_3)
            bot.sendPhoto(chat_id, open('class_index.png', 'rb'))
            YesNo_markup = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text='Yes', callback_data='Y')],
                [InlineKeyboardButton(text='No', callback_data='N')]
                ])
            bot.sendMessage(chat_id, "Is this the course you are looking for? (Yes/No)", reply_markup=YesNo_markup)
            reset_flags(chat_id)
            CheckCourse_flag.append(chat_id)


    #Step 5: After class index input, get timetable and extra options(Add,Remove,Output)
    elif chat_id in ClassIndex_flag:
        ClassInput = msg["text"]
        index_5 = UserData(chat_id)
        List_5 = ModulesData[index_5][-1]                   #To obtain the Alltext for user
        print (List_5)
        try:    
            timetable_extract2(List_5, ClassInput) 
            bot.sendMessage(chat_id, (ModulesName[index_5][-1] + " Added."))
            bot.sendMessage(chat_id, "Would you like to:", reply_markup=ExtraOptions_markup)
            ClassIndexName[index_5].append(ClassInput)
            print (ModulesData,ModulesName,ClassIndexName)
            reset_flags(chat_id)
            ExtraOptions_flag.append(chat_id)
        except:
            bot.sendMessage(chat_id, "Can't find your class index. Please retry: ")
            reset_flags(chat_id)
            ClassIndex_flag.append(chat_id)

def on_callback_query(msg):
    global getCal_flag, CourseCode_flag, CheckCourse_flag, ClassIndex_flag,\
           ExtraOptions_flag, Remove_flag, Generate_flag
    global ModulesName, ModulesData, ClassIndexName

    if chat_type in getCal_flag:
    #Step 2a: Choosing option for getting course ICal => input CourseCode
        if chat_id == "Course":
            bot.sendMessage(chat_type, "Please enter your course code/name:")
            reset_flags(chat_type)
            CourseCode_flag.append(int(chat_type))
        
    #Step 2b: Choosing option for getting ntu general ICal [End]
        elif chat_id == "NTUEvent":
            bot.sendMessage(chat_type, """All ICal for NTU Key Events are available on this website:
http://www.ntu.edu.sg/Students/Undergraduate/AcademicServices/AcademicCalendar/Pages/AY2016-17.aspx """)

    elif chat_type in CheckCourse_flag:
        #Step 4a: If course is correct, get class index input
        if chat_id == "Y":
            bot.sendMessage(chat_type, "Please enter your class index:")
            reset_flags(chat_type)
            ClassIndex_flag.append(int(chat_type))

        #Step 4b: IF course is wrong, get another course input    
        if chat_id == "N":
            bot.sendMessage(chat_type, "Please enter your CORRECT course code:")
            index_4b = UserData(chat_type)                         
            del(ModulesName[index_4b][-1])                     # Removing the CourseName and CourseData from Main LIST
            del(ModulesData[index_4b][-1])
            reset_flags(chat_type)
            CourseCode_flag.append(int(chat_type))

    elif chat_type in ExtraOptions_flag:
        #Step 6a: ADD more modules
        if chat_id == "ADD":
            bot.sendMessage(chat_type, "Please enter your course code/name:",reply_markup=return_markup)
            reset_flags(chat_type)
            Remove_flag.append(int(chat_type))
            CourseCode_flag.append(int(chat_type))

        #Step 6b: REMOVE modules
        if chat_id == "REMOVE":
            markup_code = "InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Return', callback_data='NONE')],"
            modulecounter_6b = 0
            index_6b = UserData(chat_type)
            Modules_6b = ModulesName[index_6b]
 
            for Module_6b in Modules_6b[1:]:
                code_segment = '[InlineKeyboardButton(text="""{}""", callback_data="{}")],'.format(Module_6b,modulecounter_6b)
                markup_code = markup_code + code_segment
                modulecounter_6b += 1
            markup_code = markup_code[:-1] + "])"
            markup_code = eval (markup_code)
            bot.sendMessage(chat_type, "Which module would you like to remove?", reply_markup=markup_code)
            reset_flags(chat_type)
            Remove_flag.append(int(chat_type))

        #Step 6c: Check Modules in list    
        if chat_id == "CHECK":
            index_6c = UserData(chat_type)
            ModuleNumber_6c = len(ModulesName[index_6c]) - 1
            if ModuleNumber_6c == 0:
                bot.sendMessage(chat_type, "No modules added.")
            for N in range(0,ModuleNumber_6c):
                bot.sendMessage(chat_type, ("{} [Group index:{}]".format(ModulesName[index_6c][N+1],ClassIndexName[index_6c][N+1])))
            bot.sendMessage(chat_type, "Would you like to:", reply_markup=ExtraOptions_markup)
            reset_flags(chat_type)
            ExtraOptions_flag.append(int(chat_type))
            
        #Step6d : Export ICal
        if chat_id == "CONTINUE":
            bot.sendMessage(chat_type, "Please wait for moment, this may take awhile...")
            index_6d = UserData(chat_type)
            ICal_Generator(ModulesData[index_6d][1:],ModulesName[index_6d][1:])                                   
            ClassIndexName = []
            bot.sendDocument(chat_type, open("calendar" + str(chat_type)+".ics"))
            bot.sendMessage(chat_type, """Here is the ICal you wanted! If you want to obtain a different ICal, click or type /getCal""")
            reset_flags(chat_type)
            reset_data(chat_type)
            os.remove("calendar" + str(chat_type)+".ics")
            os.remove("calendar" + str(chat_type)+".csv")


    #Step6bi : After Remove Module   
    elif chat_type in Remove_flag:
        if chat_id == "NONE":
            bot.sendMessage(chat_type, "Would you like to:", reply_markup=ExtraOptions_markup)
            reset_flags(chat_type)
            ExtraOptions_flag.append(int(chat_type))
        else:
            mod_number = int(chat_id) + 1
            index_6bi = UserData(chat_type)
            bot.sendMessage(chat_type, (ModulesName[index_6bi][mod_number] + " Removed."))
            del(ModulesData[index_6bi][mod_number])
            del(ModulesName[index_6bi][mod_number])
            del(ClassIndexName[index_6bi][mod_number])
            bot.sendMessage(chat_type, 'Would you like to:', reply_markup=ExtraOptions_markup)
            reset_flags(chat_type)
            ExtraOptions_flag.append(int(chat_type))


# 3. Selenium Function
################################################################################################
#Step 3: Retrieve Course Timetable with selenium
def timetable_extract(Courseinput):
    # Problem 1: driver not working (Issue of path of driver)
    driver = webdriver.Chrome()                                             # Run chrome
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
        Retrieved_Course1 = driver.find_element_by_xpath("/html/body/center/table[1]/tbody/tr[1]/td[1]/b/font")             # Find the course code and name obtained
        Retrieved_Course2 = driver.find_element_by_xpath("/html/body/center/table[1]/tbody/tr[1]/td[2]/b/font")
        Retrieved_Course = (Retrieved_Course1.text) + " " + (Retrieved_Course2.text)
        
        Alltext = []                                                            # Create empty set
        tablecontents = driver.find_elements_by_xpath("/html/body/center/table[2]/tbody/tr/td")                  # Find element of "INDEX, TYPE, GROUP, DAY, TIME, VENUE, REMARK"

        for elements in tablecontents:                                          # Find each string:
            elements = elements.text                                            # Convert the retrieved element to text form
            Alltext.append(elements)                                            # Input all text into an array
        print(Alltext)                                                          ## Check that list is correct

        if Alltext[6] == "Online Course":                                       # To filter out Online Courses
            driver.quit()
            return True
        
        else:
            for UserModulesData in ModulesData:                               # Add course data/name to MAIN LIST
                counter = 0
                if UserModulesData[0] == chat_id:
                    ModulesData[counter].append(Alltext)
                    ModulesName[counter].append(Retrieved_Course)
                    break
                else:
                    counter += 1
                
            driver.quit()                                                           # End selenium
            return Retrieved_Course
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
    index = UserData(chat_id)
    del(ModulesData[index][-1])
    ModulesData[index].append(finallist)


# 4. ICAL Generator
#################################################################################################################
def ICal_Generator(finallist,finalname):
    #open calendar.csv file
    global chat_type
    with open("calendar" + str(chat_type)+".csv", "w") as c:
        headers = ("Subject", "StartDate", "StartTime", "EndDate", "EndTime", "AllDayEvent", "Location","Description")
        writer = csv.DictWriter(c, fieldnames = headers)
        writer.writeheader()
        counter_Ical = -1                    #indicate the index for modulename
        # For each module module added by the user
        for Module_Ical in finallist:
            counter_Ical += 1

            #write data into calendar.csv file
            for row_Ical in Module_Ical:
                #define variables here
                First_monday = "14/8/2017" #supposed to be input value from telegram
                dates_list = []
                subject = finalname[counter_Ical] + " {}".format(row_Ical[1])          #subject located at this current row and first column
                starttime = row_Ical[4]                                                     #start time located at this current row and column 5th
                endtime = row_Ical[5]                                                       #end time located at this current row and column 6th
                alldayevent = "False"                                                       #all day event is set to false
                description = " Group: %s \n %s" %(row_Ical[2],row_Ical[7])                 #type of lession and group number is located at 2nd, 3rd, 8th column
                location = row_Ical[6]                                                      #location located at this current row and 7th column
                
                #----assigning values to days of wk and changing date accordingly ----#  
                if(row_Ical[3] == str("MON")):
                    b = 0
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))
    
                elif(row_Ical[3] == str("TUE")):
                    b = 1
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))

                elif(row_Ical[3] == str("WED")):
                    b = 2
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))

                elif(row_Ical[3] == str("THU")):
                    b = 3
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))
                
                elif(row_Ical[3] == str("FRI")):
                    b = 4
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))

                elif(row_Ical[3] == str("SAT")):
                    b = 5
                    date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))

                #----while loop to print/insert all possible dates into array----#
                wk_segment = row_Ical[7]
                if wk_segment == "":
                    total_wk = range(0,13)
                else:
                    # Recall in this code, value wk 0 is representing actual wk 1 and wk cap is 12
                    total_wk = []                                   # To input the int value of week with lesson
                    wk_segment = wk_segment.replace("Wk","")        # Remove the "Wk" in the string
                    wk_segment = wk_segment.split(",")
                    for segment_counter in range(0,len(wk_segment)):
                        if "-" in wk_segment[segment_counter]:
                            segment_Ical = wk_segment[segment_counter].split("-")
                            start_segment = int(segment_Ical[0]) - 1
                            end_segment = int(segment_Ical[1])
                            range_Ical = range(start_segment,end_segment)                                
                            for each_wk in range_Ical:
                                total_wk.append((each_wk))
                        else:
                            total_wk.append((int(wk_segment[segment_counter]))-1)

                print("POTATO")
                print(total_wk)
                 
                for wk in range(0,13):
                    if(wk != 6):
                        if wk in total_wk:
                            dates_list.append(date)
                            print(dates_list)
                        date = datetime.strptime(date,'%m/%d/%Y') + timedelta(days=7)
                        date = str(datetime.strftime(date, '%m/%d/%Y'))

                    else:
                        if wk in total_wk:
                            dates_list.append(date)
                            print(dates_list)
                        date = datetime.strptime(date,'%m/%d/%Y') + timedelta(days=14)
                        date = str(datetime.strftime(date, '%m/%d/%Y'))
        
                    #----while loop to print/insert all possible dates into array----#
                for dcol in range(0,len(total_wk)):
                    start_end_date = dates_list[dcol]
                    writer.writerow({"Subject" : subject, "StartDate" : start_end_date , "StartTime" : starttime , \
                                     "EndDate" : start_end_date , "EndTime" : endtime , "AllDayEvent" : alldayevent , \
                                     "Description" : description, "Location" : location})

    #Initializing Converter for CSV to ICS file,
    #each variable equivalent to a column in the csv file generated
    convert = Convert()
    convert.CSV_FILE_LOCATION = "calendar" + str(chat_type)+".csv"
    convert.SAVE_LOCATION = "calendar" + str(chat_type)+".ics"
    convert.HEADER_COLUMNS_TO_SKIP = 0

    convert.NAME = 0
    convert.START_DATE = 1
    convert.END_DATE = 2
    convert.DESCRIPTION = 3
    convert.LOCATION = 4

    CSV_Data = convert.csv_data
    # Create a list for data in csv
    convert.read_csv()
    # convert.csv_data is the returned value(list) of convert.read_csv
    #print (convert.csv_data)

    # To remove headings
    i = 0
    while i < len(CSV_Data):
        CSV_Row = CSV_Data[i]
        # Order should be [EVENTNAME, START_DATE, END_DATE, DESCRIPTION, LOCATION]
        CSVstart_date = str(CSV_Row[1]) + '-'+ str(CSV_Row[2])
        CSVend_date = str(CSV_Row[1]) + '-' + str(CSV_Row[4])
        try:
            CSV_Row[convert.START_DATE] = datetime.strptime(CSVstart_date, '%m/%d/%Y-%H:%M')
            CSV_Row[convert.END_DATE]= datetime.strptime(CSVend_date, '%m/%d/%Y-%H:%M')
            i +=1
            print("added")
        except:
            CSV_Data.pop(i)
            print(CSV_Data)

        CSVname = CSV_Row[0]

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
            
