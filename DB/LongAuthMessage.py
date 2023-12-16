import smtplib
from email.mime.text import MIMEText
import random
import os
from dotenv import load_dotenv

# from DBWorker import useremail

load_dotenv()


subject = "CGS Authentication Code: "
sender = os.getenv("LONG_MAIL")
password = os.getenv("LONG_MAIL_PASS")


def send_email(useremail, subject=subject, sender=sender, password=password):
    number = random.randint(1000, 9999)
    sentNumber = number
    body = "Please enter this code at login: " + str(sentNumber)
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = useremail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, useremail, msg.as_string())
    print("Message sent to user for verification!")
    return sentNumber


# send_email(subject, body, sender, recipients, password)
