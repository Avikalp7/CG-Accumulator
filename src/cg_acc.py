# Author : Avikalp Srivastava

# KEYS
# UPDATE : These are followed by a date and values that need to be updated when that date arrives. (PS can be automated by datetime, but i don't trust that for 1 second.)
# Issue : Minor to Semi-Major Issues. Please fix.
# TODO : Enhancements. Please make some. 
# VULNERABLE : Code that might break , generally if something unusual happens. Please make the code more robust.

# TODO List
# 
# Cache 
# Address Vulnerability of performing .find() on user given data
# 

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
# Issue : Unused Import?
import time


def is_number(s):
    """
    Check if given var is / can be converted to float
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_int(s):
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

	Use the textfile with name fname for the parsed HTML
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
	except Exception:
		print "ConnectionError"
		print "Retrying...."
		# Static var storing then number of times attempt to connect has failed
		# if >=4, then we assume that user is not connected to the net.
		counter += 1
		if(counter >= 4):
			counter = 0
			reconnect_choice = raw_input("You don't seem to be having internet connectivity. Enter r to try again, x to exit.")
			while reconnect_choice not in ['r', 'x']:
				reconnect_choice = raw_input("Invalid choice! Please enter r to try reconnecting again, or enter x to exit.")
			if reconnect_choice == 'r':
				return connect(fname, url_to_scrape)
			else:
				print "Exiting."
				exit(0)
		else:
			return connect(fname, url_to_scrape)
connect.counter = 0


def check_results_availability():
	""" Check if results are available at the moment. Return status. """
	fname = "Output.txt"
	# UPDATE (01/07/2018)
	url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=14CS10008'
	content = connect(fname, url_to_scrape)
	for line in content:
		# VULNERABLE
		# Change to other HTML conditions
		if line.find("Students Performance will be enabled after SENATE Approval") != -1:
			return False
	return True

def check_roll_num_validity(user_roll_num, years, departments, msc_dep_list):
	if user_roll_num[0:2] in years and user_roll_num[2:4] in departments and len(user_roll_num) == 9 and is_int(user_roll_num[4:9]):
		num = int(user_roll_num[4:9])
		if user_roll_num[2:4] in  msc_dep_list:
			return num > 20000 and num < 20100 
		else:
			return (num > 10000 and num < 10100) or (num > 30000 and num < 30100)
	else:
		return False

def take_roll_num():
	""" Take a roll number input from user till it is valid, then return it. """
	# List storing available departments in IIT Kharagpur.
	departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
	# List of Msc departments in IIT Kharagpur.
	msc_dep_list = ["GG", "EX", "MA", "CY", "HS", "PH"]
	# Currently, software supports students with starting years as 2012, 2013, 2014, 2015
	# Requires Annual UPDATE
	years = ["12","13","14","15"]
	# Taking roll_num input
	roll_num = raw_input("Enter Roll Number :  ")
	while not check_roll_num_validity(roll_num.upper(), years, departments, msc_dep_list):
		roll_num = raw_input("Please enter valid Roll Number :  ")
	return roll_num.upper()

def find_cg_individual(roll_num, content = ''):
	""" Find and return CGPA for given roll num. Returns -1 if no results exist for the given roll num.""" 
	# If HTML content for the roll_num has not been passed, make request and get it.
	if content == '':
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(roll_num)
		fname = "Output.txt"
		content = connect(fname, url_to_scrape)
	# VULNERABLE
	# Generally, if a roll number is invalid, the HTML content of the page is less than 40 lines.
	# Can be relaced by other robust methods, such as if name == "" etc.
	if len(content) < 40:
		return -1
	else:
		for line in content:
			if choice == "1" and line.find("CGPA") != -1 and line[4] != "<" and is_number(line[31:35]):
				return float(line[31:35])


def find_cg_batch(year, dep, msc_dep_bool):
	""" Prints the CG list for the batch with given year and dep. Table contents : Roll Number, CGPA, Name """
	roll_count = 10000
	if msc_dep_bool:
		roll_count = 20000
	student_count = 0
	bad_count = 0
	table = PrettyTable(['Roll Num', 'CGPA', 'Name'])
	while True:
		roll_count += 1
		student_count += 1
		rollno = str(year) + str(dep) + str(roll_count)
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
		fname = 'Output.txt'
		content = connect(fname, url_to_scrape)
		cg_total = 0.00
		# VULNERABLE
		if len(content) < 40:
			bad_count += 1
			student_count -= 1
		else:
			bad_count = 0
			cg = find_cg_individual(rollno, content)
			if cg != -1:
				cg_total += cg
			name = find_name(rollno, content)
			table.add_row([str(rollno), cg, name])
			# print "Roll Num : " + str(rollno) + "	CG : " + str(cg) + "	Name : " + str(name)
		if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
			roll_count = 30000
		elif bad_count >= 5 and ( (not msc_dep_bool and roll_count > 30000) or msc_dep_bool ):
			break
	print ''
	print table
	print ''
	print 'Total students = ' + str(student_count)	
	print 'Average CG =  ' + str(cg_total / student_count)
	print ''


def find_recent_sg_individual(user_roll_num, content = ''):
	""" Return most recent SGPA for an individual """
	user_sg = 0.00
	if content == '':
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
		fname = "Output.txt"
		content = connect(fname, url_to_scrape)
	# VULNERABLE
	if len(content) < 40:
		return -1
	else:
		# Traversing whole file and appending SGPA's to sg_list
		for line in content:
			if line.find("SGPA") != -1 and is_number(line[25:29]):
				user_sg = float(line[25:29])
				break
		return user_sg

def find_sg_list_individual(user_roll_num, content = ''):
	""" Return SG list for an individual """
	sg_list = []
	if content == '':
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
		fname = "Output.txt"
		content = connect(fname, url_to_scrape)
	# VULNERABLE
	if len(content) < 40:
		return []
	else:
		# Traversing whole file and appending SGPA's to sg_list
		for line in content:
			if line.find("SGPA") != -1 and is_number(line[25:29]):
				sg_list.append(str(line[25:29]))
		return sg_list

def find_recent_sg_or_sg_list_batch(year, dep, msc_dep_bool, choice = '0'):
	""" Choice = '0' for Sg list, '1' for recent sg. """
	roll_count = 10000
	if msc_dep_bool:
		roll_count = 20000
	student_count = 0
	bad_count = 0
	sg_total = 0.00
	if choice == '0':
		table = PrettyTable(['Roll Num', 'SGPA List', 'Name'])
	elif choice == '1':
		table = PrettyTable(['Roll Num', 'Recent SGPA', 'Name'])
	while True:
		roll_count += 1
		student_count += 1
		rollno = str(year) + str(dep) + str(roll_count)
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
		fname = 'Output.txt'
		content = connect(fname, url_to_scrape)
		# VULNERABLE
		if len(content) < 40:
			bad_count += 1
			student_count -= 1
		else:
			bad_count = 0
			if choice == '0':
				sg_list = find_sg_list_individual(rollno, content)
			elif choice == '1':
				sg = find_recent_sg_individual(rollno, content)
				sg_total += sg
			name = find_name(rollno, content)
			if (choice == '0' and sg_list != -1) or (choice == '1' and sg != -1):
				if choice == '0':
					table.add_row([str(rollno), str(sg_list), name])
					# print "Roll Num : " + str(rollno) + "	SGPA list : " + str(sg_list) + "	Name : " + str(name)
					del sg_list[:]
				elif choice == '1':
					table.add_row([str(rollno), str(sg), name])
					# print "Roll Num : " + str(rollno) + "	Recent SGPA : " + str(sg) + "	Name : " + str(name)
		if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
			roll_count = 30000
		elif bad_count >= 5 and ( (not msc_dep_bool and roll_count > 30000) or msc_dep_bool ):
			break
	print table
	print ''
	print 'Total students = ' + str(student_count)
	if choice == '1':
		print 'Average SG this recent semester for the department ' + dep + ' :  ' + str(sg_total / student_count)
	print ''

def find_dep_rank_individual(roll_num, content = ''):
	""" Returns -1 if no record exists """
	if content == '':
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(roll_num)
		fname = "Output.txt"
		content = connect(fname, url_to_scrape)
	user_cg = find_cg_individual(roll_num, content)
	if user_cg == -1:
		return -1
	# Extracting dep and year from given roll num
	year = roll_num[0:2]
	dep = roll_num[2:4]
	last_five = int(roll_num[4:9])
	if last_five > 20000 and last_five < 30000:
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
		student_count += 1
		rollno = str(year) + str(dep) + str(roll_count)
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
		fname = 'Output.txt'
		content = connect(fname, url_to_scrape)
		# VULNERABLE
		if len(content) < 40:
			bad_count += 1
			student_count -= 1
		else:
			bad_count = 0
			cg = find_cg_individual(rollno, content)
			if cg > user_cg:
				dep_rank += 1
		if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
			roll_count = 30000
		elif bad_count >= 5 and ( (not msc_dep_bool and roll_count > 30000) or msc_dep_bool ):
			break
	return dep_rank		
	# print ''
	# print 'Department Rank for ' + str(roll_num) + ' is ' + str(dep_rank) + ' among ' + str(student_count) + ' students.'
	# print ''

def find_dep_rank_list(year, dep, msc_dep_bool):
	roll_count = 10000
	if msc_dep_bool:
		roll_count = 20000
	student_count = 0
	bad_count = 0
	dep_dict = {}
	while True:
		roll_count += 1
		student_count += 1
		rollno = str(year) + str(dep) + str(roll_count)
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
		fname = 'Output.txt'
		content = connect(fname, url_to_scrape)
		# VULNERABLE
		if len(content) < 40:
			bad_count += 1
			student_count -= 1
		else:
			bad_count = 0
			cg = find_cg_individual(rollno, content)
			name = find_name(rollno, content)
			dep_dict[name] = cg
		if bad_count >= 5 and not msc_dep_bool and roll_count < 30000:
			roll_count = 30000
		elif bad_count >= 5 and ( (not msc_dep_bool and roll_count > 30000) or msc_dep_bool ):
			break
	# Sorting names in dict acc to CG in descending order.
	# TODO : analyze if this is stable or not. If not, make it -_-
	sorted_dep_dict = sorted(dep_dict.items(), key = operator.itemgetter(1), reverse = True)
	index = 0
	prev_rank = 1
	print 'Department Rank list for the dep : ' + dep
	table = PrettyTable(['Rank', 'CG', 'Name'])
	for item in sorted_dep_dict:
		if index != 0 and sorted_dep_dict[index][1] == sorted_dep_dict[index - 1][1]:
			table.add_row([prev_rank, item[1], item[0]])
			# print 'Rank : ' + str(prev_rank) + '		CG : ' + str(item[1]) + '	Name : ' + str(item[0]) 
		else:
			table.add_row([index + 1, item[1], item[0]])
			# print 'Rank : ' + str(index + 1) + '		CG : ' + str(item[1]) + '	Name : ' + str(item[0])
			prev_rank = index + 1
	print table
	print ''

def individual_semester_display(user_roll_num, sem_num, content = ''):
	
	# if content == '':
	# 	url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
	# 	fname = "Output.txt"
	# 	content = connect(fname, url_to_scrape)
	fname = 'divyansh.html'
	with open(fname) as f:
		content = f.readlines()
	index = 0
	sem_found = False
	table = PrettyTable(['Sub Name', 'Grade', 'Sub Type'])
	table.align = 'l'
	for line in content:
		if (line.find("<tr bgcolor=\"#FFF3FF\">") != -1 or line.find("<tr bgcolor=\"pink\">") != -1) and sem_found:
			currentLine = content[index + 2]
			matchObj = re.match( r'<td>(.*)</td>', currentLine, re.M|re.I)
			if matchObj != None and str(matchObj.group(1)).find("<b>") == -1:
				sub_name = str(matchObj.group(1))
				sub_name = sub_name.replace("&amp;", "&")
				currentLine = content[index + 5]
				matchObj = re.match(r'<td align="center">(.*?)<.*', currentLine, re.M|re.I)
				sub_grade = str(matchObj.group(1))
				if sub_grade == '':
					sub_grade = '-'
				currentLine = content[index + 6]
				matchObj = re.match(r'<td align="center">(.*)</td>', currentLine, re.M|re.I)
				sub_type = str(matchObj.group(1))
				table.add_row([sub_name, sub_grade, sub_type])

		elif line.find("<tr><td bgcolor=\"#FFF3FF\" colspan=\"2\"><h3 align=\"center\">Semester no:") != -1:
			matchObj = re.match(r'<tr><td bgcolor="#FFF3FF" colspan="2"><h3 align="center">Semester no: ([1-9]).*', line, re.M|re.I)
			if matchObj != None:
				if sem_found == True:
					return
				elif int(matchObj.group(1)) == sem_num:
					sem_found = True
					print 'Semester No.: ' + matchObj.group(1)
		# elif line.find("</table>") != -1 and line.find("</td>") == -1:
		elif line.find("<td><b>Semester Credit Taken") != -1 and sem_found:
			print table
			table.clear_rows()
			print ''
		index += 1
	print "No records were found for " + user_roll_num + " for the semester number : " + str(sem_num)

def find_name(roll_num, content = ''):
	""" Find name for the given roll number. Returns '' if record doesn't exist. """
	if content == '':
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
		fname = "Output.txt"
		content = connect(fname, url_to_scrape)
		name_flag = False
		name = ''
	for line in content:
		if line.find("Name") != -1 and not name_flag:
			idx = 24
			while(line[idx]!='<'):
				idx += 1
			name = line[24:idx]
			name_flag = True
	return name



