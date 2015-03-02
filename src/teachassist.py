import mechanize
import re
import urllib2
import cookielib
from bs4 import BeautifulSoup
import re

assignments_list = []
weightings_list = []

def init(html):

	soup = BeautifulSoup(html) # a = html of course web page, i.e. specific web page for chemistry marks

	for x in xrange(4,len(soup.find_all("tr"))-17, 2):
		assignments_list.append(soup.find_all("tr")[x])

	for x in xrange(len(soup.find_all("tr"))-9, len(soup.find_all("tr"))-1):
		weightings_list.append(soup.find_all("tr")[x])

	regex = '<div style="font-family:\'Alfa Slab One\', Arial, serif;font-weight:400;font-size:64pt;color:#eeeeee;">(.+?)</div>'
	patt = re.compile(regex)
	text = re.findall(patt, html)


	for x in soup.find_all("h2"):
		# if x.text == "SBI4U1-03": # uncomment this to only choose specific courses for testing dropped marks
		print "Course: {}".format(x.text)
		main(text[0].replace(" ",""))


def get_lowest_mark(alist, drop_list):

	all_assignments_list = []

	for x in alist:

		# iterates over each unparsed assignment and appends all properties of assignment to all_assignments_list

		try:
			assignment = {"title": x.find("td").text}
		except:
			pass

		a = x.find_all("td")

		# stores (mark, weighting) as a tuple in dict under the category
		try:
			assignment["K"] = (a[1].text.split("\n")[1].replace("\t",""), a[1].text.split("\n")[2].split("=")[-1]) 
		except:
			pass

		try:
			assignment["T"] = (a[2].text.split("\n")[1].replace("\t",""), a[2].text.split("\n")[2].split("=")[-1]) 
		except:
			pass

		try:
			assignment["C"] = (a[3].text.split("\n")[1].replace("\t",""), a[3].text.split("\n")[2].split("=")[-1]) 
		except:
			pass

		try:
			assignment["A"] = (a[4].text.split("\n")[1].replace("\t",""), a[4].text.split("\n")[2].split("=")[-1])
		except:
			pass	

		# try:
		# 	assignment["O"] = (a[5].text.split("\n")[1].replace("\t",""), a[5].text.split("\n")[2].split("=")[-1])
		# except:
		# 	pass	

		drop = False

		for x in drop_list:
			if x.lower() in assignment['title'].lower():
				print "dropping {}".format(assignment['title'])
				drop = True
				break

		if not drop:
			all_assignments_list.append(assignment)

	return all_assignments_list


def get_weightings_BASE(wlist):
	x = wlist[0]

	weight_dict = {}

	for a in x.find_all("tr"):
		weight_dict[a.contents[1].text] = a.contents[5].text

	return weight_dict

def get_total_marks(alist):

	mark_sum = {"K": 0, "T": 0, "C": 0, "A": 0}
	
	#TOTAL OCCURANCE
	totalK = 0
	totalT = 0
	totalC = 0
	totalA = 0

	# WEIGHTINGS
	WK = 0
	WT = 0 
	WC = 0
	WA = 0

	lol = ['K', 'T', 'C', 'A']

	# THIS FOR LOOP IS TO GATHER ALL WEIGHTS
	for x in alist:

		for y in lol:
			try:
				if x[y][1] == 'no weight':
					continue
			except:
				pass


		try:
			if "%" in x['K'][0]:
				WK += float(x['K'][1])
		except:
			pass
			

		try:
			if "%" in x['T'][0]:
				WT += float(x['T'][1])
		except:
			pass


		try:
			if "%" in x['C'][0]:
				WC += float(x['C'][1])
		except:
			pass


		try:
			if "%" in x['A'][0]:
				WA += float(x['A'][1])
		except:
			pass

	# print WK, WT, WC, WA


	# ADD UP ALL MARKS
	# xW = weighted mark of assignment
	# xWM = total weight of section (i.e. knowledge)
	for x in alist:

		for y in lol:
			try:
				if x[y][1] == 'no weight':
					continue
			except:
				pass

		try:
			if "%" in x['K'][0]:
				x['KWM'] = (float(x['K'][1]) / WK) * 100  # max possible relative to weight
				x['KW'] = float(x['K'][0].replace(" ","").strip("%")) * (float(x['K'][1]) / WK) # add weighted mark to dict
				mark_sum['K'] += float(x['K'][0].replace(" ","").strip("%")) * (float(x['K'][1]) / WK) # percent * (assignment_weight / total_weight)
				totalK += 1
		except:
			pass
			

		try:
			if "%" in x['T'][0]:
				x['TWM'] = (float(x['T'][1]) / WK) * 100  # max possible relative to weight
				x['TW'] = float(x['T'][0].replace(" ","").strip("%")) * (float(x['T'][1]) / WK) # add weighted mark to dict
				mark_sum['T'] += float(x['T'][0].replace(" ","").strip("%")) * (float(x['T'][1]) / WT)
				totalT += 1	
		except:
			pass

		try:
			if "%" in x['C'][0]:
				x['CWM'] = (float(x['C'][1]) / WK) * 100  # max possible relative to weight
				x['CW'] = float(x['C'][0].replace(" ","").strip("%")) * (float(x['C'][1]) / WK) # add weighted mark to dict
				mark_sum['C'] += float(x['C'][0].replace(" ","").strip("%")) * (float(x['C'][1]) / WC)
				totalC += 1	
		except:
			pass


		try:
			if "%" in x['A'][0]:
				x['AWM'] = (float(x['A'][1]) / WK) * 100  # max possible relative to weight
				x['AW'] = float(x['A'][0].replace(" ","").strip("%")) * (float(x['A'][1]) / WK) # add weighted mark to dict
				mark_sum['A'] += float(x['A'][0].replace(" ","").strip("%")) * (float(x['A'][1]) / WA) 
				totalA += 1	
		except:
			pass


	# print "K: {} T: {} C: {} A: {}".format(totalK, totalT, totalC, totalA)

	return (mark_sum, alist) # (total_marks for each category, list with specific assignments weighted)

