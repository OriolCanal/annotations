import smtplib
import ssl
from email.message import EmailMessage
import os



def send_email(reciever, subject, body):
    bioinf_pwd = os.environ.get("pwd_bioinf")
    email_sender = "bioinformaticaudmmp@gmail.com"
    email_password = bioinf_pwd
    
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = reciever
    em["Subject"] = subject
    em.set_content(body)
    
    # Adding a layer of security, SSL is a technology for keeping an internet connection secure
    context = ssl.create_default_context()
    smtp = smtplib.SMTP_SSL("smtp.gmail.com",context=context)
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, reciever, em.as_string())
    smtp.quit()







