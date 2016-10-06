""" A software to help accumulate CGPA / SGPA data and extract useful results for the students of IIT KGP.

Important Features:
1. SEMESTER SUMMARISER
    Summarises the important aspects of a particular semester for a department 
    based on previous year grades. The important aspects include:
    - Know the average SGPA for the semester (based on previous year) to get a fair idea about the semester's difficulty level.
    - Generating the grade distribution data for all the depth subjects in the previous year
    - Generate list of all the breadth and elective courses that were actually taken up by previous year students.
    - Generate the grade distribution for these breadth and electives based on students of a particular department only.
    - Sort the depth subjects in decreasing order of 'difficulty' based on a normalised score calculated from the grade distribution.
    - Find the subject that recorded most deregistrations, helping students know in advance about courses that are strict with attendance.
    - Find the most scoring subject - based on number of A's + Ex's, or find the subject with most F's involved. 

2. DEPARTMENT RANKS
    - An important evaluation whenever a semester ends as the option to find the department rank 
      on the basis of SGPA achieved in most recent results is available.
    - CGPA based evaluation is also available.
    - Generating a department rank list for the entire batch on above parameters.

VERY IMP : This version is a high privacy version which includes a lot of features cut down, and a lot of unused code.

Developed by : Avikalp Srivastava
"""

# KEYS -
# UPDATE : These are followed by a date and values that need to be updated when that date arrives.
# (PS can be automated by datetime, but i don't trust that for 1 second.)
# Issue : Minor to Semi-Major Issues. Please fix.
# TODO : Enhancements. Please make some. 
# VULNERABLE : Code that might break , generally if something unusual happens. Please make the code more robust.

# TODO List
# 
# Cache 
# Address Vulnerability of performing .find() on user given data
# TODO's present in code

# Dependencies
# [requests, bs4, prettytable, eventlet]

# Software Requirements
# [Python 2.7, pip] 

# Usage : Exception Handling
from __future__ import with_statement
# Usage : Sort dictionary based on keys / values
import operator
# Usage : open a link in user's default web browser.
import webbrowser
# Usage : Connect to a link
import requests 
# Usage : scraping ERP performance page
from bs4 import BeautifulSoup
# Usage : To display data in tables
from prettytable import PrettyTable
# Usage : Regular Expressions for scraping html text
import re
# Usage : While generating previous year depth subj grade list
import datetime
# Usage : floor function
import math
# Usage : -
import time
# Usage : Timeout a request
import eventlet
eventlet.monkey_patch(socket = True)
# Usage : Suppressing warnings on non HTTPS
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Stores the version of the software
# Used for Software Update, after matching latest version number available from http://cgaccumulator.blog.com/
version = '1.1.2'


def check_for_update(content):
    """ Compares global var version with the version mentioned at http://cgaccumulator.blogspot.com/.
    
    Prompts user for update, if available.
    """
    global version
    for line in content:
        matchObj = re.match( r'LATEST VERSION : (.*)<br/>', line, re.M|re.I)
        if matchObj:
            if matchObj.group(1) != version:
                for nline in content:
                    mobj = re.match(r'UPDATE INFO : (.*)<br/>', nline, re.M|re.I)
                    if mobj:
                        print '\a'
                        print "A new version of the software is available. Use 'pip install --upgrade CG-Acc' command to get the latest version or USE THE UPDATE LINK BELOW."
                        print "Update Info : " + str(mobj.group(1))
                    else:
                        mobj = re.match(r'UPDATE LINK :(.*)<br/>', nline, re.M|re.I)
                        if mobj:
                            print "Update Link : " + str(mobj.group(1))
                            time.sleep(1)
                            break
            break


def is_number(s):
    """ Check if given var is / can be converted to float """
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int(s):
    """ Check if given var is / can be converted to int """
    try:
        float(s)
        if float(s) - int(s) == 0:
            return True
        else:
            return False
    except ValueError:
        return False


def connect(fname, url_to_scrape):
    """Connect to the given url, Return HTML content

    Use the text file with name fname for the parsed HTML
    Return the parsed HTML content as a string
    Return 'Exit' if connection failure occurs 3 times
    """
    try:
        with eventlet.Timeout(12, Exception):
            r = requests.get(url_to_scrape, verify = False)
        soup = BeautifulSoup(r.text, "html.parser")
        with open(fname, "w") as text_file:
            text_file.write("{}".format(soup))
        with open(fname) as f:
            content = f.readlines()
        connect.counter = 0
        return content
    #except requests.exceptions.RequestException:
    except Exception:
        # Static var storing then number of times attempt to connect has failed
        # If >=4, then we assume that user is not connected to the internet.
        connect.counter += 1
        if connect.counter >= 4:
            connect.counter = 0
            print '\a'
            print '\nYou don\'t seem to be having internet connectivity | Connection with ERP performance page cannot be established.'
            reconnect_choice = raw_input('Enter r to try again, x to exit :  ')
            while reconnect_choice not in ['r', 'x']:
                reconnect_choice = raw_input('Invalid choice! Please enter r to try reconnecting again, or enter x to exit :  ')
            if reconnect_choice == 'r':
                print 'Retrying....'
                return connect(fname, url_to_scrape)
            else:
                print "\nExiting...."
                exit(0)
        else:
            if connect.counter == 1:
                print 'Experiencing slow internet connectivity...'
            # print 'Connection Error'
            # print 'Retrying....'
            return connect(fname, url_to_scrape)
connect.counter = 0     
# counter is a static variable for the function connect().


def check_results_availability():
    """ Check if results are available at the moment (Eg-Not available before senate). Return status bool. """
    # The HTML content of the url will be stored in this file
    fname = "Output.txt"
    # UPDATE (01/07/2018)
    # Right now, performs check on default roll number - 14CS10008
    url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=14CS10008'
    content = connect(fname, url_to_scrape)
    for line in content:
        # VULNERABLE
        # Change to other HTML conditions
        if line.find("Students Performance will be enabled after SENATE Approval") != -1 or line.find("HTTP Status 500") != -1:
            return False
    return True


def check_roll_num_validity(user_roll_num):
    """Checks validity of user_roll_num. Return type : bool """
    # List storing available departments in IIT Kharagpur.
    departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
    # List of Msc departments in IIT Kharagpur.
    msc_dep_list = ["GG", "EX", "MA", "CY", "HS", "PH"]
    # Currently, software supports students with starting years as 2012, 2013, 2014, 2015
    # Requires Annual UPDATE
    years = ["11","12","13","14","15"]

    # Check that first 2 chars are present in years, next 2 in departments, length is 9 and the last 5 chars correspond to an integer
    if user_roll_num[0:2] in years and user_roll_num[2:4] in departments and len(user_roll_num) == 9 and is_int(user_roll_num[4:9]):
        num = int(user_roll_num[4:9])
        # If the department belongs to Msc dep list, the last five digits should be in the 20000 series
        if user_roll_num[2:4] in msc_dep_list:
            if 20000 < num < 20100:
                url = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + user_roll_num
                content = connect('Output.txt', url)
                return [len(content) > 50, content]
            else:
                return [False, '']
        # Else for other deps, last five digits should be in 10000 or 30000 series
        elif (10000 < num < 10100) or (30000 < num < 32000):
            url = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + user_roll_num
            content = connect('Output.txt', url)
            return [len(content) > 50, content]
        else:
            return [False, '']
    else:
        return [False, '']


