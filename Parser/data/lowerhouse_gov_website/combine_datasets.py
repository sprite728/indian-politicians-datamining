import csv
import glob
import ipdb, time, re
from pymongo import MongoClient


HOST = 'localhost'
PORT = 27017

"""
====================================================================================
        Read politicians information from Priyank's politicians.csv file
====================================================================================
"""

politicians = {}

FI_politicians = open("../priyank_politicians/politicians.csv", 'r')

dict_reader = csv.DictReader(FI_politicians,  delimiter=",")

for row in dict_reader:
    politicians[row['Name of elected M.P.']] = row




"""
====================================================================================
        Read politicians information from HTML files
====================================================================================
"""
politicians_from_html = {}

list_of_html_files = glob.glob('raw/*.html')

fields = [
    "Name", "Date of Birth", "Constituency from which I am elected", "Educational Qualifications",
    "Positions Held", "Profession", "Social and Cultural Activities", "Special Interests",
    "Sports and Clubs", "Birth Place", "Permanent Address", "Profession", "Countries Visited",
    "State Name", "Party Name"
]


for file_index, file_name in enumerate(list_of_html_files):
    # print str(file_index) + " " + file_name
    FI = open(file_name, 'r')
    content = FI.read()

    search_term = "<tr><td><strong>Name</strong></td><td>(.*?)</td></tr>"
    m = re.search(search_term, content, re.I|re.DOTALL)
        
    try:
        result = m.group(1)
        result = result.strip('\n\t')
    except:
        result = ''
        print "Error: Cannot find the name of this politician."

    politician_name = result
    politicians_from_html[politician_name] = {}


    # Preprocess Positions Held, the format is different from other fields
    search_term = "<tr><td><strong>Name</strong></td><td>(.*?)</td></tr>"

    for field in fields:
        search_term = "<tr><td><strong>" + field + "</strong></td><td>(.*?)</td></tr>"
        m = re.search(search_term, content, re.I|re.DOTALL)
        
        try:
            result = m.group(1)
            result = result.strip('\n\t')
        except:
            result = ''

        print "..." + field + ": " + result

        politicians_from_html[politician_name][field] = result 

"""
====================================================================================
        Combine politicians and politicians_from_html
====================================================================================

    Process:
    0. Read in name mapping file into a `name_mapping` dictionary
    1. Put all the data in `politicians` dictionary
        into `db.politicians` collection in mongoDB.
        - Add a prefix p_* to all the key
    2. Iterate through the items in politicians_from_html, 
    3. look up the item.name in name mapping
        
        if(find a name in name mapping)
            use the alternative_name to lookup document in mongoDB, 
            - Add a prefix h_* to all the key
        
        if(cannot find)
            create a new politician document in `db.politicians`
    4. Generate a csv file based on the `db.politicians` collection (Use MongoDB explorer)
"""

fname = "name_mappings_jaccarddistance_edited_PC.csv"

# Notice the file flag: "U". 
# This should fix any CSV parsing issues when your
# Excel sheet is irregularly formatted and populated. 
FI_name_mapping = open(fname, 'rU')
name_mapping_reader= csv.DictReader(FI_name_mapping, delimiter=",")

name_mappings = {}
# key = name from html
# value = name from politicians.csv

for row in name_mapping_reader:
    #print row["Name1"] + ' | ' + row["Name2"]
    
    name_from_politician = row.get("Name1", None)
    name_from_html = row.get("Name2", None)
    
    if name_from_politician and name_from_html:
        name_mappings[name_from_html] = name_from_politician
        
# Put a prefix p_ to the politicians dictionary
politicians_with_prefix = {}
for politician in politicians:
    politicians_with_prefix[politician] = {}
    for field in politicians[politician]:
        politicians_with_prefix[politician]["p_" + str(field).replace('.', "")] = politicians[politician][field]

# Put a prefix h_ to the politicians_from_html dictionary
politicians_from_html_with_prefix = {}
for politician in politicians_from_html:
    politicians_from_html_with_prefix[politician] = {}
    for field in politicians_from_html[politician]:
        politicians_from_html_with_prefix[politician]["h_" + str(field).replace('.', "")] = politicians_from_html[politician][field]

# def addPrefixToDict(prefix, old_dict):
#     new_dict = {}
#     for item in old_dict:
#         new_dict[item] = {}
#         if new_dict[item].__class__ == {}.__class__: # the value of dict is still a dict
#             new_dict[item] = addPrefixToDict(prefix, old_dict[item])
#         else:
#             new_dict[str(pre_fix) + item] = old_dict[item]
#     return new_dict

client = MongoClient(HOST, PORT)
db = client.india

for politician in politicians_with_prefix:
    db.politicians.insert(politicians_with_prefix[politician])


for politician_from_html in politicians_from_html_with_prefix:
    name_in_html = politicians_from_html_with_prefix[politician_from_html]["h_Name"]

    name_in_csv = name_mappings.get(name_in_html, None)
    
    if name_in_csv:
        cursor = db.politicians.find( { "p_Name of elected MP": name_in_csv } )

        if cursor.count() == 1:
            for p_in_db in cursor:
                new_p_in_db = dict(p_in_db.items() + politicians_from_html_with_prefix[politician_from_html].items())
                db.politicians.save(new_p_in_db)
        else:
            print "Error: Find multiple matches in database"
    else:
        db.politicians.insert(politicians_from_html_with_prefix[politician_from_html])

"""
    Output to csv

"""


fname = "combined_politicians.csv"
with open(fname, 'wb') as outf:
    outcsv = csv.writer(outf, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

    cursor = db.politicians.find()
    for politician in cursor:
        row = []
        for key, value in politician.items():
            row.append(value)

"""
Need to clean up the bday format later, as well as income, ...
"""
