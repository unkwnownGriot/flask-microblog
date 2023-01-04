from flask_mail import Message
from flask import render_template,current_app
from app import mail
from threading import Thread
from flask_babel import _

def send_async_mail(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject,sender,recipients,text_body,html_body):
    msg = Message(subject=subject,sender=sender,recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(message=msg)
    Thread(target=send_async_mail,args=(current_app._get_current_object(),msg)).start()