def take_roll_num():
    """ Take a roll number input from user until it is valid, then return it. Return type : str"""
    # Taking roll_num input
    roll_num = raw_input("Enter Roll Number :  ")
    # Converting user inp to upper (14cs10008 - 14CS10008) and checking validity
    while True:
        flag, content = check_roll_num_validity(roll_num.upper())
        if not flag:
            roll_num = raw_input("Roll Number Invalid / Not currently supported. Please enter valid Roll Number :  ")
        else:
            break
    return [roll_num.upper(), content]


def take_year():
    """Take user input for batch start year, validate and return year. Return type : str"""
    # Currently, software supports students with starting years as 2012, 2013, 2014, 2015
    # UPDATE : Annual
    years = ["11","12", "13", "14", "15"]
    year = raw_input("Enter start year for the batch (Choices : 11, 12, 13, 14, 15) :  ")
    while year not in years:
        year = raw_input("Please enter valid year :  ")
    return year


def take_dep():
    """ Take user input for department, validate and return department. Return type : str"""
    # List storing available departments in IIT Kharagpur.
    departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
    dep = raw_input("Enter Department (e.g \"CE\" for civil) :  ")
    # Converting user entered input to uppercase, in case it isn't.
    dep = dep.upper()
    while dep not in departments:
        print "Please enter a valid department!"
        dep = raw_input("Enter Valid Department again : ")
        dep = dep.upper()
    return dep


def take_sem_num():
    """ Take user input for semester number, validate and return. Return type : int"""
    # Right now, software only supports semester 1 to 8
    # EXTEND : Make Semester Physics and Chemistry instead of 1 and 2
    # EXTEND : Introduce semesters 9 and 10
    sem_num = raw_input("Enter Semester Number [3-8] :  ")
    while not is_int(sem_num) or int(sem_num) < 3 or int(sem_num) > 8:
        sem_num = raw_input("Please enter valid Semester Number :  ")
    return int(sem_num)


def is_msc_dep(dep):
    """ Given dep str, check if it's one of the Msc dep offered by IIT KGP. Return bool """
    msc_dep_list = ["GG", "EX", "MA", "CY", "HS", "PH"]
    if dep in msc_dep_list:
        return True
    return False


def get_prev_year(sem_num):
    """ Given semester number, find the year of the batch which most recently completed that semester number """
    today = datetime.date.today()
    current_year = float(today.year)
    current_month = int(today.month)
    if current_month >= 5:
        current_year += 0.6
    # For sem num between 1 to 8, year always takes values between 12 to 15
    prev_year = int(math.floor(current_year - (sem_num + 1)/float(2)))
    prev_year -= 2000
    return str(prev_year)


def find_name(roll_num, content=''):
    """ Find name for the given roll number. Returns '' if record doesn't exist. """
    if content == '':
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(roll_num)
        fname = "Output.txt"
        content = connect(fname, url_to_scrape)
    name = ''
    for line in content:
        if line.find("Name") != -1:
            # TODO : Replace with regex logic - (.*)<td>(.*)</td> - group(2)
            idx = 24
            while line[idx] != '<':
                idx += 1
            name = line[24:idx]
            break
    return name



def find_cg_individual(roll_num, content = ''):
    """ Find and return CGPA for given roll num. Returns -1 if no results exist for the given roll num.

    Choice Route - 1.1 -> 1 -> Enter Roll Number 
    CGPA -> Individual    
    """
    # If HTML content for the roll_num has not been passed, make request and get it.
    if content == '':
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(roll_num)
        fname = "Output.txt"
        content = connect(fname, url_to_scrape)
    # VULNERABLE
    # Generally, if a roll number is invalid, the HTML content of the page is less than 40 lines.
    # Can be replaced by other robust methods, such as if name == "" etc.
    if len(content) < 50:
        return -1
    else:
        for line in content:
            # TODO : replace with regex
            if line.find("CGPA") != -1 and line[4] != "<" and is_number(line[31:35]):
                return float(line[31:35])
        return -1



def find_cg_batch(year, dep, msc_dep_bool):
    """ Prints the CG list for the batch with given year and dep. Table contents : Roll Number, CGPA, Name

    Choice Route - 1.1 -> 2 -> Enter year -> Enter dep
    CGPA -> Batch    
    """
    roll_count = 10000
    # If department is Msc, roll count of last 5 digits starts from 20000
    if msc_dep_bool:
        roll_count = 20000
    # Keeps count of number of students in the batch
    student_count = 0
    # Keeps count of the number of consecutive roll numbers encountered for which no records were found.
    bad_count = 0
    # Sum of CG's for this batch. Used for calculating average.
    cg_total = 0.00
    # Initialising Table
    table = PrettyTable(['Roll Num', 'Name', 'CGPA'])
    while True:
        # Moving to next student
        roll_count += 1
        rollno = str(year) + str(dep) + str(roll_count)
        # URL to this student's performance
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
        # HTML data to be temporarily stored here
        fname = 'Output.txt'
        # Getting HTML data from the net and storing it as a list of strings in content
        content = connect(fname, url_to_scrape)
        # Find cg for given roll number
        cg = find_cg_individual(rollno, content)
        # VULNERABLE
        # If no records for this roll number, increment the bad count
        if cg == -1:
            bad_count += 1
        else:
            # Reset bad count, since it stores the CONSECUTIVE bad roll numbers encountered
            bad_count = 0
            student_count += 1
            cg_total += cg
            name = find_name(rollno, content)
            print 'Processing', 
            print rollno, name
            table.add_row([rollno, name, cg])
        # If the subject is not Msc, then we make a transition to dual degree students
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
            if dep == 'MI':
                roll_count = 31000
        # Conditions for ending, self explanatory.
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    print '\nCGPA list for batch : ' + str(year) + '-' + dep
    print table
    print '\nTotal students = ' + str(student_count)
    print 'Average CGPA =  ',
    print  str(cg_total/float(student_count)) if student_count > 0 else '-'
    print ''

def find_cg_list_individual(user_roll_num, content = ''):
    """ Return list of CGPA over the years for the given roll number"""
    cg_list = []
    if content == '':
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
        fname = "Output.txt"
        content = connect(fname, url_to_scrape)
    # VULNERABLE
    if len(content) < 50:
        # Return empty list
        return cg_list
    else:
        # Traversing whole file and appending SGPA's to sg_list
        for line in content:
            matchObj = re.match( r'<td>(.*)<b> CGPA</b></td><td>(\d+\.\d+)</td>', line, re.M|re.I)
            if matchObj and line.find("Additional") == -1:
                cg_list.append(float(matchObj.group(2)))
        return cg_list

def find_sg_list_individual(user_roll_num, content = ''):
    """ Return list of SGPA over the years for the given roll number

    Choice Route - 1.2 -> 1 -> Enter Roll Number
    SGPA List -> Individual
    """
    sg_list = []
    if content == '':
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
        fname = "Output.txt"
        content = connect(fname, url_to_scrape)
    # VULNERABLE
    if len(content) < 50:
        # Return empty list
        return sg_list
    else:
        # Traversing whole file and appending SGPA's to sg_list
        for line in content:
            if line.find("SGPA") != -1 and is_number(line[25:29]):
                sg_list.append(str(line[25:29]))
        return sg_list


