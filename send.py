#!/usr/local/bin/python2.6

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import subprocess
import sys, traceback
import pymysql

print "Content-type: text/html"
print """
<html>
<head><title>Send.A.Message Status</title></head>
<body>
"""

########################################
# Initialize vars
########################################
form = cgi.FieldStorage()
subject = form.getvalue("messagesubject", "(no subject)").strip().split(":")[1];
message = form.getvalue("message", "(no message text)");
targets = form.getvalue("messagetarget", "(no targets)").split(":");
dbhost = 'dbhost'
dbpasswd = 'dbpass'
dbuser = 'dbuser'
dbname = 'DBNAME'
dbtable = 'SENDAMESSAGE'

########################################
# Loop through targets, send email, 
# print status and log to DB
########################################
for target in targets[1].strip().split(","):
	if target == 'List1':
		bcclist_file = "./List1.txt"
	elif target == 'List2':
		bcclist_file = "./List2.txt"
	elif target == 'List3':
		bcclist_file = "./List3.txt"
	else:
		print "INVALID TARGET RECIPIENT LIST:" + target
		exit(1)
	with open(bcclist_file, 'r') as content_file:
    		bcclist = content_file.read()

	try:
		subprocess.check_call("echo \"%s\" | mail -s \"%s\" -bcc %s you@domain.com -- -f from-email@domain.com" % (message, subject, bcclist.strip()), shell=True)
		retcode="SUCCESS"
	except subprocess.CalledProcessError:
		print "ERROR SENDING MAIL"
		print '-'*60
        	traceback.print_exc(file=sys.stdout)
        	print '-'*60
		print "<br />"
		retcode="FAILURE"
	print """
		%s : %s <br />
	""" % (retcode, cgi.escape(target))

	db = pymysql.connect( host=dbhost, passwd=dbpasswd, user=dbuser, db=dbname);
	cursor = db.cursor()
        sql = "INSERT INTO %s VALUES(null, null, \"%s\", \"%s\", \"%s\")" % (dbtable, bcclist, message, retcode)
	cursor.execute(sql)
	cursor.close()
        db.close()


########################################
# Close HTML page
########################################
print """
</body>
</html>
"""