def take_main_choice():
	""" Take user input for main menu choice and proceed accordingly 

		Return bool, whether to return to main menu or not.
	"""
	# default value, UPDATE after 1/5/2018
	user_roll_num = '14CS10008'
	# Available choices from main table
	# 5 will be used for exiting
	choices = ['1.1', '1.2', '1.3', '2.1', '2.2', '3.0', '3.1', '3.2', '3.3', '3.4', '4.1', '4.2', '5']
	print "Enter your choice."
	print "Eg. \"1.1\" (without quotes) for CGPA list. For exiting, enter 5"
	# Taking user input for choice
	choice = raw_input("")
	# Checking validity of choice entered.
	while choice not in choices:
		choice = raw_input("Please enter a valid choice :  ")
	# Choices 1.1, 1.2, 1.3 further require a sub choice of Individual / Batch list
	if choice in ['1.1', '1.2', '1.3']:
		sub_choice = raw_input(" Select - 1) Individual 		2) Batch List : ")
		while sub_choice not in ['1', '2']:
			sub_choice = raw_input("Please enter valid sub choice again (1 or 2) : ")
		# If asked for an individual
		if sub_choice == '1':
			user_roll_num = take_roll_num()
			# Individual CGPA asked
			if choice == '1.1':
				user_cg = find_cg_individual(user_roll_num)
				# Checking that records exist for this roll num
				if user_cg != -1:
					print "CGPA for " + user_roll_num + " is : " + str(user_cg)
				else:
					print "Records don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered."
			# Individual SGPA list
			elif choice == '1.2':
				sg_list = find_sg_list_individual(user_roll_num)
				num_semesters = len(sg_list)
				if num_semesters > 0:
					for i in range(len, 0, -1):
						table = PrettyTable(['Semester Number', 'SGPA'])
						table.add_row([i, sg_list[num_semesters - i]])
					print table
				else:
					print "Records don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered."
				print ''
			# Individual - Most recent SGPA
			elif choice == '1.3':
				sg = find_recent_sg_individual(user_roll_num)
				if sg != -1:
					print 'Most recent SGPA for ' + user_roll_num + ' is : ' + str(sg)
				else:
					print "Records don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered."
				print ''
		# Batch List case
		elif sub_choice == '2':
			year = take_year()
			dep = take_dep()
			msc_dep_bool = is_msc_dep(dep)
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


	if choice in ['2.1', '2.2']:
		sub_choice = raw_input("1) Individual    2) Full batch rank list")
		while sub_choice not in ['1', '2']:
			sub_choice = raw_input("Please enter valid sub choice again (1 or 2) : ")
		if sub_choice == '1':
			user_roll_num = take_roll_num()
			# Individual Dep rannk based on CG
			if choice == '2.1':
				dep_rank = find_dep_rank_individual(user_roll_num)
				if dep_rank == -1:
					print "Records don't exist for " + user_roll_num + ". Please check the validity of the roll number you have entered."
				else:
					print "Department Rank for " + user_roll_num + " is " + str(dep_rank)
			# Individual Dep rannk based on recent SGPA
			elif choice == '2.2':
				#TODO : Do this lol
				pass
		elif sub_choice == '2':
			year = take_year()
			dep = take_dep()
			msc_dep_bool = is_msc_dep(dep)
			if choice == '2.1':
				find_dep_rank_list(year, dep, msc_dep_bool)
			elif choice == '2.2':
				#TODO : Do this lol
				pass
	elif choice in ['4.1', '4.2']:
		user_roll_num = take_roll_num()
		if choice == '4.1':
			url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(user_roll_num)
			webbrowser.open(url_to_scrape,new=2)
		elif choice == '4.2':
			sem_num = raw_input("Enter the semester number : ")
			individual_semester_display(user_roll_num, int(sem_num))


