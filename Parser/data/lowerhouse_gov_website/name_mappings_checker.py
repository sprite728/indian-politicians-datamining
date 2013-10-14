"""
	lowerhouse_gov_website parser
	author: Chuan-Che Jeff Huang
	email: chuanche@umich.edu

	Description
	1. Read Html files in raw/
	2. Compare the names in the html files with Politicians.xlsx
	3. Generate an intermediate name mapping files
	4. We, researchers, confirm in the name mappings are correct
	5. Delegate the later data combining task to another parser

	Note
	- Criteria
		User should be able to easily re-run this program when a field in 
		the Politicians.xlsx or HTML files are updated. 


"""

import glob
import re, csv, io
import time
import ipdb

from HTMLParser import HTMLParser

from pymongo import MongoClient

from fuzzycomp import fuzzycomp

# HOST = "dhcp3-234.si.umich.edu"
HOST= 'localhost'
PORT = 27017

"""
Name mapping data structure

name_in_politicians, name_in_html, 

Process
    1. Put all the names and birthday from name_in_politicians into a dictionary
        "Politicians"
        - key: politician name
        - value: 
            -key: source
                - value: "politicians" or "html" 
            -key: name_in_politicians
            -key: name_in_html
            -key: bday_in_politicians
            -key: bday_in_html
            -key: problem

       
    2. Get a politician name and birthday from html file
    3. See if this politician matches any of the name in the 
        "Politicians", 
        if yes:
            - check to see if bday is matched 
            if yes:
                - set bday_in_html, name_in_html
            if not:
                - set bday_in_html, name_in_html
                - set problem = True
        if not:
            - create a new item in dictionary
                - key: name_in_html
                - value
                    -key: source = "html"

            - set bday_in_html
            - set 'problem' to True


    4. Output to a csv file

"""

def processPoliticiansData():
    politicians = {}

    FI_politicians = open("../priyank_politicians/politicians.csv", 'r')

    dict_reader = csv.DictReader(FI_politicians,  delimiter=",")
    for row in dict_reader:
        
        name_in_politician = row['Name of elected M.P.']

        if row['Birthdate'] == "#N/A":
            bday_in_politician = "NA"
        else:
            bday_in_politician = convertBdayToStandard(row['Birthdate']) #format: 25/12/1951

        politicians[name_in_politician] = {
            'name': name_in_politician,
            'bday': bday_in_politician
        }

    return politicians


def processPoliticiansFromHtmlData():
    politicians_from_html = {}

    list_of_html_files = glob.glob('raw/*.html')
    for file_index, file_name in enumerate(list_of_html_files):
        print str(file_index) + " " + file_name
        FI = open(file_name, 'r')
        content = FI.read()

        m = re.search("<tr><td><strong>Name</strong></td><td>(.*?)</td></tr>", content, re.I|re.DOTALL)
        name_in_html = m.group(1)
        print name_in_html

        m = re.search("<tr><td><strong>Date of Birth</strong></td><td>(.*?)</td></tr>", content, re.I|re.DOTALL)
        bday_in_html = m.group(1) #format: "16 Mar 1950"
        bday_in_html = bday_in_html.strip('\n\t')

        if bday_in_html == "-NA-":
            bday_in_html = "NA"
        else:
            print bday_in_html
            try:
                bday_in_html = convertHtmlBdayToStandard(bday_in_html)
            except:
                ipdb.set_trace()

        politicians_from_html[name_in_html] = {
            'name': name_in_html,
            'bday': bday_in_html
        }

    return politicians_from_html

politicians = processPoliticiansData()
politicians_from_html = processPoliticiansFromHtmlData()

client = MongoClient(HOST, PORT)
db = client.india


for politician in politicians:
    db.raw_politicians.insert(politicians[politician])

for politician in politicians_from_html:
    db.raw_politicians_from_html.insert(politicians_from_html[politician])

def convertHtmlBdayToStandard(bday_str):
    btime = time.strptime(bday_str, "%d %b %Y")
    return "%s/%s/%s" % (btime.tm_mday, btime.tm_mon, btime.tm_year)

def convertBdayToStandard(bday_str):
    #format: 25/12/1951
    btime = time.strptime(bday_str, "%d/%m/%Y")
    return "%s/%s/%s" % (btime.tm_mday, btime.tm_mon, btime.tm_year)

