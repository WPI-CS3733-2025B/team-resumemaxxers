import smtplib
from flask import current_app
from threading import Thread

def _send_async_email(app, to, subject, message):
    with app.app_context():
        try:
            server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
            server.starttls()
            server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
            
            from_email = app.config['SMTP_USERNAME']
            email_message = f"From: {from_email}\nTo: {to}\nSubject: {subject}\n\n{message}"
            
            server.sendmail(from_email, to, email_message)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_email(to, subject, message):
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_email, args=[app, to, subject, message])
    thr.start()
    return thr