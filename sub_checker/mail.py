# Import smtplib for the actual sending function
import smtplib
import json,sys
from pprint import pprint
from time import strptime  # parse time
from time import strftime  # format time

# Import the email modules we'll need
from email.mime.text import MIMEText

new_body = ""
with open("body.json") as data_file:
    data = json.load(data_file)
    #pprint(data)
    for item in data["list"]:
        start = item["Items"][0]["Start"]
	start_ts = strptime(start, "%Y-%m-%dT%H:%M:%S")
	end = item["Items"][0]["End"]
	end_ts = strptime(end, "%Y-%m-%dT%H:%M:%S")
	duration = item["Items"][0]["Duration"]
	duration_ts = strptime(duration, "%H:%M:%S")
	teacher = item["WorkerFirstName"] + " " + item["WorkerLastName"]
	title = item["WorkerTitle"]
	school = item["Items"][0]["Institution"]['Name']
	new_body += "%s %s-%s (%s)\n%s with %s @ %s\n\n" % (strftime("%Y %B %d", start_ts),  \
				strftime("%I:%M%p", start_ts), strftime("%I:%M%p", end_ts), strftime("%I:%M", duration_ts), title, teacher, school)

#print new_body
userid=sys.argv[2]
pid=sys.argv[3]
new_body += "\n\nhttps://sub.aesoponline.com/Login/RedirectLogin?userId=%s&pin=%s&remember=false&pswd=&loginBaseUrl=www.aesoponline.com\n" % (userid, pin)

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
# Create a text/plain message
msg = MIMEText(new_body)

from = sys.argv[4]
to = sys.argv[5]
msg['Subject'] = sys.argv[1] + " Available Position(s)"
msg['From'] = from
msg['To'] = to

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP('localhost')
s.sendmail(from, [to], msg.as_string())
s.quit()

print("mail sent")