def find_recent_sg_or_sg_list_batch(year, dep, msc_dep_bool, choice = '0', num_req = 8):
    """ Choice = '0' for Sg list of given batch, '1' for Recent sg of given batch. 

    Choice Route : 1.2 -> 2 -> Enter Year -> Enter Dep or 1.3 -> 2 -> Enter Year -> Enter Dep
    SGPA List -> Batch or Recent SGPA -> Individual
    """
    roll_count = 10000
    if msc_dep_bool:
        roll_count = 20000
    student_count = 0
    bad_count = 0
    sg_total = 0.00
    fname = 'Output.txt'
    table = None
    total_SGPA = [0.00] * 8
    total_SGPA_sq = [0.00] * 8
    if choice == '0':
        table = PrettyTable(['Roll Num', 'Name', 'SGPA List (Starts from most recent)'])
    elif choice == '1':
        table = PrettyTable(['Roll Num', 'Name', 'Recent SGPA'])
    while True:
        roll_count += 1
        rollno = str(year) + str(dep) + str(roll_count)
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
        content = connect(fname, url_to_scrape)
        # VULNERABLE
        if len(content) < 40:
            bad_count += 1
        else:
            bad_count = 0
            if choice == '0':
                sg_list = find_sg_list_individual(rollno, content)
                if len(sg_list) != num_req:
                    continue;
                else:
                    student_count += 1
                    idx = 0
                    for item in sg_list:
                        sg_list[idx] = float(sg_list[idx])
                        idx += 1
                    total_SGPA = [sum(x) for x in zip(total_SGPA, sg_list)]
                    total_SGPA_sq = [x + y*y for x,y in zip(total_SGPA_sq, sg_list)]
            elif choice == '1':
                sg = find_recent_sg_individual(rollno, content)
                sg_total += sg
            name = find_name(rollno, content)
            print 'Processing', 
            print rollno
            if (choice == '0' and len(sg_list) != 0) or (choice == '1' and sg != -1):
                if choice == '0':
                    table.add_row([rollno, name, str(sg_list)])
                    del sg_list[:]
                elif choice == '1':
                    table.add_row([rollno, name, sg])
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
            if dep == 'MI':
                roll_count = 31000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    if choice == '0':
        total_SGPA.reverse()
        total_SGPA_sq.reverse()
        total_SGPA.append(student_count)
        lis = [total_SGPA, total_SGPA_sq]
        return lis
    '''
        print '\nSGPA list for batch ' + year + '-' + dep + ' : '
    elif choice == '1':
        print '\nRecent SGPA list for batch ' + year + '-' + dep + ' : '
    print table
    print '\nTotal students = ' + str(student_count)
    if choice == '1':
        print 'Average SG this recent semester for the batch ' + year + '-' + dep + ' : ',
        print str(sg_total/float(student_count)) if student_count > 0 else '-'
    print ''
    '''

def find_cg_list_batch(year, dep, msc_dep_bool, choice = '0'):

    roll_count = 10000
    if msc_dep_bool:
        roll_count = 20000
    student_count = 0
    bad_count = 0
    cg_total = 0.00
    fname = 'Output.txt'
    table = None
    total_CGPA = [0.00] * 8;
    total_CGPA_sq = [0.00] * 8;
    while True:
        roll_count += 1
        rollno = str(year) + str(dep) + str(roll_count)
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
        content = connect(fname, url_to_scrape)
        # VULNERABLE
        if len(content) < 40:
            bad_count += 1
        else:
            bad_count = 0
            if choice == '0':
                cg_list = find_cg_list_individual(rollno, content)
                if len(cg_list) != 8:
                    continue;
                else:
                    student_count += 1
                    idx = 0
                    cg_list.reverse()
                    for item in cg_list:
                        cg_list[idx] = float(cg_list[idx])
                        idx += 1
                    total_CGPA = [sum(x) for x in zip(total_CGPA, cg_list)]
                    total_CGPA_sq = [x + y*y for x,y in zip(total_CGPA_sq, cg_list)]
            name = find_name(rollno, content)
            print 'Processing', 
            print rollno
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
            if dep == 'MI':
                roll_count = 31000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    total_CGPA.reverse()
    total_CGPA_sq.reverse()
    total_CGPA.append(student_count)
    return [total_CGPA, total_CGPA_sq]

def find_recent_sg_individual(user_roll_num, content = ''):
    """ Return most recent SGPA for given roll number 

    Choice Route : 1.3 -> 1 -> Enter Roll Number
    Recent SGPA -> Individual
    """
    user_sg = -1
    if content == '':
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
        fname = "Output.txt"
        content = connect(fname, url_to_scrape)
    # VULNERABLE
    if len(content) < 50:
        return -1
    else:
        for line in content:
            if line.find("SGPA") != -1 and is_number(line[25:29]):
                user_sg = float(line[25:29])
                break
        return user_sg

def find_recent_cg_individual(user_roll_num, content = ''):
    """ Return most recent CGPA for given roll number """
    user_cg = -1
    if content == '':
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
        fname = "Output.txt"
        content = connect(fname, url_to_scrape)
    # VULNERABLE
    if len(content) < 50:
        return -1
    else:
        for line in content:
            matchObj = re.match( r'<td>(.*)<b> CGPA</b></td><td>(\d+\.\d+)</td>', line, re.M|re.I)
            if matchObj and line.find("Additional") == -1:
                user_cg = matchObj.group(2)
                break
        return float(user_cg)

def find_dep_rank_individual(roll_num, choice = '1', content = ''):
    """ Choice = '1' - CG based department rank, Choice = '2' - SG based. Returns -1 if no record exists.

    Choice Route : 2.1 -> 1 -> Enter Roll Number or 2.2 -> 1 -> Enter Roll Number 
    Department Rank Based on CG -> Inidividual or Department Rank Based on SG -> Inidividual
    """
    if content == '':
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(roll_num)
        fname = "Output.txt"
        content = connect(fname, url_to_scrape)
    if choice == '1':
        user_gpa = find_cg_individual(roll_num, content)
    elif choice == '2':
        user_gpa = find_recent_sg_individual(roll_num, content)
    if user_gpa == -1:
        return -1
    # Extracting dep and year from given roll num
    year = roll_num[0:2]
    dep = roll_num[2:4]
    last_five = int(roll_num[4:9])
    msc_dep_bool = None
    if 20000 < last_five < 30000:
        msc_dep_bool = True
    else:
        msc_dep_bool = False
    roll_count = 10000
    if msc_dep_bool:
        roll_count = 20000
    student_count = 0
    bad_count = 0
    dep_rank = 1
    while True:
        roll_count += 1
        rollno = str(year) + str(dep) + str(roll_count)
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
        fname = 'Output.txt'
        content = connect(fname, url_to_scrape)
        # VULNERABLE
        if len(content) < 50:
            bad_count += 1
        else:
            print 'Processing', 
            print rollno
            bad_count = 0
            student_count += 1
            if choice == '1':
                cg = find_cg_individual(rollno, content)
                if cg > user_gpa:
                    dep_rank += 1
            elif choice == '2':
                sg = find_recent_sg_individual(rollno, content)
                if sg > user_gpa:
                    dep_rank += 1
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
            if dep == 'MI':
                roll_count = 31000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    info_list = [dep_rank, student_count]
    return info_list


