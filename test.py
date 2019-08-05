# from tempapp import db, bcrypt
# from tempapp.models import User, Record
import numpy as np
from datetime import datetime


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


date_begin = np.datetime64('2019-06-28')
low = np.random.uniform(36.3, 36.45, size=14)
high = np.random.uniform(36.6, 37.0, size=14)
temp_list = [round(x, 2) for x in np.concatenate((low, high), axis=None)]
date_end = date_begin + np.timedelta64(len(temp_list), 'D')
date_list64 = np.arange(date_begin, date_end, 1)
date_list = []

date_list64[6].astype(datetime)

# add_user()
# for i in range(len(temp_list)):
#     add_new_record(temp_list[i], date_list[i])