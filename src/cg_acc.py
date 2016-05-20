# Developed by : Avikalp Srivastava

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
# [pip, requests, operator, webbrowser, bs4, prettytable]

# Usage : Sort dictionary based on keys / values
import operator
# Usage : open a link in user's default web browser.
import webbrowser
# Usage : Connect to a link
import requests 
# Usage : 
from bs4 import BeautifulSoup
# Usage : To display data in tables
from prettytable import PrettyTable
# Usage : Regular Expressions for scraping html text
import re
# Usage : While generating previous year depth subj grade list
import datetime
# Usage : floor function
import math

# Stores the version of the software
# Used for Software Update, after matching latest version number available from http://cgaccumulator.blog.com/
# TODO : Not implemented as of now
version = 1.0


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
        r = requests.get(url_to_scrape)
        soup = BeautifulSoup(r.text, "html.parser")
        with open(fname, "w") as text_file:
            text_file.write("{}".format(soup))
        with open(fname) as f:
            content = f.readlines()
        return content
    except requests.exceptions.RequestException:
        # Static var storing then number of times attempt to connect has failed
        # If >=4, then we assume that user is not connected to the internet.
        connect.counter += 1
        if connect.counter >= 4:
            connect.counter = 0
            reconnect_choice = raw_input('\nYou don\'t seem to be having internet connectivity. Enter r to try again, x to exit :  ')
            while reconnect_choice not in ['r', 'x']:
                reconnect_choice = raw_input('Invalid choice! Please enter r to try reconnecting again, or enter x to exit :  ')
            if reconnect_choice == 'r':
                print 'Retrying....'
                return connect(fname, url_to_scrape)
            else:
                print "\nExiting...."
                exit(0)
        else:
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
        if line.find("Students Performance will be enabled after SENATE Approval") != -1:
            return False
    return True


def check_roll_num_validity(user_roll_num):
    """Checks validity of user_roll_num
        Return type : bool
    """
    # List storing available departments in IIT Kharagpur.
    departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
    # List of Msc departments in IIT Kharagpur.
    msc_dep_list = ["GG", "EX", "MA", "CY", "HS", "PH"]
    # Currently, software supports students with starting years as 2012, 2013, 2014, 2015
    # Requires Annual UPDATE
    years = ["12","13","14","15"]

    # Check that first 2 chars are present in years, next 2 in departments, length is 9 and the last 5 chars correspond to an integer
    if user_roll_num[0:2] in years and user_roll_num[2:4] in departments and len(user_roll_num) == 9 and is_int(user_roll_num[4:9]):
        num = int(user_roll_num[4:9])
        # If the department belongs to Msc dep list, the last five digits should be in the 20000 series
        if user_roll_num[2:4] in msc_dep_list:
            if 20000 < num < 20100:
                url = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + user_roll_num
                content = connect('Output.txt', url)
                return len(content) > 50
            else:
                return False
        # Else for other deps, last five digits should be in 10000 or 30000 series
        elif (10000 < num < 10100) or (30000 < num < 30100):
            url = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + user_roll_num
            content = connect('Output.txt', url)
            return len(content) > 50
        else:
            return False
    else:
        return False


def take_roll_num():
    """ Take a roll number input from user till it is valid, then return it.
        Return type : str
    """
    # Taking roll_num input
    roll_num = raw_input("Enter Roll Number :  ")
    # Converting user inp to upper (14cs10008 - 14CS10008) and checking validity
    # while not check_roll_num_validity(roll_num.upper()):
    #     roll_num = raw_input("Please enter valid Roll Number :  ")
    return roll_num.upper()


def take_year():
    """Take user input for year, validate and return year
        Return type : str
    """
    # Currently, software supports students with starting years as 2012, 2013, 2014, 2015
    # UPDATE : Annual
    years = ["12", "13", "14", "15"]
    year = raw_input("Enter start year for the batch (Choices : 12, 13, 14, 15) :  ")
    while year not in years:
        year = raw_input("Please enter valid year :  ")
    return year


def take_dep():
    """ Take user input for department, validate and return department
        Return type : str
    """
    # List storing available departments in IIT Kharagpur.
    departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
    dep = raw_input("Enter Department (e.g \"CE\" for civil) :  ")
    # Converting user entered input to uppercase, in case it isn't.
    dep = dep.upper()
    while dep not in departments:
        print "Please enter a valid department!"
        dep = raw_input("Enter Valid Department again : ")
    return dep