def find_dep_rank_list_CG(year, dep, msc_dep_bool):
    """ Generate and print department ranks for the given batch based on CGPA

    Choice Route : 2.1 -> 2 -> Enter Year -> Enter Dep
    Department Rank Based on CG -> Batch
    """
    roll_count = 10000
    if msc_dep_bool:
        roll_count = 20000
    student_count = 0
    bad_count = 0
    fname = 'Output.txt'
    dep_dict = {}
    while True:
        roll_count += 1
        rollno = str(year) + str(dep) + str(roll_count)
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
        content = connect(fname, url_to_scrape)
        cg = find_cg_individual(rollno, content)
        if cg == -1:
            bad_count += 1
        else:
            bad_count = 0
            student_count += 1
            name = find_name(rollno, content)
            print 'Processing', 
            print rollno
            # Handling duplicate names. Will label more than 2 dups in same fashion 
            try:
                dep_dict[name]
                dep_dict[name + ' (2)'] = cg
            except KeyError:
                dep_dict[name] = cg
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
            if dep == 'MI':
                roll_count = 31000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    # Sorting names in dict acc to CG in descending order.
    # TODO : analyze if this is stable or not. If not, make it -_-
    sorted_dep_dict = sorted(dep_dict.items(), key=operator.itemgetter(1), reverse=True)
    index = 0
    prev_rank = 1
    print '\nDepartment Rank distribution for the batch ' + year + '-' + dep + ' based on CGPA : '
    table = PrettyTable(['Rank', 'CGPA'])
    for item in sorted_dep_dict:
        if index != 0 and sorted_dep_dict[index][1] == sorted_dep_dict[index - 1][1]:
            table.add_row([prev_rank, item[1]])
        else:
            table.add_row([index + 1, item[1]])
            prev_rank = index + 1
        index += 1
    print table
    print ''


def find_dep_rank_list_SG(year, dep, msc_dep_bool):
    """ Generate and print department ranks for the given batch based on SGPA

    Choice Route : 2.2 -> 2 -> Enter Year -> Enter Dep
    Department Rank Based on SG -> Batch
    """
    roll_count = 10000
    if msc_dep_bool:
        roll_count = 20000
    student_count = 0
    bad_count = 0
    fname = 'Output.txt'
    dep_dict = {}
    while True:
        roll_count += 1
        rollno = str(year) + str(dep) + str(roll_count)
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
        content = connect(fname, url_to_scrape)
        sg = find_recent_sg_individual(rollno, content)
        if sg == -1:
            bad_count += 1
        else:
            bad_count = 0
            student_count += 1
            name = find_name(rollno, content)
            print 'Processing', 
            print rollno
            # Handling duplicate names. Will label more than 2 dups in same fashion 
            try:
                dep_dict[name]
                dep_dict[name + ' (2)'] = sg
            except KeyError:
                dep_dict[name] = sg
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
            if dep == 'MI':
                roll_count = 31000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    # Sorting names in dict acc to SG in descending order.
    # TODO : analyze if this is stable or not. If not, make it -_-
    sorted_dep_dict = sorted(dep_dict.items(), key=operator.itemgetter(1), reverse=True)
    index = 0
    prev_rank = 1
    print '\nDepartment Rank list for the batch ' + year + '-' + dep + ' based on recent SGPA : '
    table = PrettyTable(['Rank', 'SG'])
    for item in sorted_dep_dict:
        if index != 0 and sorted_dep_dict[index][1] == sorted_dep_dict[index - 1][1]:
            table.add_row([prev_rank, item[1]])
        else:
            table.add_row([index + 1, item[1]])
            prev_rank = index + 1
        index += 1
    print table
    print ''


def get_depth_sub_name_list(year, dep, sem_num, content = ''):
    """ Return list of name of depth subjects (excluding EAA) for this batch"""
    sub_name_list = []

    tmp_roll_count = 10000
    if is_msc_dep(dep):
        tmp_roll_count = 20000
    while len(content) <= 50:
      tmp_roll_count += 1
      user_roll_num = year + dep + str(tmp_roll_count)
      url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
      fname = "Output.txt"
      content = connect(fname, url_to_scrape)
    index = 0
    sem_found = False
    for line in content:
        if (line.find("<tr bgcolor=\"#FFF3FF\">") != -1 or line.find("<tr bgcolor=\"pink\">") != -1) and sem_found:
            currentLine = content[index + 2]
            matchObj = re.match( r'<td>(.*)</td>', currentLine, re.M|re.I)
            if matchObj and str(matchObj.group(1)).find("<b>") == -1:
                sub_name = str(matchObj.group(1))
                currentLine = content[index + 6]
                matchObj = re.match(r'<td align="center">(.*)</td>', currentLine, re.M|re.I)
                sub_type = str(matchObj.group(1))
                if sub_type == 'Depth' and sub_name.find("EXTRA ACADEMIC ACTIVITY") == -1:
                    sub_name_list.append(sub_name)
        elif line.find("<tr><td bgcolor=\"#FFF3FF\" colspan=\"2\"><h3 align=\"center\">Semester no:") != -1:
            matchObj = re.match(r'<tr><td bgcolor="#FFF3FF" colspan="2"><h3 align="center">Semester no: ([1-9]).*', line, re.M|re.I)
            if matchObj:
                if sem_found:
                    break
                elif int(matchObj.group(1)) == sem_num:
                    sem_found = True
        index += 1
    return sub_name_list


def find_depth_sub_grade_list(dep, sem_num, msc_dep_bool, print_table = 'False'):
    """ The wrapper function for gen_depth_sub_grade_list. Returns dict with subj names as key and grade lists as values.
    
    Choice Route : 3.1 -> Enter Semester Number
    Depth Subjects Grade List
    """
    prev_year = get_prev_year(int(sem_num))
    dep_dict = {}
    dict_list = get_br_el_sub_name_list_helper(prev_year, dep, sem_num, dep_dict)
    sgpa_avg = dict_list[2]
    dict_list.pop()
    dict_list.append(dep_dict)
    if not print_table:
        print '\n\nAverage SGPA for the semester number ' + str(sem_num) + ' for the department ' + dep + ' based on prev yr is ' + str(sgpa_avg)
        return dict_list
    # Else :
    grade_dict = dep_dict
    print '\n\nAverage SGPA for the semester number ' + str(sem_num) + ' for the department ' + dep + ' based on prev yr is ' + str(sgpa_avg)
    print '\nPrevious year grade list of depth subjects for semester number ' + str(sem_num) + ' for the ' + dep + ' department :'
    table = PrettyTable(['Sub Name', 'Ex', 'A', 'B', 'C', 'D', 'P', 'F', 'X'])
    table.align = 'l'
    for item in grade_dict:
        table.add_row([item.replace("&amp;", "&"), grade_dict[item][0],  grade_dict[item][1], grade_dict[item][2], grade_dict[item][3],
            grade_dict[item][4], grade_dict[item][5],  grade_dict[item][6], grade_dict[item][7]])
    print table
    print ''
    return dict_list