def calculate_average(c_weight, a_marks):

	c_sum = 0.0
	final_sum = 0.0

	for x in c_weight.values():
		if "%" in x:
			c_sum += float(x.replace("%","").replace(" ",""))

	c_sum = 100 - c_sum # done so that categories that have no mark aren't part of your total

	# makes sure that sections that dont have marks aren't counted in the total percentage, assumes that user handed in all assignments
	if not a_marks[0]['T'] == 0:
		c_weight['Thinking'] = float(c_weight['Thinking'].replace("%","")) / (.01 * c_sum)
		a_marks[0]['T'] = a_marks[0]['T'] * (0.01 * c_weight['Thinking'])

	if not a_marks[0]['K'] == 0:
		c_weight['Knowledge/Understanding'] = float(c_weight['Knowledge/Understanding'].replace("%","")) / (.01 * c_sum)
		a_marks[0]['K'] = a_marks[0]['K'] * (0.01 * c_weight['Knowledge/Understanding'])
	
	if not a_marks[0]['C'] == 0:
		c_weight['Communication'] = float(c_weight['Communication'].replace("%","")) / (.01 * c_sum)
		a_marks[0]['C'] = a_marks[0]['C'] * (0.01 * c_weight['Communication'])

	if not a_marks[0]['A'] == 0:
		c_weight['Application'] = float(c_weight['Application'].replace("%","")) / (.01 * c_sum)
		a_marks[0]['A'] = a_marks[0]['A'] * (0.01 * c_weight['Application'])


	for x in a_marks[0].values():
		final_sum += x

	return final_sum

def old_mark():
	a_list = get_lowest_mark(assignments_list, [])
	w_dict = get_weightings_BASE(weightings_list) 
	pp = get_total_marks(a_list)
	course_mark = calculate_average(w_dict, pp)

	return course_mark

def main(curr_mark):

	print "Mark is currently : {0:.2f}%".format(round(old_mark(), 2))
	# print "Mark is currently : {}".format(curr_mark)

	drop_list = []

	drops = 0

	drop = ""

	while not drop == "0" and drops < 7:
		drop = raw_input("Enter the assignment you want to drop (0 to stop): ")	

		drop_list.append(drop)

		drops += 1

	can_remove = {'quiz': (1, 1), 'prelab': (1, 1), 'making_conns': (1, 1), 'test': (3, 1), 'quest': (2, 1)} # name: (weight, can_drop (1 = yes, 0 = no))

	a_list = get_lowest_mark(assignments_list, drop_list)

	w_dict = get_weightings_BASE(weightings_list) # return dict with 

	pp = get_total_marks(a_list) # returns dict with each category + its mark after weighting

	course_mark = calculate_average(w_dict, pp) # returns corrent course mark + converts get_weighting_BASE dict to weighted dict

	print a_list

	print "After dropping stuff, mark will be : {0:.2f}%".format(round(course_mark, 2))




ta_url = "https://ta.yrdsb.ca/yrdsb/index.php"

br = mechanize.Browser()
cj = cookielib.LWPCookieJar()
br.set_handle_robots(False)
br.set_handle_refresh(False)
br.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0')]

response = br.open(ta_url)

# br.set_read_only(False)
br.select_form("loginForm")
br.set_all_readonly(False)


# for form in br.forms():
	# pass


#######################################################################################

USERNAME = ""
PASSWORD = ""

#######################################################################################


br['username'] = USERNAME
br['password'] = PASSWORD

response = br.submit().read()

soup = BeautifulSoup(response)

# for result in soup.find_all('a'):
# 	print str(result)

courses_links = []

links = list(br.links())
	
for x in links:
	if "%" in x.text:
		html = br.open(x.url).read()
		init(html)