def take_sem_num():
    """ Take user input for semester number, validate and return
        Return type : int
    """
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
    prev_year = math.floor(current_year - (sem_num + 1)/float(2))
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


# Choice Route - 1.1 -> 1 -> Enter Roll Number 
# CGPA -> Individual
def find_cg_individual(roll_num, content = ''):
    """ Find and return CGPA for given roll num. Returns -1 if no results exist for the given roll num.
        Return type : float , context : CGPA for the given roll_num
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


# Choice Route - 1.1 -> 2 -> Enter year -> Enter dep
# CGPA -> Batch
def find_cg_batch(year, dep, msc_dep_bool):
    """ Prints the CG list for the batch with given year and dep. Table contents : Roll Number, CGPA, Name """
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
            table.add_row([rollno, name, cg])
        # If the subject is not Msc, then we make a transition to dual degree students
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
        # Conditions for ending, self explanatory.
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    print '\nCGPA list for batch : ' + str(year) + '-' + dep
    print table
    print '\nTotal students = ' + str(student_count)
    print 'Average CGPA =  ',
    print  str(cg_total/float(student_count)) if student_count > 0 else '-'
    print ''


# Choice Route - 1.2 -> 1 -> Enter Roll Number
# SGPA List -> Individual
def find_sg_list_individual(user_roll_num, content = ''):
    """ Return SG list for an individual """
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


# Choice Route : 1.2 -> 2 -> Enter Year -> Enter Dep or 1.3 -> 2 -> Enter Year -> Enter Dep
# SGPA List -> Batch or Recent SGPA -> Individual
def find_recent_sg_or_sg_list_batch(year, dep, msc_dep_bool, choice = '0'):
    """ Choice = '0' for Sg list, '1' for Recent sg. """
    roll_count = 10000
    if msc_dep_bool:
        roll_count = 20000
    student_count = 0
    bad_count = 0
    sg_total = 0.00
    fname = 'Output.txt'
    table = None
    if choice == '0':
        table = PrettyTable(['Roll Num', 'Name', 'SGPA List'])
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
            student_count += 1
            if choice == '0':
                sg_list = find_sg_list_individual(rollno, content)
            elif choice == '1':
                sg = find_recent_sg_individual(rollno, content)
                sg_total += sg
            name = find_name(rollno, content)
            if (choice == '0' and len(sg_list) != 0) or (choice == '1' and sg != -1):
                if choice == '0':
                    table.add_row([rollno, name, str(sg_list)])
                    del sg_list[:]
                elif choice == '1':
                    table.add_row([rollno, name, sg])
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    if choice == '0':
        print '\nSGPA list for batch ' + year + '-' + dep + ' : '
    elif choice == '1':
        print '\nRecent SGPA list for batch ' + year + '-' + dep + ' : '
    print table
    print '\nTotal students = ' + str(student_count)
    if choice == '1':
        print 'Average SG this recent semester for the batch ' + year + '-' + dep + ' : ',
        print str(sg_total/float(student_count)) if student_count > 0 else '-'
    print ''


# Choice Route : 1.3 -> 1 -> Enter Roll Number
# Recent SGPA -> Individual
def find_recent_sg_individual(user_roll_num, content = ''):
    """ Return most recent SGPA for an individual """
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


# Choice Route : 2.1 -> 1 -> Enter Roll Number or 2.2 -> 1 -> Enter Roll Number 
# Department Rank Based on CG -> Inidividual or Department Rank Based on SG -> Inidividual
def find_dep_rank_individual(roll_num, choice = '1', content = ''):
    """ Choice = '1' - CG based, Choice = '2' - SG based. Returns -1 if no record exists.
        Return type : int, context : department rank
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
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    dep_rank = [dep_rank, student_count]
    return dep_rank