def find_sum(alist):
    """ Find normalised difficulty score from a particular subject's grade list and return it.

    No. of Ex are multiplied by 0, A's by 1, B's by 2 and so on. And final sum is returned.
    """
    csum = 0
    factor = 0
    for item in alist:
        csum += item*factor
        factor += 1
    return csum


def find_subjects_by_difficulty_level(grade_dict):
    """ Prints difficlulty scores (as computed by find_sum) for subjects in grade_dict """
    sum_dict = {}
    for item in grade_dict:
        csum = find_sum(grade_dict[item])
        sum_dict[item] = csum
    sorted_sum_dict = sorted(sum_dict.items(), key = operator.itemgetter(1), reverse = True)
    print '\nFollowing subjects have been sorted in decreasing level of difficulty according to their previous yr. grade distribution.'
    table = PrettyTable(['Subject Name', 'Difficulty Score'])
    table.align = 'l'
    table.align['Difficulty Score'] = 'c'
    for item in sorted_sum_dict:
        table.add_row([item[0].replace("&amp;", "&"), item[1]])
    print table

def get_br_el_sub_name_list_helper(year, dep, sem_num, dep_dict = {}):
    """ Function to get breadth and elective subjects taken by previous yr students of the given batch for the given sem_num

    Traverses all roll numbers of the batch to get the exhaustive list.
    Returns a combined list, have dict of breadths as first and electives as second element. 
    """
    br_dict = {}
    el_dict = {}
    msc_dep_bool = is_msc_dep(dep)
    roll_count = 10000
    # If department is Msc, roll count of last 5 digits starts from 20000
    if msc_dep_bool:
        roll_count = 20000
    # Keeps count of number of students in the batch
    student_count = 0
    # Keeps count of the number of consecutive roll numbers encountered for which no records were found.
    bad_count = 0
    sgpa = 0.00
    # Sum of CG's for this batch. Used for calculating average.
    # Initialising Table
    while True:  
        # Moving to next student
        roll_count += 1
        rollno = str(year) + str(dep) + str(roll_count)
        # URL to this student's performance
        url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
        # HTML data to be temporarily stored here
        fname = 'Output.txt'
        # Getting HTML data from the net and storing it as a list of strings in content
        content = connect(fname, url_to_scrape)
        # Find cg for given roll number
        cg = find_cg_individual(rollno, content)
        # VULNERABLE
        # If no records for this roll number, increment the bad count
        if cg == -1:
            bad_count += 1
        else:
            # Reset bad count, since it stores the CONSECUTIVE bad roll numbers encountered
            bad_count = 0
            student_count += 1
            print 'Processing', 
            print rollno
            sgpa += get_br_el_sub_name_list(year, dep, sem_num, br_dict, el_dict, dep_dict, content)
        # If the subject is not Msc, then we make a transition to dual degree students
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
            if dep == 'MI':
                roll_count = 31000
        # Conditions for ending, self explanatory.
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    sgpa = sgpa/float(student_count)
    return [br_dict, el_dict, sgpa]


def get_br_el_sub_name_list(year, dep, sem_num, br_dict, el_dict, dep_dict, content = ''):
    """ Return list of name of breadth and elective subjects for this batch 

    Called by get_br_el_sub_name_list_helper for every roll number in the dep.
    """
    grade_list = ['EX', 'A', 'B', 'C', 'D', 'P', 'F', 'X']
    sub_grade_dict = {'EX' : 0, 'A' : 1, 'B' : 2, 'C' : 3, 'D' : 4, 'P' : 5, 'F' : 6, 'X' : 7}
    index = 0
    sem_found = False
    sgpa = 0.00
    for line in content:
        if (line.find("<tr bgcolor=\"#FFF3FF\">") != -1 or line.find("<tr bgcolor=\"pink\">") != -1) and sem_found:
            currentLine = content[index + 2]
            matchObj = re.match( r'<td>(.*)</td>', currentLine, re.M|re.I)
            if matchObj and str(matchObj.group(1)).find("<b>") == -1:
                sub_name = str(matchObj.group(1))
                currentLine = content[index + 6]
                matchObj = re.match(r'<td align="center">(.*)</td>', currentLine, re.M|re.I)
                sub_type = str(matchObj.group(1))
                currentLine = content[index + 5]
                matchObj = re.match(r'<td align="center">(.*?)<(.+)', currentLine, re.M|re.I)
                sub_grade = str(matchObj.group(1))
                if sub_type.find('Elective') != -1:
                    try:
                        el_dict[sub_name]
                        el_dict[sub_name][sub_grade] += 1
                    except KeyError:
                        el_dict[sub_name] = {}
                        for item in grade_list:
                            el_dict[sub_name][item] = 0
                        el_dict[sub_name][sub_grade] += 1
                elif sub_type.find('Breadth') != -1 or sub_type.find('HSS') != -1:
                    try:
                        br_dict[sub_name]
                        br_dict[sub_name][sub_grade] += 1
                    except KeyError:
                        br_dict[sub_name] = {}
                        for item in grade_list:
                            br_dict[sub_name][item] = 0
                        br_dict[sub_name][sub_grade] += 1
                if sub_type.find('Depth') != -1:
                    try:
                        dep_dict[sub_name]
                        dep_dict[sub_name][sub_grade_dict[sub_grade]] += 1
                    except KeyError:
                        dep_dict[sub_name] = {}
                        for item in grade_list:
                            dep_dict[sub_name] = [0] * 8
                        dep_dict[sub_name][sub_grade_dict[sub_grade]] += 1
        elif (line.find("<td> <b>SGPA</b></td><td>") != -1) and sem_found:
            matchObj = re.match(r'<(.*?)(\d+\.\d+)(.*)', line, re.M|re.I)
            if is_number(matchObj.group(2)):
                sgpa = float(matchObj.group(2))
        elif line.find("<tr><td bgcolor=\"#FFF3FF\" colspan=\"2\"><h3 align=\"center\">Semester no:") != -1:
            matchObj = re.match(r'<tr><td bgcolor="#FFF3FF" colspan="2"><h3 align="center">Semester no: ([1-9]).*', line, re.M|re.I)
            if matchObj:
                if sem_found:
                    break
                elif int(matchObj.group(1)) == sem_num:
                    sem_found = True
        index += 1
    return sgpa;


