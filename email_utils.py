import smtplib, ssl
from email.utils import formatdate
from email.message import EmailMessage

smtp_server = "smtp.kellerkompanie.com"
port = 587
sender = "no-reply@kellerkompanie.com"
password = input("Type your password and press enter: ")
receiver = "schwaggot@kellerkompanie.com"

msg = EmailMessage()
msg.set_content("Hello, World!")
msg['Subject'] = 'Testmessage 2'
msg['From'] = sender
msg['To'] = receiver
msg['Date'] = formatdate(localtime=True)

context = ssl.create_default_context()
server = smtplib.SMTP(smtp_server, port)
server.starttls(context=context)
server.login(sender, password)
server.send_message(msg)
server.quit()
