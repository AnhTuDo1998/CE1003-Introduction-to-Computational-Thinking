from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
import numpy as np
import telepot
import csv 
from datetime import datetime, timedelta
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import os

#Intializing Telegram Bot:
#########################################################################
token = '388718978:AAEUppjISCz8eVq_j3b8owag04-E95y1PRk'
bot = telepot.Bot(token)
print(bot.getMe())

#Initializing Chrome webdriver:
chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', None)
opts = ChromeOptions()
opts.binary_location = chrome_bin
self.selenium = webdriver.Chrome(executable_path="chromedriver", chrome_options=opts)

step = 0                                                                        #State variable to indicate which step users is at and for telepot to refer to
Retrieved_Course =''
Retrieved_Class = ''
newlist = []
newlist2 = []


mod_class = []
mod_class = np.array(mod_class)

def update_list_of_mod_classes(mod, group):                                 ###function to return an update list of saved modules
    global mod_class, bot, chat_id
    mod_class= np.append(mod_class, [mod, group])
    #print (mod_class.size)
    total_row = int(mod_class.size/2)
    mod_class = mod_class.reshape(total_row , 2)
    #print(mod_class)
        
        
def extract_course (Courseinput):
    # Parsing data from ntu website
    #########################################################################
     # To input course code obtained from user
    #/Classinput = str(input("Enter Class index no. here:"))

    # Problem 1: driver not working (Issue of path of driver)
                                                                            
    driver.implicitly_wait(10)                                             # Wait for slow processing of devices
    driver.get("https://wish.wis.ntu.edu.sg/webexe/owa/aus_schedule.main")  # Chrome go to website

    #@@@@assert "Class Schedule" in driver.title@@@@@@@@@                   ## Check correct website

    Keyword = driver.find_element_by_name("r_subj_code")                    # Find the element for inputting course code
    Keyword.send_keys(Courseinput)                                          # Input Userinput to element found
    driver.find_element_by_xpath('//input[4]').click()                      # Find and select the "Enter" button
    # Problem 2: Enter the values was an issue, button was assigned an input value so cannot use 'select'

    # Switching Tabs:
    driver.implicitly_wait(5)
    tabs = driver.window_handles                                            # Get list for all tab names
    driver.switch_to_window(tabs[-1])                                        # Switch to last tab 
    print (driver.current_url)                                             ## Check the focus tab is correct

    #@@@@@assert "Class Schedule" in driver.title@@@@@@@
    global Retrieved_Course
    Retrieved_Course = driver.find_element_by_tag_name("tbody")             # Find the course code and name obtained
    print(Retrieved_Course.text)
 

def extract_class (Classinput):
    Alltext = []                                                            # Create empty set
    tablecontents = driver.find_elements_by_tag_name("TD")                  # Find element of "INDEX, TYPE, GROUP, DAY, TIME, VENUE, REMARK"

    for elements in tablecontents:                                          # Find each string:
        elements = elements.text                                            # Convert the retrieved element to text form
        Alltext.append(elements)                                            # Input all text into an array
        #print(Alltext)
    #Alltext = np.array(Alltext)            #No need apparently?
    index = [0,1,2,3,4]                                                     # Position of elements that are not in the table
    Alltext = np.delete(Alltext,index)                                      # Remove irrelevant elements
    #print(Alltext)                                                          ## Check that list is correct


    # Filter relevant data only
    #########################################################################
    length = Alltext.size                           # To obtain total no. of elements in array
    subsetno = length / 7                           # Find total no. of rows
    Table = Alltext.reshape(int(subsetno),7)        # Create a "table" format of x rows and 5 columns
    print(Table)                                                # Create an empty set for valid rows only, aka "newlist"

    # filter top half
    for row in Table:
        if (row[0] != Classinput):
            Table = np.delete(Table,[0],0)
        elif (row[0] == Classinput):
            break
        
    newlist.append(Table[0])                        # Move the first row to "newlist"
    Table = np.delete(Table,[0],0)                  # Remove the first row from the inital table

    # filter bottom half
    for row in Table:                               # Check EACH row
        if (row[0] == ""):                          # If first column is empty, then carry out:
            newlist.append(row)                     # Move row to "newlist"
        elif (row[0] != ""):                        # If first colum is not empty, stop loop
            break
    print(newlist)                                  ## Check that "newlist" is correct


