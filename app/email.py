import smtplib
from flask import current_app

def send_email(to, subject, message):
    try:
        server = smtplib.SMTP(current_app.config['SMTP_SERVER'], current_app.config['SMTP_PORT'])
        server.starttls()
        server.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])
        
        # The 'message' parameter to 'sendmail' should be a full email message string,
        # including headers. The 'subject' parameter is not a direct argument for sendmail.
        # We construct the email message with From, To, and Subject headers.
        from_email = current_app.config['SMTP_USERNAME']
        email_message = f"From: {from_email}\nTo: {to}\nSubject: {subject}\n\n{message}"
        
        server.sendmail(from_email, to, email_message)
        server.quit()
    except Exception as e:
        # It's a good practice to log the exception.
        # In a real application, you might use Flask's logger.
        print(f"Failed to send email: {e}")
