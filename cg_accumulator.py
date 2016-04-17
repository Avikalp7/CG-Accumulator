import requests 
from bs4 import BeautifulSoup
import time


def is_number(s):
    """
    Check and parse entered value as a number
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def cg_accumulate(year, dep, degree_choice, sg_cg_choice, user_cg):
	
	# List of departments with Integrated M.Sc. (5 year courses)
	msc_dep_list = ["GG", "EX", "MA", "CY", "HS", "PH"]
	msc_dep = False
	dep_rank = 1
	
	print ""
	fname = "Output.txt"
	roll_count = 10000
	if degree_choice == "2":
		roll_count = 30000
	if dep in msc_dep_list:
		roll_count = 20000
		msc_dep = True
		
	student_count = 0
	flag = False
	cg_total = 0.00
	sg_total = 0.00
	bad_count = 0
	sg_list = []

	while True:
		roll_count += 1
		student_count += 1
		rollno = str(year) + str(dep) + str(roll_count)
		url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + rollno
		name_flag = False
		flag = False
		
		try:
			r = requests.get(url_to_scrape) 
		except Exception:
			print "ConnectionError on :" + str(roll_count)
			print "Retrying...."
			student_count -= 1
			roll_count -= 1
			continue
		soup = BeautifulSoup(r.text, "html.parser") 

		with open(fname, "w") as text_file:
			text_file.write("{}".format(soup))

		with open(fname) as f:
			content = f.readlines()

		for line in content:
			if len(content) < 40:
				flag = True
				bad_count += 1
				student_count -= 1
				break
			
			bad_count = 0

			if line.find("Name") != -1 and not name_flag:
				idx = 24
				while(line[idx]!='<'):
					idx += 1
				name = line[24:idx]
				name_flag = True

			if sg_cg_choice == "1" or sg_cg_choice == "4":
				if line.find("CGPA") != -1:
					if line[4] != "<" and is_number(line[31:35]):
						if sg_cg_choice == "4":
							if user_cg < float(line[31:35]):
								dep_rank += 1
						else:
							print "Roll Num : " + str(rollno) + "	CG : " + str(line[31:35]) + "	Name : " + str(name)
							cg_total += float(line[31:35])
						break
			elif sg_cg_choice == "2":
				if line.find("SGPA") != -1 and is_number(line[25:29]):
					print "Roll Num : " + str(rollno) + "	SGPA in most recent semester : " + str(line[25:29]) + "	Name : " + str(name)
					sg_total += float(line[25:29])
					break
			elif sg_cg_choice == "3":
				if line.find("SGPA") != -1 and is_number(line[25:29]):
					sg_list.append(str(line[25:29]))
		
		if sg_cg_choice == "3" and not flag:
			print "Roll Num : " + str(rollno) + "	SGPA list : " + str(sg_list) + "	Name : " + str(name)
			del sg_list[:]

 					
		if flag and bad_count >= 5 and (degree_choice != "3" or roll_count > 30000 or msc_dep):
			break
		
		# Will not be executed for MSc Integrated Courses
		if flag and bad_count >= 5 and not msc_dep:
			roll_count = 30000 
			print "Making transition to dual degree students..."
			continue

	student_count -= 1
	print ""
	print "__________________________________"
	print "Number of Students : " + str(student_count)
	if sg_cg_choice == "1":
		print "Total CG : " + str(cg_total)
		print "Average CG : " + str(cg_total / student_count)
	elif sg_cg_choice == "2":
		print "Total SG : " + str(sg_total)
		print "Average SG : " + str(sg_total / student_count)
	elif sg_cg_choice == "4":
		print "Your Department Rank is : " + str(dep_rank)
		if dep_rank < student_count/2:
			print "Good going. You are in the top half of your department"
		else:
			print "A bit more hard work can see you in the top half of your department"
	print "__________________________________"


def find_cg(roll_num):
	url_to_scrape = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno=' + str(roll_num)
	fname = "Output.txt"
	try:
		r = requests.get(url_to_scrape) 

		soup = BeautifulSoup(r.text, "html.parser") 

		with open(fname, "w") as text_file:
			text_file.write("{}".format(soup))

		with open(fname) as f:
			content = f.readlines()

		if len(content) < 40:
			print "Invalid Roll Number!"
			return -1
		else:
			for line in content:
				if line.find("CGPA") != -1:
					if line[4] != "<" and is_number(line[31:35]):
						return float(line[31:35])
	except Exception:
		print "ConnectionError on you roll number. Please check your connection and try again!"
		key = raw_input("The program will now exit. Press enter")
		exit(0)



print "*** Welcome to CG Accumulator ***"

departments = ["AE", "AG", "AR", "BT", "CE", "CH", "CS", "CY", "EC", "EE", "EX", "GG", "HS", "IE", "IM", "MA", "ME", "MF", "MI", "MT", "NA", "PH", "QD"]
years = ["12","13","14","15"]
user_cg = 0.00

while True:
	print ""
	year = raw_input("Enter year (Available Choices : 12, 13, 14, 15) :  ")
	if year not in years:
		print "Please enter a valid year choice"
		continue
	print ""
	dep = raw_input("Enter Department :  ")
	while dep not in departments:
		print "Please enter a valid department!"
		print "P.S. Department name should be capitalised. Eg. \"CS\" and not \"cs\""
		dep = raw_input("Enter Valid Department again : ")
	print ""
	sg_cg_choice = raw_input("Do you want CG list (enter '1') \n or Most recent SG list (enter '2') \n or Entire SG history (enter '3') \n or Know your D.R. (enter '4')? :  ")
	while sg_cg_choice not in ["1", "2", "3", "4"]:
		print "Please enter a valid choice!"
		sg_cg_choice = raw_input("Enter valid choice again : ")

	if sg_cg_choice == "4":
		roll_num = raw_input("Enter last 5 digits of your roll number :  ")
		while len(roll_num) != 5 or (user_cg = find_cg(year + dep + roll_num)) != -1:
			print "Please enter valid last 5 digits"
			roll_num = raw_input("Enter valid last 5 digits of your roll number again:  ")
		#user_cg = find_cg(year + dep + roll_num)
		degree_choice = "3"
	else:
		degree_choice = raw_input("Enter choice : '1' for 4 years only, '2' for 5 years only, '3' for both :  ")
		while degree_choice not in ["1", "2", "3"]:
			print "Please enter a valid choice!"
			degree_choice = raw_input("Enter valid choice again : ")
		print ""
	break


print ""
print "Please wait while results are being accumulated, this may take a few minutes...."
print "Meanwhile, minimize this screen and think about what you are doing with your life."
print ""
var = cg_accumulate(year, dep, degree_choice,sg_cg_choice, user_cg)
print ""
key = raw_input("Press Enter to exit")