def take_year():
	# Currently, software supports students with starting years as 2012, 2013, 2014, 2015
	# UPDATE : Annual
	years = ["12","13","14","15"]
	year = raw_input("Enter year of batch (Choices : 12, 13, 14, 15) :  ")
	while year not in years:
		year = raw_input("Please enter valid year :  ")
	return year

def take_dep():
	# List storing available departments in IIT Kharagpur.
	departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
	dep = raw_input("Enter Department (e.g \"CE\" for civil) :  ")
	# Converting user entered input to uppercase, in case it isn't.
	dep = dep.upper()
	while dep not in departments:
		print "Please enter a valid department!"
		dep = raw_input("Enter Valid Department again : ")
	return dep
	
def is_msc_dep(dep):
	msc_dep_list = ["GG", "EX", "MA", "CY", "HS", "PH"]
	if dep in msc_dep_list:
		return True
	return False

if __name__ == "__main__":
	print "***** Welcome to CG Accumulator *****"


	'''
	# List storing available departments in IIT Kharagpur.
	departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
	# List of Msc departments in IIT Kharagpur.
	msc_dep_list = ["GG", "EX", "MA", "CY", "HS", "PH"]
	# Currently, software supports students with starting years as 2012, 2013, 2014, 2015
	# Requires Annual UPDATE
	years = ["12","13","14","15"]
	# Variable storing CG of the user, based on the roll number provided for him/her.
	user_cg = 0.00
	# Bool var storing user's choice to return to / display main menu.
	# Initially set as True, to display menu on start of program.
	'''
	main_menu_status = True
	while main_menu_status:
		# Main Menu content
		print "I wanna play a game. Pick your poison : "
		table = PrettyTable(['Basic Lists', 'Department Rank' , '3.0 Semester Summariser', 'Individual Grade Summariser'])
		table.add_row(['1.1 CGPA','2.1 Based on CG', '3.1 Depth Subjects Grade List', '4.1 Full Performance'])
		table.add_row(['1.2 SGPA List', '2.2 Batch on recent SG','3.2 Most Scoring and Intimidating Subjects','4.2 Particular Semester'])
		table.add_row(['1.3 Recent SGPA','', '3.3 Subject with most A\'s + Ex\'s', ''])
		table.add_row(['','', '3.4 Subject with most F and Deregistrations', ''])
		table.align = 'l'
		print table
		print "Establishing Connection ........"
		# connecting to a default performance page.
		# INCLUDE
		
		content = connect("Output.txt", "https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=14CS10008")
		# Checking availability of results.
		if not check_results_availability():
			print "Sorry. Right now the results are not available due to ongoing upadations in institute database."
			key = raw_input("Press Enter to Exit.")
			exit(0)
		
	# END INCLUDE
		main_menu_status = take_main_choice()
		break

		














