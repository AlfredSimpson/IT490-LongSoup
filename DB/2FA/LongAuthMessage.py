import smtplib
from email.mime.text import MIMEText
import random
import os
from dotenv import load_dotenv
from TESTDBWorker import useremail
# from DBWorker import useremail

load_dotenv()


# Test only
#useremail = "8bitjava5354@gmail.com"

# 2FA Code
number = random.randint(1000,9999)
sentNumber = number
print(sentNumber)

subject = "Email Subject"
body = "Please enter this code at login: " + str(sentNumber)
sender = os.getenv("LONG_MAIL")
recipients = useremail
password = os.getenv("LONG_MAIL_PASS")


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent to user for verification!")


send_email(subject, body, sender, recipients, password)

