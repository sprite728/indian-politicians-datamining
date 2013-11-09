indian-politicians-datamining
=============================

Data Mining India Politicians



virtualenv setup
===============
1. activate virtualenv
	- ./venv/bin/activate

2. deactivate
	- deactivate

3. If you move the venv folder to another place, you need to reset the virtualenv by:
	$virtualenv --system-site-packages /Path/To/Virtual/Environment/venv

dependencies
===========
1. pymongo
2. twython (Python wrapper for Twitter)
3. Networkx
4. matplotlib
5. R
	- igraph (also has a python extension)
6. numpy



Servers
=========
1. Amazon EC2 Domain Name: ec2-54-205-67-179.compute-1.amazonaws.com
2. Test Server: jeff@dhcp3-234, Hint: 傳chi


Installation
============
* Mac OSX
	http://www.mkyong.com/mongodb/how-to-install-mongodb-on-mac-os-x/

MongoDB setup
===============
* Allow remote access
	1. Lastest MongoDb package on debian is bind to 127.0.0.1, this address doesn’t allow the connection by remote hosts, to change it u must set bind to 0.0.0.0 for 
	$ vim /etc/mongodb.conf

	2.
	bind_ip = 0.0.0.0
	port = 27017

	3.
	restart mongodb

MongoDB Management
===================
* http://docs.mongodb.org/ecosystem/tools/administration-interfaces/

* mongobird setup
	- Reference:
		* http://mongobird.citsoft.net/?page_id=460
		* http://wolfpaulus.com/jounal/mac/tomcat7/
	- Install JDK
	- Install Tomcat 
		* start tomcat
			$ sudo /Library/Tomcat/bin/startup.sh
		* shutdown tomcat
			$ sudo /Library/Tomcat/bin/shutdown.sh
		
		* Remember to setup an initial admin user in usr/local/<tomcat dir>/conf

		
	- Default Tetrad username/pw
		- admin/admin

* MongoExplorer
	- Allows admin to quickly see the documents in MongoDB
	- Connect to the remote db, dhcp3-234

iPython Notebook Remote Access Setup
=====================================
1. See detail here: http://nbviewer.ipython.org/urls/raw.github.com/Unidata/tds-python-workshop/master/ipython-notebook-server.ipynb

2. Creating a profile for the server 
	$ ipython profile create nbserver

[ProfileCreate] Generating default config file: u'/Users/Jeff/.ipython/profile_nbserver/ipython_config.py'
[ProfileCreate] Generating default config file: u'/Users/Jeff/.ipython/profile_nbserver/ipython_notebook_config.py'
[ProfileCreate] Generating default config file: u'/Users/Jeff/.ipython/profile_nbserver/ipython_nbconvert_config.py'

3. Go here: si-roller-coaster port = 10001

Issues with Data
================
[11/8]
* Twitter account problems:
	- Rahul Gandhi - suspended
	- Manish Tewari - protected, ManishTewari
	- Basori Singh Masram - protected, BasorisinghMasr
	- Sandeep Dikshit - protected, SandeepDikshit


[Before 11/8]
1. There are two Harsh Vardhan in the html files, but one in the politicians.csv
	- Harsh Vardhan
	- Shri Harsh Vardhan
2. There are two Mahadeo Singh Khandela in the html files, but one in the politicians.csv (Which one is which?)
	- Mahadeo Singh Khandela
	- Shri Mahadeo Singh Khandela
3. In html files, there are "Ajay Makan" with bday "NA" and Ajay Maken with bday "12/1/1964", and in the politicians.csv file there is only a "Ajay Makan" with bday "NA"

4. In the html files, there is "Shri Abhijit Mukherjee" with bday 2/1/1960 and "Abhijit Mukherjee" with bday 1/2/1960. Are they two different people or that's the problem with the html files?

5. There are  "Ramashankar Rajbhar" with bday NA and "Shri Ramashankar Rajbhar" with bday 1/1/1960 in the html files. Only one "Ramashankar Rajbhar" with bday NA in the politicians.csv file 

6. There are "Sansuma Khunggur Bwiswmuthiary" and "Shri Sansuma Khunggur Bwiswmuthiary" in the html files

7. There are "Ravindra Kumar Pandey" and "Shri Ravindra Kumar Pandey" in the html files

8. "Prasun Banerjee" is not in the combined_politicians.csv

9. "Pradeep Kumar Singh" & "Shri Pradeep Kumar Jain   Aditya" in combined file