def get_br_and_elective_grade_list(dep, sem_num, dict_filled_bool, br_dict = {}, el_dict = {}):
    """ Print grade list for all electives and breadth fr prev yr batch for given sem_num

    Calls get_br_el_sub_name_list_helper to get names of all such subjects and generates grade lists
    """ 
    year = get_prev_year(int(sem_num))
    if dict_filled_bool:
        combined_list = [br_dict, el_dict]
    else:
        combined_list = get_br_el_sub_name_list_helper(year, dep, sem_num)
    if len(combined_list[0]) > 0:
        grade_dict = combined_list[0]
        print '\n\nPrevious year grade list of BREADTH subjects for semester number ' + str(sem_num) + ' for the ' + dep + ' department :'
        table = PrettyTable(['Sub Name', 'Ex', 'A', 'B', 'C', 'D', 'P', 'F', 'X'])
        table.align = 'l'
        for item in grade_dict:
            table.add_row([item.replace("&amp;", "&"), grade_dict[item]['EX'],  grade_dict[item]['A'], grade_dict[item]['B'], grade_dict[item]['C'],
                grade_dict[item]['D'], grade_dict[item]['P'],  grade_dict[item]['F'], grade_dict[item]['X']])
        print table
        print ''
        grade_dict.clear()
    else:
        print '\n\nNO BREADTH SUBJECTS FOUND FOR THIS SEMESTER.\n'
    if len(combined_list[1]) > 0:
        grade_dict = combined_list[1]
        print '\n\nPrevious year grade list of ELECTIVE subjects for semester number ' + str(sem_num) + ' for the ' + dep + ' department :'
        table = PrettyTable(['Sub Name', 'Ex', 'A', 'B', 'C', 'D', 'P', 'F', 'X'])
        table.align = 'l'
        for item in grade_dict:
            table.add_row([item.replace("&amp;", "&"), grade_dict[item]['EX'],  grade_dict[item]['A'], grade_dict[item]['B'], grade_dict[item]['C'],
                grade_dict[item]['D'], grade_dict[item]['P'],  grade_dict[item]['F'], grade_dict[item]['X']])
        print table
        print ''
        grade_dict.clear()
    else:
        print '\n\nNO ELECTIVES FOUND FOR THIS SEMESTER.\n'
    

def find_sub_most_x_f(grade_dict, choice):
    """ Given subjects with their grade lists, prints subj with most F's and Deregs. """
    if choice == 1:
        idx = 7
    elif choice == 2:
        idx = 6
    maxim = 0
    maxitem = ''
    sub_list = []
    for item in grade_dict:
        if grade_dict[item][idx] >= maxim:
            maxim = grade_dict[item][idx]
    if maxim != 0:
        for item in grade_dict:
            if grade_dict[item][idx] == maxim:
                sub_list.append(item.replace("&amp;", "&"))
    if choice == 1:
        if len(sub_list) > 0:
            print '\nDepth Subject(s) with most Deregistrations : ',
            for item in sub_list:
                print item,
            print '\nNumber of deregistrations : ' + str(maxim)
        else:
            print '\nNO DEPTH SUBJECTS WITH DEREGISTRATIONS FOUND :D'
    elif choice == 2:
        if len(sub_list) > 0:
            print '\nSubject(s) with most F grades : ',
            for item in sub_list:
                print item,
            print '\nNumber of F grades : ' + str(maxim)
        else:
            print '\nNO DEPTH SUBJECTS WITH F GRADES FOUND :D'
    print ''


def find_sub_most_a_ex(grade_dict):
    """ Given subjects with their grade lists, prints subj with most A's + Ex's. """
    maxim = 0
    for item in grade_dict:
        if grade_dict[item][0] + grade_dict[item][1] > maxim:
            maxim = grade_dict[item][0] + grade_dict[item][1]
    list_sub = []
    for item in grade_dict:
        if grade_dict[item][0] + grade_dict[item][1] == maxim:
            list_sub.append(item)
    print 'Depth Subject(s) with most A\'s + Ex\'s : ',
    for item in list_sub:
        print item,
    print ''


def individual_full_performance(user_roll_num):
    """ Opens the erp performance link for the given roll num in user's default browser in a new tab. 

    Choice Route : 4.1 -> Enter Roll number
    Full Performance
    """
    url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
    webbrowser.open(url_to_scrape, new=2)


def individual_semester_display(user_roll_num, sem_num, content = ''):
    """ Display the grades of an individual for a particular semester along with SGPA. 

    Choice Route : 4.2 -> Enter Roll Number
    Particular Semester
    """
    # INCLUDE
    if content == '':
      url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
      fname = "Output.txt"
      content = connect(fname, url_to_scrape)
    # END INCLUDE
    # EXCLUDE
    # fname = 'divyansh.html'
    # with open(fname) as f:
    #     content = f.readlines()
    # END EXCLUDE
    name = find_name(user_roll_num, content)
    print ''
    print 'Name : ' + name
    print 'Roll Number : ' + user_roll_num
    index = 0
    sem_found = False
    table = PrettyTable(['Sub Name', 'Credits', 'Grade', 'Sub Type'])
    table.align = 'l'
    for line in content:
        if (line.find("<tr bgcolor=\"#FFF3FF\">") != -1 or line.find("<tr bgcolor=\"pink\">") != -1) and sem_found:
            currentLine = content[index + 2]
            matchObj = re.match( r'<td>(.*)</td>', currentLine, re.M|re.I)
            if matchObj != None and str(matchObj.group(1)).find("<b>") == -1:
                sub_name = str(matchObj.group(1))
                sub_name = sub_name.replace("&amp;", "&")
                currentLine = content[index + 4]
                matchObj = re.match(r'<td align="center">(.*?)<.*', currentLine, re.M|re.I)
                sub_credits = str(matchObj.group(1))
                currentLine = content[index + 5]
                matchObj = re.match(r'<td align="center">(.*?)<.*', currentLine, re.M|re.I)
                sub_grade = str(matchObj.group(1))
                if sub_grade == '':
                    sub_grade = '-'
                currentLine = content[index + 6]
                matchObj = re.match(r'<td align="center">(.*)</td>', currentLine, re.M|re.I)
                sub_type = str(matchObj.group(1))
                table.add_row([sub_name, sub_credits, sub_grade, sub_type])

        elif line.find("<tr><td bgcolor=\"#FFF3FF\" colspan=\"2\"><h3 align=\"center\">Semester no:") != -1:
            matchObj = re.match(r'<tr><td bgcolor="#FFF3FF" colspan="2"><h3 align="center">Semester no: ([1-9]).*', line, re.M|re.I)
            if matchObj:
                if sem_found:
                    return
                elif int(matchObj.group(1)) == sem_num:
                    sem_found = True
                    print 'Semester No.: ' + matchObj.group(1)
        elif line.find("<td><b>Semester Credit Taken") != -1 and sem_found:
            print table
            table.clear_rows()
            sg_found = False
            for line_ in content[index:]:
                if line_.find("SGPA") != -1 and line_.find("Additional") == -1:
                    if len(re.findall(r"[-+]?\d*\.*\d+", line_)) > 0:
                        try:
                            sg = float(re.findall(r"[-+]?\d*\.*\d+", line_)[0])
                            sg_found = True
                            break
                        except Exception:
                            sg = '--'
                            break
                    else:
                        break
            if sg_found:
                print "SGPA for this semester : " + str(sg)
            else:
                print "No SGPA available for this semester yet."
        index += 1
    # Control reaches here only if said semester is not found
    print "No records were found for " + user_roll_num + " for the semester number : " + str(sem_num)

def find_senior_year():
    today = datetime.date.today()
    current_year = float(today.year)
    current_month = int(today.month)
    if current_month >= 5:
        current_year += 0.6
    batchNum = int(math.floor((current_year - 2000.0) - 4.5))
    return batchNum

def find_sem_num(roll_num):
    
    user_year = float(roll_num[0:2])
    user_year += 0.5
    today = datetime.date.today()
    current_year = float(today.year) - 2000.0
    current_month = int(today.month)
    if current_month >= 5:
        current_year += 0.6
    return int((current_year - user_year)*2)