"""
    Combine the two collections, raw_politicians and raw_politicians_from_html
    into one politicians collections

    politician
        - name
        - alias: []
        - bday
        - ...

    Process
    1. Start from `raw_politicians_from_html`, read a single politician
    2. Compare the bday of this politician with the `raw_politicians`
        output the found names on the display
        if 1:
            #Ask researcher: correct or not?
            create a document in `politicians`
            - name: raw_politician.name
            - alias: [raw_politicians_from_html.name]
            - bday: raw_politician.bday
            - fields-1: from raw_politician
            - fields-2: from raw_politicians_from_html
        if 0:
            create a document in `politicians`
            - name: raw_politicians_from_html.name
            - bday: raw_politicians_from_html.bday
            - fields-1: from raw_politicians_from_html
        if N:
            #Ask researcher: which one it is (by number)?
            create a document in `politicians`
            - name: raw_politician.name
            - alias: [raw_politicians_from_html.name]
            - bday: raw_politician.bday
            - fields-1: from raw_politician
            - fields-2: from raw_politicians_from_html            

"""

"""
    Construct Name Mappings First
"""
clean_politicians = {}

cursor_html = db.raw_politicians_from_html.find()
for politician_from_html in cursor_html:
    print politician_from_html
    # ipdb.set_trace()
    # cursor = db.raw_politicians.find({ "bday": politician_from_html.get('bday')})

    bday_options = []
    bday_options.append( politician_from_html.get('bday') )

    bday_str = politician_from_html.get('bday')
    
    if bday_str != "NA":
        bday_time = time.strptime(bday_str, "%d/%m/%Y")
    
        reverse_str = "%s/%s/%s" % (bday_time.tm_mon, bday_time.tm_mday, bday_time.tm_year)
        bday_options.append(reverse_str)

    
    cursor = db.raw_politicians.find(
            {"bday": {"$in": bday_options}}
        )

    if cursor.count() == 0:
        # didn't find matches
        clean_politicians[politician_from_html.get('name')] = {
            "name_in_html": politician_from_html.get('name'),
            "bday_in_html": politician_from_html.get('bday'),
            "problem": True,
        }

    elif cursor.count() == 1:
        for item in cursor:
            clean_politicians[politician_from_html.get('name')] = {
                "name_in_politicians": item.get('name'),
                "name_in_html": politician_from_html.get('name'),
                "bday_in_politicians": item.get('bday'),
                "bday_in_html": politician_from_html.get('bday'),
                "problem": False
            }
    else:
        # Multiple ones
        names_in_politicians = []
        for item in cursor:
            names_in_politicians.append(
                    item.get("name")
                )
        
        clean_politicians[politician_from_html.get('name')] = {
                "name_in_html": politician_from_html.get('name'),
                "bday_in_html": politician_from_html.get('bday'),
                "names_in_politicians": names_in_politicians,
                "problem": True
            }
    # if cursor.count() == 0:
    #     # try use last name
    #     name_array = politician_from_html.get('name').split()
    #     name_query_term = name_array[len(name_array) -1 ]

    # stupid Priyank makes a mistake in his data!
    # So I need to check if he reverse the Month and Day in the birthday data

    print cursor.count()


# writer = csv.writer(open("name_mappings.csv", 'wb'))

# for key, value in clean_politicians.items():
#     writer.writerow([key, value])

for key, value in clean_politicians.items():
    if clean_politicians[key].get("problem"):
        
        str1 = key # a name from the html file

        # ipdb.set_trace()
        min_distance = float("inf")
        min_distance_name = ''
        for name in politicians.keys():
            current_distance = fuzzycomp.jaccard_distance(str(str1), str(name))
            if (current_distance < min_distance):
                min_distance = current_distance
                min_distance_name = name

        print key + ' | ' + min_distance_name + ' | ' + str(min_distance)
        clean_politicians[key]['name_in_politicians'] = min_distance_name
        # ipdb.set_trace()

fname = "name_mappings.csv"
with open(fname, 'wb') as outf:
    output = io.StringIO()

    outcsv = csv.writer(outf, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

    outcsv.writerow(["Name from Politicians.csv", "Names from Html files"])

    for key, value in clean_politicians.items():
        row = [
            clean_politicians[key].get("name_in_politicians", ''),
            # clean_politicians[key].get("bday_in_politicians", ''),
            clean_politicians[key].get("name_in_html", ''),
            # clean_politicians[key].get('bday_in_html', ''),
            # clean_politicians[key].get("names_in_politicians", ''),
            clean_politicians[key].get("problem", '')
        ]
        
        for name in clean_politicians[key].get('names_in_politicians', []):
            row.append(name)
        
        outcsv.writerow(row)
    # clean_politicians



