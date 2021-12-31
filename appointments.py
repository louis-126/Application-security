from datetime import datetime


class Appointment:
    def __init__(self, date, time, department, venue):
        self.__date = date
        self.__time = time
        self.__department = department
        self.__venue = venue
        self.__doctor = ''
        self.__patient = ''
        self.__id = ''
        self.__comment = ''
        self.__url = ''

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time

    def get_department(self):
        return self.__department

    def get_venue(self):
        return self.__venue

    def get_doctor(self):
        return self.__doctor

    def get_patient(self):
        return self.__patient

    def get_id(self):
        return self.__id

    def get_comment(self):
        return self.__comment

    def get_datetime(self):
        date = datetime.strftime(self.__date, '%Y-%m-%d')
        dt = date + " " + self.__time
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        return dt

    def get_url(self):
        return self.__url

    def set_date(self, date):
        self.__date = date

    def set_time(self, time):
        self.__time = time

    def set_department(self, dpmt):
        self.__department = dpmt

    def set_venue(self, venue):
        self.__venue = venue

    def set_doctor(self, doctor):
        self.__doctor = doctor

    def set_patient(self, patiet):
        self.__patient = patiet

    def set_id(self, id):
        self.__id = id

    def set_comment(self, comment):
        self.__comment = comment

    def set_url(self, url):
        self.__url = url