def take_main_choice():
    """ Take user input for main menu choice and proceed accordingly.

        Return bool, whether to return to main menu or not.
    """
    # default value, UPDATE after 1/5/2018
    user_roll_num = '14CS10008'
    # Available choices from main table
    # 5 will be used for exiting
    choices = ['1.0', '1.1', '1.2', '1.3', '1.4','2.1', '2.2', '2.3', '2.4', '3.1', '3.2', '3.3', '4']
    print "Enter your choice. To Exit, enter 4"
    print "Eg. \"1.0\" (without quotes) for Entire Semester Summariser Info"
    # Taking user input for choice
    choice = raw_input("")
    # Checking validity of choice entered.
    while choice not in choices:
        choice = raw_input("Please enter a valid choice :  ")
    if choice in ['2.1', '2.2', '2.3', '2.4']:
        # sub_choice = raw_input("Select 1) Individual    2) Full batch rank list :  ")
        # while sub_choice not in ['1', '2']:
        #     sub_choice = raw_input("Please enter valid sub choice again (1 or 2) :  ")
        if choice in ['2.1', '2.2']:
            user_roll_num, content = take_roll_num()
            print '\nCrunching Data... This may take a couple of minutes or more depending on your OS and internet connection.\n'
            # Individual Dep rank based on CG
            if choice == '2.1':
                dep_rank = find_dep_rank_individual(user_roll_num)
                if dep_rank == -1:
                    print "\nRecords don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered.\n"
                else:
                    print '\nDepartment Rank for ' + user_roll_num + ' is ' + str(dep_rank[0]) + ' out of ' + str(dep_rank[1]) + ' students.\n'
            # Individual Dep rank based on recent SGPA
            elif choice == '2.2':
                dep_rank, student_count = find_dep_rank_individual(user_roll_num, '2')
                if dep_rank == -1:
                    print "\nRecords don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered.\n"
                else:
                    print '\nDepartment Rank for ' + user_roll_num + ' on basis of most recent SGPA is ' + str(dep_rank) + ' out of ' + str(student_count) + ' students.\n'
        elif choice in ['2.3', '2.4']:
            year = take_year()
            dep = take_dep()
            msc_dep_bool = is_msc_dep(dep)
            print '\nCrunching Data... This may take a couple of minutes or more depending on your OS and internet connection.\n'
            if choice == '2.3':
                find_dep_rank_list_CG(year, dep, msc_dep_bool)
            elif choice == '2.4':
                find_dep_rank_list_SG(year, dep, msc_dep_bool)
    # elif choice in ['4.1', '4.2']:
    #     user_roll_num, content = take_roll_num() 
    #     if choice == '4.1':
    #         individual_full_performance(user_roll_num)
    #         print '\nThe result should have opened in your default web browser.\n'
    #     elif choice == '4.2':
    #         sem_num = take_sem_num()
    #         individual_semester_display(user_roll_num, sem_num, content)
    elif choice in ['1.0','1.1', '1.2', '1.3', '1.4']:
        dep = take_dep()
        sem_num = take_sem_num()
        print '\nCrunching Data... This may take couple of minutes or more depending on your OS and internet connection.\n'
        if choice == '1.1':
            find_depth_sub_grade_list(dep, sem_num, is_msc_dep(dep), True)
        elif choice == '1.2':
            get_br_and_elective_grade_list(dep, sem_num, False)
        elif choice == '1.3':
            dict_list = find_depth_sub_grade_list(dep, sem_num, is_msc_dep(dep), False)
            grade_dict = dict_list[2]
            find_subjects_by_difficulty_level(grade_dict)
        elif choice == '1.4':
            dict_list = find_depth_sub_grade_list(dep, sem_num, is_msc_dep(dep), False)
            grade_dict = dict_list[2]
            find_sub_most_x_f(grade_dict, 2)
            find_sub_most_x_f(grade_dict, 1)
        elif choice == '1.0':
            # if sem_num == 3:
            #     print '\nSUMMARY OF 3RD SEMESTER FOR THE ' + dep + ' DEPARTMENT BASED ON PREVIOUS YEAR'
            # else:
            #     print '\nSUMMARY OF ' + str(sem_num) +'TH SEMESTER FOR THE ' + dep +' DEPARTMENT BASED ON PREVIOUS YEAR'
            dict_list = find_depth_sub_grade_list(dep, sem_num, is_msc_dep(dep), True)
            grade_dict = dict_list[2]
            get_br_and_elective_grade_list(dep, sem_num, True, dict_list[0], dict_list[1])
            find_subjects_by_difficulty_level(grade_dict)
            find_sub_most_x_f(grade_dict, 2)
            find_sub_most_x_f(grade_dict, 1)
            find_sub_most_a_ex(grade_dict)
    elif choice in ['3.1', '3.2', '3.3']:
        if choice == '3.1':
            dep = take_dep()
            batchNum = find_senior_year()
            print '\nAccumulating data from ' + str(batchNum) + dep + ' batch for analyis : '
            lis = find_recent_sg_or_sg_list_batch(str(batchNum), dep, is_msc_dep(dep))
            total_SGPA = lis[0]
            total_SGPA_sq = lis[1]
            N = total_SGPA[8]
            table = PrettyTable(['Semester Number', 'Average SGPA', 'Variance in SGPA'])
            for i in range(0,8):
                variance = (float(total_SGPA_sq[i]) - total_SGPA[i]**2/float(N)) / float(N)
                table.add_row([i+1, round(total_SGPA[i]/float(N), 2), round(variance, 2)])
            print '\nThe following data is accumulated on basis of ' + str(batchNum) +  dep + ' batch :'
            print table
            print '\n'
        elif choice == '3.4':
            batchNum = find_senior_year()
            user_roll_num, content = take_roll_num()
            dep = user_roll_num[2:4]
            user_sem_num = find_sem_num(user_roll_num)
            if user_sem_num >= 8:
                print 'Sorry, No Prediction Patterns for Semesters 9-10.\n'
            else:
                print '\nAccumulating data from ' + str(batchNum) + dep + ' batch for analyis : '
                user_cg = find_recent_cg_individual(user_roll_num, content)
                total_CGPA, total_CGPA_sq = find_cg_list_batch(str(batchNum), dep, is_msc_dep(dep))
                N = total_CGPA[8]
                avg_CGPA = [x/float(N) for x in total_CGPA]
                avg_cg = avg_CGPA[user_sem_num - 1]
                if user_cg > avg_cg:
                    pos_factor =  max((user_cg - avg_cg)/0.20, 0.75)
                    neg_factor = max((user_cg - avg_cg)/0.25, 0.75)
                else:
                    neg_factor = max((avg_cg - user_cg)/0.20, 0.75)
                    pos_factor = max((avg_cg - user_cg)/0.25, 0.75)
                table = PrettyTable(['Semester Number', 'Predicted CGPA', 'Predicted Lowest Point', 'Predicted Highest Point'])
                for i in range(user_sem_num, 8):
                    diff = avg_CGPA[i] - avg_cg
                    variance = (float(total_CGPA_sq[i]) - total_CGPA[i]**2/float(N)) / float(N)
                    sdpos = variance/float(pos_factor)
                    sdneg = variance/float(neg_factor)
                    table.add_row([i+1, min(round(user_cg + diff, 2),10.0), min(round(user_cg + diff - sdneg/float(2), 2), 10.0), min(round(user_cg + diff + sdpos/float(2), 2), 10.0)])
                print '\nThe following data is accumulated on basis of ' + str(batchNum) +  dep + ' batch and your past CGPA data :'
                print table
                print '\n'
        elif choice == '3.3':
            batchNum = find_senior_year()
            user_roll_num, content = take_roll_num()
            dep = user_roll_num[2:4]
            user_sem_num = find_sem_num(user_roll_num)
            if user_sem_num >= 8:
                print 'Sorry, No Prediction Patterns for Semesters 9-10.\n'
            else:
                print '\nAccumulating data from ' + str(batchNum) + dep + ' batch for analyis : '
                user_sg = find_recent_sg_individual(user_roll_num, content)
                user_cg = find_cg_individual(user_roll_num, content)
                total_SGPA, total_SGPA_sq = find_recent_sg_or_sg_list_batch(str(batchNum), dep, is_msc_dep(dep))
                N = total_SGPA[8]
                avg_SGPA = [x/float(N) for x in total_SGPA]
                avg_sg = avg_SGPA[user_sem_num - 1]
                user_sg = (user_sg + user_cg*(user_sem_num)) / float(user_sem_num + 1)
                if user_sg > avg_sg:
                    diff_factor = 1 - min((user_sg - avg_sg)/2.5, 0.9)
                    pos_factor =  max((user_sg - avg_sg)/0.30, 0.5)
                    neg_factor = max((user_sg - avg_sg)/0.35, 0.5)
                else:
                    diff_factor = 1 
                    neg_factor = max((avg_sg - user_sg)/0.30, 0.5)
                    pos_factor = max((avg_sg - user_sg)/0.35, 0.5)
                table = PrettyTable(['Semester Number', 'Predicted SGPA', 'Predicted Lowest Point', 'Predicted Highest Point'])
                for i in range(user_sem_num, 8):
                    diff = avg_SGPA[i] - avg_sg
                    if diff > 0:
                        diff = diff*diff_factor
                    variance = (float(total_SGPA_sq[i]) - total_SGPA[i]**2/float(N)) / float(N)
                    sdpos = variance/float(pos_factor)
                    sdneg = variance/float(neg_factor)
                    table.add_row([i+1, min(round(user_sg + diff, 2),10.0), min(round(user_sg + diff - sdneg/float(2), 2), 10.0), min(round(user_sg + diff + sdpos/float(2), 2), 10.0)])
                print '\nThe following data is accumulated on basis of ' + str(batchNum) +  dep + ' batch and your past SGPA data :'
                print table
                print '\n'
        elif choice == '3.2':
            user_roll_num, content = take_roll_num()
            user_year = int(user_roll_num[0:2])
            dep = user_roll_num[2:4]
            user_sem_num = find_sem_num(user_roll_num)
            if user_sem_num >= 7:
                print 'Sorry, No Prediction Patterns for Semesters 8-10.\n'
            else:
                batchNum = user_year - 1
                print '\nAccumulating data from ' + str(batchNum) + dep + ' batch for analyis : '
                user_sg = find_recent_sg_individual(user_roll_num, content)
                total_SGPA, total_SGPA_sq = find_recent_sg_or_sg_list_batch(str(batchNum), dep, is_msc_dep(dep), '0', user_sem_num + 2)
                N = total_SGPA[user_sem_num + 2]
                avg_SGPA = [x/float(N) for x in total_SGPA]
                avg_sg = avg_SGPA[user_sem_num - 1]
                if user_sg > avg_sg:
                    diff_factor = 1 - min((user_sg - avg_sg)/2.5, 0.9)
                    pos_factor =  max((user_sg - avg_sg)/0.30, 0.5)
                    neg_factor = max((user_sg - avg_sg)/0.35, 0.5)
                else:
                    diff_factor = 1
                    neg_factor = max((avg_sg - user_sg)/0.30, 0.5)
                    pos_factor = max((avg_sg - user_sg)/0.35, 0.5)
                diff = avg_SGPA[user_sem_num] - avg_sg
                if diff > 0:
                    diff = diff*diff_factor
                variance = (float(total_SGPA_sq[user_sem_num]) - total_SGPA[user_sem_num]**2/float(N)) / float(N)
                sdpos = variance/float(pos_factor)
                sdneg = variance/float(neg_factor)
                print '\nThe following data is accumulated on basis of ' + str(batchNum) +  dep + ' batch and your past SGPA data :'
                print 'Predicted SGPA : ',
                print min(round(user_sg + diff, 2),10.0)
                print 'Predicted Lower Bound : ',
                print min(round(user_sg + diff - sdneg/float(2), 2), 10.0)
                print 'Predicted Upper Bound : ',
                print min(round(user_sg + diff + sdpos/float(2), 2), 10.0)
                print '\n'
                print 'PS. This data is based on more recent results than those computed in choice 3.2 and hence may vary.\n'
    elif choice == '4':
        print 'Exiting...'
        exit(0)
    return_choice = raw_input('\nReturn to main menu : \'r\' or Exit : \'e\' ? :  ')
    while return_choice not in ['r', 'e']:
        return_choice = raw_input('Please enter valid choice (r, e) :  ')
    if return_choice == 'r':
        return True
    elif return_choice == 'e':
        return False