# Choice Route : 2.1 -> 2 -> Enter Year -> Enter Dep
# Department Rank Based on CG -> Batch
def find_dep_rank_list_CG(year, dep, msc_dep_bool):
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
        # VULNERABLE
        if len(content) < 50:
            bad_count += 1
        else:
            bad_count = 0
            student_count += 1
            cg = find_cg_individual(rollno, content)
            name = find_name(rollno, content)
            # Handling duplicate names. Will label more than 2 dups in same fashion 
            try:
                dep_dict[name]
                dep_dict[name + ' (2)'] = cg
            except KeyError:
                dep_dict[name] = cg
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    # Sorting names in dict acc to CG in descending order.
    # TODO : analyze if this is stable or not. If not, make it -_-
    sorted_dep_dict = sorted(dep_dict.items(), key=operator.itemgetter(1), reverse=True)
    index = 0
    prev_rank = 1
    print '\nDepartment Rank list for the batch : ' + year + '-' + dep + ' based on CGPA : '
    table = PrettyTable(['Rank', 'Name', 'CGPA'])
    for item in sorted_dep_dict:
        if index != 0 and sorted_dep_dict[index][1] == sorted_dep_dict[index - 1][1]:
            table.add_row([prev_rank, item[0], item[1]])
        else:
            table.add_row([index + 1, item[0], item[1]])
            prev_rank = index + 1
        index += 1
    print table
    print ''


# Choice Route : 2.2 -> 2 -> Enter Year -> Enter Dep
# Department Rank Based on SG -> Batch
def find_dep_rank_list_SG(year, dep, msc_dep_bool):
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
        # VULNERABLE
        if sg == -1:
            bad_count += 1
        else:
            bad_count = 0
            student_count += 1
            name = find_name(rollno, content)
            dep_dict[name] = sg
            # Handling duplicate names. Will label more than 2 dups in same fashion 
            try:
                dep_dict[name]
                dep_dict[name + ' (2)'] = sg
            except KeyError:
                dep_dict[name] = sg
        if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
            roll_count = 30000
        elif bad_count >= 5 and ((not msc_dep_bool and roll_count > 30000) or msc_dep_bool):
            break
    # Sorting names in dict acc to SG in descending order.
    # TODO : analyze if this is stable or not. If not, make it -_-
    sorted_dep_dict = sorted(dep_dict.items(), key=operator.itemgetter(1), reverse=True)
    index = 0
    prev_rank = 1
    print '\nDepartment Rank list for the batch : ' + year + '-' + dep + ' based on recent SGPA : '
    table = PrettyTable(['Rank', 'Name', 'SG'])
    for item in sorted_dep_dict:
        if index != 0 and sorted_dep_dict[index][1] == sorted_dep_dict[index - 1][1]:
            table.add_row([prev_rank, item[0], item[1]])
        else:
            table.add_row([index + 1, item[0], item[1]])
            prev_rank = index + 1
        index += 1
    print table
    print ''


def get_depth_sub_name_list(year, dep, sem_num, content = ''):
    """ Return list of name of depth subjects (excluding EAA) for this batch """
    sub_name_list = []
    # INCLUDE
    # tmp_roll_count = 10000
    # if is_msc_dep(dep):
        # tmp_roll_count = 20000
    # while len(content) <= 50:
    #   tmp_roll_count += 1
    #   user_roll_num = year + dep + str(tmp_roll_count)
    #   url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
    #   fname = "Output.txt"
    #   content = connect(fname, url_to_scrape)
    # END INCLUDE
    # EXCLUDE
    fname = 'divyansh.html'
    with open(fname) as f:
        content = f.readlines()
    # END EXCLUDE
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
                    # print 'Semester No.: ' + matchObj.group(1)
        index += 1
    return sub_name_list


