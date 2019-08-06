# from tempapp import db, bcrypt
# from tempapp.models import User, Record
import numpy as np
from datetime import datetime
import datetime



def add_user():
    hashed_pw = bcrypt.generate_password_hash('1234').decode('utf-8')
    user = User(username='test', email='test@test.com', password=hashed_pw)
    db.session.add(user)
    db.session.commit()


def add_new_record(temp, date):
    user = User.query.filter_by(email='test@test.com').first()
    record = Record(temp=temp, notes='', author=user, date_posted=date)
    db.session.add(record)
    db.session.commit()


def temps_dates():
    low = np.random.uniform(36.3, 36.45, size=14)
    high = np.random.uniform(36.6, 37.0, size=14)
    temp_list = [round(x, 2) for x in np.concatenate((low, high), axis=None)]
 
    numdays = len(temp_list)
    date_begin = datetime.datetime.strptime("21-01-2014", "%d-%m-%Y")
    date_list = [date_begin + datetime.timedelta(days=x) for x in range(numdays)]
    date_end = date_list[-1]
    res = {date_list[i]: temp_list[i] for i in range(len(date_list))}
    return res

for date,temp in temps_dates().items():
    print(temp, date)