if __name__ == "__main__":
    print "\n***** Welcome to CG Accumulator *****\n"
    # CONDITION TO CHECK FOR RESULTS AVAILABILITY WILL BE PLACED HERE
    # FOLLOWING BLOCK WILL BE PLACED AFTER PRINTING "***** Welcome to CG Accumulator *****"
    print "Establishing Connection ........"
    # connecting to a page containing info about latest version
    content = connect("Output.txt", 'http://cgaccumulator.blogspot.com/')
    # Checking availability of results.
    if not check_results_availability():
        print "\nSorry. Right now the results are not available due to ongoing upadations in the institute database."  
        key = raw_input("Press Enter to Exit.")
        exit(0)
    print '\nConnected!'
    # Checking for latest version
    check_for_update(content)  
    # Bool var storing user's choice to return to / display main menu.
    # Initially set as True, to display menu on start of program.
    main_menu_status = True
    while main_menu_status:
        # Main Menu content
        print '\n*** Main Menu ***'
        table = PrettyTable(['1.0 Semester Summariser', 'Department Rank', 'Departmental SGPA/CGPA Pattern Detection'])
        table.add_row(['1.1 Depth Subjects Grade List (Prev Yr.)', '2.1 Individual Department Rank Based on CGPA', '3.1 Average SGPA & Variance for All Semesters'])
        table.add_row(['1.2 Breadth & Elective Subjects Grade List (Prev yr.)','2.2 Individual Department Rank Based on Recent Results/SGPA', '3.2 Next Semester SGPA Predictor'])
        table.add_row(['1.3 Depth Subjects by Difficulty Level', '2.3 D.R vs CGPA Distribution for a Batch', '3.3 SGPA Predictor - All Semesters'])
        table.add_row(['1.4 Depth Subject with most F and Deregistrations', '2.4 D.R vs Recent SGPA Distribution for a Batch', ''])
        table.align = 'l'
        print table
        main_menu_status = take_main_choice()

    exit(0)
