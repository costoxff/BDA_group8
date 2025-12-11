from utils.env import SENDER_EMAIL, SENDER_PASSWORD

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email_with_attachment(to_email, subject, body, file_path=None):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = SENDER_EMAIL
    sender_password = SENDER_PASSWORD
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    if file_path != None:
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.split("/")[-1]}'
            )
            msg.attach(part)
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        print("acount or password error")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        return False 
    except Exception as e:
        print(f"sending failed: {e}")
        return False