def ical(newlist):
    global newlist2, link
    newlist = np.array(newlist)
    for row in newlist:
        time = row[4]
        start = time[0:4]
        start = start[:2] + ':' + start[2:]
        end = time[5:]
        end = end[:2] + ':' + end[2:]
        row = np.delete(row,4)
        row = np.insert(row,4, start)
        row = np.insert(row,5, end)
        newlist2.append(row)
    newlist2 = np.array(newlist2)
    newlist2 = newlist2.reshape(int(newlist2.size/8), 8)
    print(newlist2)
    First_monday = "14/8/2017" #supposed to be input value from telegram
    print (newlist2.shape) #5 rows, 8 columns
    newlist2_rows, newlist2_cols = newlist2.shape
    nrow = 0 #intial row 
    dcol = 0 #initial column (course code)
    wk = 0 #including recess wk as wk 6
    total_wks = 13 #to equate to the input of button, if special term thn 5, norm is 13

    #open calendar.csv file
    with open("calendar.csv", "w") as c:
        headers = ("Subject", "StartDate", "StartTime", "EndDate", "EndTime", "AllDayEvent", "Description", "Location")
        writer = csv.DictWriter(c, fieldnames = headers)
        writer.writeheader()
        
    #write data into calendar.csv file
        while (nrow < newlist2_rows): #if current row < total rows in newlist array
            
            #define variables here
            subject = newlist2[nrow,0]       #subject located at this current row and first column
            starttime = newlist2[nrow,4]     #start time located at this current row and column 5th
            endtime = newlist2[nrow,5]       #end time located at this current row and column 6th
            alldayevent = "False"           #all day event is set to false
            description = " Type: %s \n Group: %s \n %s" %(newlist2[nrow,1],newlist2[nrow,2],newlist2[nrow,7]) #type of lession and group number is located at 2nd, 3rd, 8th column
            location = newlist2[nrow,6]      #location located at this current row and 7th column
            
            #----assigning values to days of wk and changing date accordingly ----#  
            if(newlist2[nrow,3] == str("MON")):
                b = 0
                date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                date = str(datetime.strftime(date, '%m/%d/%Y'))

            elif(newlist2[nrow,3] == str("TUE")):
                b = 1
                date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                date = str(datetime.strftime(date, '%m/%d/%Y'))

            elif(newlist2[nrow,3] == str("WED")):
                b = 2
                date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                date = str(datetime.strftime(date, '%m/%d/%Y'))

            elif(newlist2[nrow,3] == str("THU")):
                b = 3
                date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                date = str(datetime.strftime(date, '%m/%d/%Y'))
                    
            elif(newlist2[nrow,3] == str("FRI")):
                b = 4
                date = datetime.strptime(First_monday,'%d/%m/%Y') + timedelta(days=b)
                date = str(datetime.strftime(date, '%m/%d/%Y'))
            #----assigning values to days of wk and changing date accordingly ---- #

            #----while loop to print/insert all possible dates into array----#
            dates_list = [date]

            while(wk < 12): # change to (wk < (total_wks -1))
                if(wk == 6):
                    date = datetime.strptime(date,'%m/%d/%Y') + timedelta(days=14)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))
                    dates_list.append(date)
                    print(dates_list)
                else:
                    date = datetime.strptime(date,'%m/%d/%Y') + timedelta(days=7)
                    date = str(datetime.strftime(date, '%m/%d/%Y'))
                    dates_list.append(date)
                    print(dates_list)
                wk+=1
            
            #----while loop to print/insert all possible dates into array----#
            while(dcol < total_wks): #dcol = 0
                start_end_date = dates_list[dcol]
                writer.writerow({"Subject" : subject, "Start Date" : start_end_date , "Start Time" : starttime , \
                                 "End Date" : start_end_date , "End Time" : endtime , "All Day" : alldayevent , \
                                 "Description" : description, "Location" : location })
                #print(dcol)
                dcol+=1
                #print (dcol)   
            dcol = 0
            wk = 0
            #print(dcol)
            nrow+=1

    
    #accessing the website for conversion to ical from csv file
    driver = webdriver.Chrome()                                          
    ##driver.implicitly_wait(10)##                            
    driver.get("https://manas.tungare.name/software/csv-to-ical/")
    
    #upload file---note if the file is changed to google drive, send keys must change
    upload = driver.find_element_by_xpath("//*[@id='csvFile']")
    path_csv = os.path.abspath("calendar.csv")
    upload.send_keys(path_csv)
    #converting the file and save to downloads
    convert = driver.find_element_by_xpath("/html/body/article/section/div[1]/form/div/input")
    convert.click()
    path_ics = os.path.abspath("calendar.ics")
    
    

