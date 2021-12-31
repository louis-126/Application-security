import smtplib
from email.message import EmailMessage

def sendmail(to,dprt,doc,date,time,venue):
    server = smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=30)
    server.login("nanyangpolyclinic@gmail.com","appdev123")
    msg = EmailMessage()
    msg['Subject'] = 'Appointment Notification'
    msg['From'] = 'nanyangpolyclincic@gmail.com'
    msg['To'] = to
    msg.set_content(f'Your appointment has been booked with the following details:\n'
                    f'Department: {dprt}\n'
                    f'Doctor: {doc}\n'
                    f'Date: {date}\n'
                    f'Time: {time}\n'
                    f'Venue: {venue}')
    server.send_message(msg)
    server.quit()
