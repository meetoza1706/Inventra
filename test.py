import smtplib
from email.mime.text import MIMEText

# Email content
sender = 'inventra8@gmail.com'
recipient = 'ozamee17@gmail.com'
subject = 'Test Email'
body = 'This is a test email sent via Gmail SMTP.'

# Create the email message
msg = MIMEText(body)
msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = subject

try:
    # Connect to Gmail's SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Secure the connection
        server.login(sender, 'nrse ieig itce hltm')
        server.sendmail(sender, recipient, msg.as_string())
    print('Email sent successfully!')
except Exception as e:
    print(f'Error: {e}')
