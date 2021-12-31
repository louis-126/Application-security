from __init__ import *
import datetime
import shelve
user = Users.query.all()
for i in user:
    i.password_expiry_date
expired = Users.query.filter_by(NRIC='T2222222A').first()
expired.password_expiry_date = datetime.datetime(2021,9,11)