def handle_chat_message(msg):
    global step ,driver, bot, newlist, modlist, classlist, link
    #tell python to note these data from getUpdates only
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

#######################################################Define reply keyboards
    keyboard_initial = ReplyKeyboardMarkup(
        keyboard=[
        [KeyboardButton(text='Add Modules')],
        [KeyboardButton(text='Generate Ical Now!')]
        ],
        one_time_keyboard = True)

    keyboard_validate = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Yes')],
        [KeyboardButton(text='No')],],
        one_time_keyboard = True)

    keyboard_terminate= ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Add Modules")],
        [KeyboardButton(text="Remove Modules")],
        [KeyboardButton(text="Generate Ical Now!")],],
        one_time_keyboard = True)
    ########################### main loop for the program
    if msg['text'] == '/start':                                                                     #/start command handler
        step = 0
        bot.sendMessage(chat_id,'Welcome to NTU iCal Bot!\n' +
                                """ I am built to help you create a electronic calendar to simplify your life in NTU.
Please help me to come up with your calendar by filling in your Course Code as well as group indext number (access via your Stars Planner or Stars
Firstly, please select one of the following functions: """, reply_markup = keyboard_initial )
        step += 1

    elif msg['text'] == '/ical':
        step = 0
        ical(newlist)
      
    elif step == 1:                                                                                                                     #2 Options: To add mods or to generate the current mods( add a feature of validation for improvement)
            if msg['text'] == "Add Modules":                                                                                
                bot.sendMessage(chat_id, 'Enter Course Code or Keywords here (e.g: CE1003 or Computational Thinking): ')             #Get input from user for their course, mods
                step += 1
            else:
                ical(newlist)
                print("generating the ical")
                bot.sendDocument(chat_id, link)
                                                                                                                                                
    elif step == 2:
        Courseinput = msg['text']
        print (Courseinput)
        try:
            extract_course(Courseinput)
            bot.sendMessage(chat_id, 'Is this the course you are looking for?', reply_markup = keyboard_validate)
            bot.sendMessage(chat_id, Retrieved_Course.text)
            step += 1
        except NoSuchElementException:
            bot.sendMessage(chat_id, "Can't find your course. Please retry: ")
            step = 2

    elif step == 3:
        print (msg['text'])
        if msg['text'] == 'Yes':
            url=driver.current_url
            bot.sendMessage(chat_id, "Enter Class index no. here:")
            step += 1

        elif msg['text'] == 'No':
            print(msg['text'])
            bot.sendMessage(chat_id, "Do you want to retry?", reply_markup = keyboard_validate)
            step  +=2

    elif step == 4:
        Classinput = Retrieved_Class = msg['text']
        try:
            extract_class(Classinput)
            update_list_of_mod_classes(Retrieved_Course.text, Retrieved_Class)
            bot.sendMessage(chat_id, "You have added these courses and group index: "  )
            for rownumber in range(0, int(mod_class.size/2)):
                for columnnumber in range (0, 2):
                    bot.sendMessage(chat_id, mod_class[rownumber, columnnumber])

            bot.sendMessage(chat_id, "What you want me do ?", reply_markup = keyboard_terminate)
            step = 1

        except IndexError:
            bot.sendMessage(chat_id, "Can't seem to find your group index number! Try again: ")
            step = 4

    elif step == 5:
        if msg['text'] == 'Yes':
            step = 1
            bot.sendMessage(chat_id, "Enter a function: ",reply_markup = keyboard_initial )

##########################################################################################        

MessageLoop(bot, {'chat': handle_chat_message}).run_as_thread()

                
        