# Relocate this function
def gen_depth_sub_grade_list(year, dep, msc_dep_bool, sub_dict):
    """ Generate no. of grades list for the depths subjects of given batch for the given sem_num """
    fname = 'Output.txt'
    bad_count = 0
    last5 = 10000
    if msc_dep_bool:
        last5 = 20000
    tmp = 28                                                                #######################
    names = ['divyansh.html', 'divyansh2.html', 'divyansh3.html']       #######################
    while tmp != 0:             #######################
        tmp -= 1                ######################
        last5 += 1
        rollno = year + dep + str(last5)
        # url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(rollno)           ########################
        # content = connect(fname, url_to_scrape)                                                                               ########################
        fname = names[tmp % 3]          ########################
        with open(fname) as f:          ########################
            content = f.readlines()     ########################
        if len(content) < 40 :
            bad_count += 1
        else :
            for sub in sub_dict:
                str_to_find = '<td>' + sub + '</td>'
                index = 0
                for line in content:
                    if line.find(str_to_find) != -1:
                        currentLine = content[index + 3]
                        matchObj = re.match( r'<td align="center">([A,B,C,D,P,F,X])</td>', currentLine, re.M|re.I)
                        if not matchObj:
                            matchObj = re.match( r'<td align="center">([E])X</td>', currentLine, re.M|re.I)
                        if matchObj:
                            if matchObj.group(1) == 'E':
                                sub_dict[sub][0] += 1
                            elif matchObj.group(1) == 'A':
                                sub_dict[sub][1] += 1
                            elif matchObj.group(1) == 'B':
                                sub_dict[sub][2] += 1
                            elif matchObj.group(1) == 'C':
                                sub_dict[sub][3] += 1
                            elif matchObj.group(1) == 'D':
                                sub_dict[sub][4] += 1
                            elif matchObj.group(1) == 'P':
                                sub_dict[sub][5] += 1
                            elif matchObj.group(1) == 'F':
                                sub_dict[sub][6] += 1
                            elif matchObj.group(1) == 'X':
                                sub_dict[sub][7] += 1
                        break
                    index += 1
        if bad_count >= 5 and not msc_dep_bool and last5 < 30000:
            last5 = 30000
        if bad_count >= 5 and (msc_dep_bool or last5 > 30000):
            return ##################################


# Choice Route : 3.1 -> Enter Semester Number
# Depth Subjects Grade List
def find_depth_sub_grade_list(dep, sem_num, msc_dep_bool, print_table = 'False'):
    prev_year = get_prev_year(int(sem_num))
    depth_sub_name_list = get_depth_sub_name_list(prev_year, dep, sem_num)
    grade_dict = {}
    for item in depth_sub_name_list:
        # List corresponds to Ex, A, B, C, D, P, F, X
        grade_dict[item] = [0, 0, 0, 0, 0, 0, 0, 0]
    gen_depth_sub_grade_list(prev_year, dep, msc_dep_bool, grade_dict)
    if not print_table:
        return grade_dict
    # Else :
    print ''
    print 'Previous year grade list of depth subjects for semester number ' + str(sem_num) + ' for the ' + dep + ' department :'
    table = PrettyTable(['Sub Name', 'Ex', 'A', 'B', 'C', 'D', 'P', 'F', 'X'])
    table.align = 'l'
    for item in grade_dict:
        table.add_row([item, grade_dict[item][0],  grade_dict[item][1], grade_dict[item][2], grade_dict[item][3],
            grade_dict[item][4], grade_dict[item][5],  grade_dict[item][6], grade_dict[item][7]])
    print table
    return grade_dict
    # sub_most_a_ex = find_sub_most_a_ex(grade_dict)
    # print sub_most_a_ex
    # sub_most_x = find_sub_most_x_f(grade_dict, 2)
    # print sub_most_x
    # find_subjects_by_difficulty_level(grade_dict)
    # TODO : Rest of the shit


def find_sum(alist):
    csum = 0
    factor = 0
    for item in alist:
        csum += item*factor
        factor += 1
    return csum


def find_subjects_by_difficulty_level(grade_dict):
    result_list = []
    sum_dict = {}
    for item in grade_dict:
        csum = find_sum(grade_dict[item])
        sum_dict[item] = csum
    sorted_sum_dict = sorted(sum_dict.items(), key = operator.itemgetter(1), reverse = True)
    print 'Following subjects have been sorted in decreasing level of difficulty according to their previous yr. grade distribution.'
    table = PrettyTable(['Subject Name', 'Difficulty Score'])
    table.align = 'l'
    table.align['Difficulty Score'] = 'c'
    for item in sorted_sum_dict:
        table.add_row([item[0], item[1]])
    print table


def find_sub_most_x_f(grade_dict, choice):
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
    if maxim == 0:
        return sub_list
    for item in grade_dict:
        if grade_dict[item][idx] == maxim:
            sub_list.append(item)
    return sub_list


