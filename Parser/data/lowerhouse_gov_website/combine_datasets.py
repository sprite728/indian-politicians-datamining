import csv
import glob
import ipdb, time, re
from pymongo import MongoClient


HOST = 'localhost'
PORT = 27017


politicians = {}

FI_politicians = open("../priyank_politicians/politicians.csv", 'r')

dict_reader = csv.DictReader(FI_politicians,  delimiter=",")

for row in dict_reader:
    politicians[row['Name of elected M.P.']] = row


politicians_from_html = {}

list_of_html_files = glob.glob('raw/*.html')

for file_index, file_name in enumerate(list_of_html_files):
    # print str(file_index) + " " + file_name
    FI = open(file_name, 'r')
    content = FI.read()

    fields = [
        "Name", "Date of Birth", "Constituency from which I am elected", "Educational Qualifications",
        "Positions Held", "Profession", "Social and Cultural Activities", "Special Interests",
        "Sports and Clubs", "Birth Place", "Permanent Address", "Profession", "Countries Visited",
        "State Name", "Party Name"
    ]

    for field in fields:
        search_term = "<tr><td><strong>" + field + "</strong></td><td>(.*?)</td></tr>"
        m = re.search(search_term, content, re.I|re.DOTALL)
        
        try:
            result = m.group(1)
            result = result.strip('\n\t')
        except:
            pass
            
        print "..." + field + ": " + result


    # Date of Birth, Constituency, Education Qualification
    # Position Held, Other Information, Special Interests
    # Sports and Clubs, Birth place
    # Permanent Address, Profession, Countries Visted