'''

		sg_cg_choice = raw_input("   Do you want CG list (enter '1') \nor Most recent SG list (enter '2') \nor Entire SG history (enter '3') \nor Know your D.R. (enter '4') \n or Find previous year grades in a particular subject (enter '5')? :  ")
		# Checking that entered choice is valid. If not, enter a loop.
		while sg_cg_choice not in ["1", "2", "3", "4", "5"]:
			print "Please enter a valid choice!"
			sg_cg_choice = raw_input("Enter valid choice again : ")
		print ""
		# Choices 1,2,3 require the user to input year, department and the type of degree of students.
		if sg_cg_choice in ["1", "2", "3"]:
			year = raw_input("Enter year (Available Choices : 12, 13, 14, 15) :  ")
			while year not in years:
				year = raw_input("Please enter a valid year choice :  ")
				continue
			print ""
			dep = raw_input("Enter Department :  ")
			while dep not in departments:
				print "Please enter a valid department!"
				print "P.S. Department name should be capitalised. Eg. \"CS\" and not \"cs\""
				dep = raw_input("Enter Valid Department again : ")
			print ""
			# Degree choice is required only if the entered department is not an Msc dep.
			if dep not in msc_dep_list:
				degree_choice = raw_input("Enter choice : '1' for 4 years only, '2' for 5 years only, '3' for both :  ")
				while degree_choice not in ["1", "2", "3"]:
					print "Please enter a valid choice!"
					degree_choice = raw_input("Enter valid choice again : ")
				print ""
			# In case of dep being an Msc dep, the degree choice is set to default value of "2" as it only has 5 year students.
			else:
				degree_choice = "2"
		elif sg_cg_choice == "4":
			choice = raw_input("Enter choice (1 or 2) : 1. On basis of CGPA		(2) On basis of most recent SGPA")
			while choice not in ["1", "2"]:
				choice = raw_input("Please enter a valid choice")
			user_roll_num = raw_input("Please enter your roll number. Eg - 14CS10008 :  ")
			while not check_roll_num_validity(user_roll_num, years, departments, msc_dep_list):
				user_roll_num = raw_input("Please enter valid roll number :  ")
			find_dep_rank(choice, user_roll_num, msc_dep_list)





		if sg_cg_choice == "4" or sg_cg_choice == "5":
			degree_choice = "3"
			if sg_cg_choice == "4":
				roll_num = raw_input("Enter last 5 digits of your roll number :  ")
				while len(roll_num) != 5 or find_cg(year + dep + roll_num) == -1:
					print "Please enter valid last 5 digits"
					roll_num = raw_input("Enter valid last 5 digits of your roll number again:  ")
				user_cg = find_cg(year + dep + roll_num)
			elif sg_cg_choice == "5":
				sub_name = raw_input("Enter subject name in capital letters :  ")
				#line_num = find_subject_grade_line(year, dep, sub_name, False)				

		else:

			print ""
			degree_choice = raw_input("Enter choice : '1' for 4 years only, '2' for 5 years only, '3' for both :  ")
			while degree_choice not in ["1", "2", "3"]:
				print "Please enter a valid choice!"
				degree_choice = raw_input("Enter valid choice again : ")
			print ""
		break
'''


# Option path - 1.1 -> 1 - 1 request sent, 1 line printing CG of entered roll num.
# Option path - 1.1 -> 2 - No. of requests = O(no. of students in batch) - Table and average CG printed