def find_sub_most_a_ex(grade_dict):
    maxim = 0
    for item in grade_dict:
        if grade_dict[item][0] + grade_dict[item][1] > maxim:
            maxim = grade_dict[item][0] + grade_dict[item][1]
    list_sub = []
    for item in grade_dict:
        if grade_dict[item][0] + grade_dict[item][1] == maxim:
            list_sub.append(item)
    return list_sub


# Choice Route : 4.1 -> Enter Roll Number
# Full Performance
def individual_full_performance(user_roll_num):
    """ Opens the erp performance link for the given roll num in user's default browser in a new tab """
    url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
    webbrowser.open(url_to_scrape, new=2)


# Choice Route : 4.2 -> Enter Roll Number
# Particular Semester
def individual_semester_display(user_roll_num, sem_num, content = ''):
    """ Display the grades of an individual for a particular semester along with SGPA. """
    # INCLUDE
    # if content == '':
    #   url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
    #   fname = "Output.txt"
    #   content = connect(fname, url_to_scrape)
    # END INCLUDE
    # EXCLUDE
    fname = 'divyansh.html'
    with open(fname) as f:
        content = f.readlines()
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
        # elif line.find("</table>") != -1 and line.find("</td>") == -1:
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


def take_main_choice():
    """ Take user input for main menu choice and proceed accordingly.

        Return bool, whether to return to main menu or not.
    """
    # default value, UPDATE after 1/5/2018
    user_roll_num = '14CS10008'
    # Available choices from main table
    # 5 will be used for exiting
    choices = ['1.1', '1.2', '1.3', '2.1', '2.2', '3.0', '3.1', '3.2', '3.3', '3.4', '4.1', '4.2', '5']
    print "Enter your choice. To Exit, enter 5"
    print "Eg. \"1.1\" (without quotes) for CGPA list"
    # Taking user input for choice
    choice = raw_input("")
    # Checking validity of choice entered.
    while choice not in choices:
        choice = raw_input("Please enter a valid choice :  ")
    # Choices 1.1, 1.2, 1.3 further require a sub choice of Individual / Batch list
    if choice in ['1.1', '1.2', '1.3']:
        sub_choice = raw_input("Select - 1) Individual         2) Batch List :  ")
        while sub_choice not in ['1', '2']:
            sub_choice = raw_input("Please enter valid sub choice again (1 or 2) :  ")
        # If asked for an individual
        if sub_choice == '1':
            user_roll_num = take_roll_num()
            name = find_name(user_roll_num)
            # Individual CGPA asked
            if choice == '1.1':
                user_cg = find_cg_individual(user_roll_num)
                # Checking that records exist for this roll num
                if user_cg != -1:
                    print "\nCGPA for " + name + " is : " + str(user_cg) + "\n"
                else:
                    print "\nRecords don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered.\n"
            # Individual SGPA list
            elif choice == '1.2':
                sg_list = find_sg_list_individual(user_roll_num)
                num_semesters = len(sg_list)
                if num_semesters > 0:
                    print '\nSGPA list for ' + name + ' : '
                    table = PrettyTable(['Semester Number', 'SGPA'])
                    for i in range(num_semesters, 0, -1):
                        table.add_row([i, sg_list[num_semesters - i]])
                    print table
                else:
                    print "\nRecords don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered.\n"
                print ''
            # Individual - Most recent SGPA
            elif choice == '1.3':
                sg = find_recent_sg_individual(user_roll_num)
                if sg != -1:
                    print '\nMost recent SGPA for ' + name + ' is : ' + str(sg)
                else:
                    print "\nRecords don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered.\n"
                print ''
        # Batch List case
        elif sub_choice == '2':
            year = take_year()
            dep = take_dep()
            msc_dep_bool = is_msc_dep(dep)
            print '\nCrunching Data... This may take a couple of minutes or more depending on your OS and internet connection.\n'
            # Batch List - CGPA
            if choice == '1.1':
                find_cg_batch(year, dep, msc_dep_bool)
            # Batch List - SGPA List
            elif choice == '1.2':
                find_recent_sg_or_sg_list_batch(year, dep, msc_dep_bool, '0')
            # Bathc List - Recent SGPA
            elif choice == '1.3':
                find_recent_sg_or_sg_list_batch(year, dep, msc_dep_bool, '1')
    # BASIC LISTS ALL DONE!!!!!

    elif choice in ['2.1', '2.2']:
        sub_choice = raw_input("Select 1) Individual    2) Full batch rank list :  ")
        while sub_choice not in ['1', '2']:
            sub_choice = raw_input("Please enter valid sub choice again (1 or 2) :  ")
        if sub_choice == '1':
            user_roll_num = take_roll_num()
            name = find_name(user_roll_num)
            # Individual Dep rank based on CG
            if choice == '2.1':
                dep_rank = find_dep_rank_individual(user_roll_num)
                if dep_rank == -1:
                    print "\nRecords don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered.\n"
                else:
                    print "\nDepartment Rank for " + name + " is " + str(dep_rank[0]) + 'out of ' + str(dep_rank[1]) + ' students.'
                print ''
            # Individual Dep rank based on recent SGPA
            elif choice == '2.2':
                find_dep_rank_individual(user_roll_num, '2')
                if dep_rank == -1:
                    print "\nRecords don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered.\n"
                else:
                    print "\nDepartment Rank for " + name + " on basis of most recent SGPA is " + str(dep_rank[0]) + 'out of ' + str(dep_rank[1]) + ' students.'
            print ''
        elif sub_choice == '2':
            year = take_year()
            dep = take_dep()
            msc_dep_bool = is_msc_dep(dep)
            print '\nCrunching Data... This may take a couple of minutes or more depending on your OS and internet connection.\n'
            if choice == '2.1':
                find_dep_rank_list_CG(year, dep, msc_dep_bool)
            elif choice == '2.2':
                find_dep_rank_list_SG(year, dep, msc_dep_bool)
    elif choice in ['4.1', '4.2']:
        user_roll_num = take_roll_num()
        if choice == '4.1':
            individual_full_performance(user_roll_num)
            print '\nThe result should have opened in your default web browser.\n'
        elif choice == '4.2':
            sem_num = take_sem_num()
            individual_semester_display(user_roll_num, sem_num)
    elif choice in ['3.0','3.1', '3.2', '3.3', '3.4']:
        dep = take_dep()
        sem_num = take_sem_num()
        print '\nCrunching Data... This may take couple of minutes or more depending on your OS and internet connection.\n'
        if choice == '3.1':
            find_depth_sub_grade_list(dep, sem_num, is_msc_dep(dep), True)
        elif choice == '3.2':
            # TODO
            print 'pass'
            pass
        elif choice == '3.3':
            # TODO
            print 'pass'
            pass
        elif choice == '3.4':
            # TODO
            print 'pass'
            pass
        elif choice == '3.0':
            print 'pass'
            pass
            # TODO
    elif choice == '5':
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
    # TODO : Check for latest version
    # CONDITION TO CHECK FOR RESULTS AVAILABILITY WILL BE PLACED HERE
    # FOLLOWING BLOCK WILL BE PLACED AFTER PRINTING "***** Welcome to CG Accumulator *****"
    print "Establishing Connection ........"
    # connecting to a default performance page.
    # INCLUDE once ready to test
    content = connect("Output.txt", "https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=14CS10008")
    print '\nConnected!'
    # Checking availability of results.
    # if not check_results_availability():
    #     print "Sorry. Right now the results are not available due to ongoing upadations in the institute database."
    #     key = raw_input("Press Enter to Exit.")
    #     exit(0)
    # END INCLUDE
    # Bool var storing user's choice to return to / display main menu.
    # Initially set as True, to display menu on start of program.
    main_menu_status = True
    while main_menu_status:
        # Main Menu content
        print '\n*** Main Menu ***'
        table = PrettyTable(['Basic Lists / Info', 'Department Rank' , '3.0 Semester Summariser', 'Individual Grade Summariser'])
        table.add_row(['1.1 CGPA','2.1 Based on CG', '3.1 Depth Subjects Grade List (Prev Yr.)', '4.1 Full Performance'])
        table.add_row(['1.2 SGPA', '2.2 Based on recent SG','3.2 Breadth & Elective Subjects Grade List (Prev yr.)','4.2 Particular Semester'])
        table.add_row(['1.3 Most Recent SGPA','', '3.3 Subjects by Difficulty Level', ''])
        table.add_row(['','', '3.4 Subject with most F and Deregistrations', ''])
        table.align = 'l'
        print table
        main_menu_status = take_main_choice()
        # find_depth_sub_grade_list('CS', 4, False)

