# utils/email.py
import smtplib
from email.mime.text import MIMEText

def send_verification_email(to_email, token):
    msg = MIMEText(f"Click here to verify your email: http://localhost:8000/verify-email?token={token}")
    msg['Subject'] = "Verify Your Email"
    msg['From'] = "wedding booking system"
    msg['To'] = to_email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("phonesell7896@gmail.com", "wpeolucbkvtfmljy")
    server.send_message(msg)
    server.quit()
