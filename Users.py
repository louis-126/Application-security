class User:
    def __init__(self, NRIC, first_name, last_name, gender, dob, email, password):
        self.__NRIC = NRIC
        self.__first_name = first_name
        self.__last_name = last_name
        self.__gender = gender
        self.__dob = dob
        self.__email = email
        self.__password = password
        self.__role = ""
        self.__url = ""

    def get_NRIC(self):
        return self.__NRIC

    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_name(self):
        return self.get_first_name() + " " + self.get_last_name()

    def get_gender(self):
        return self.__gender

    def get_dob(self):
        return self.__dob

    def get_email(self):
        return self.__email

    def get_password(self):
        return self.__password

    def get_role(self):
        return self.__role

    def get_appointment(self):
        return self.__role

    def get_url(self):
        return self.__url

    def set_NRIC(self, NRIC):
        self.__NRIC = NRIC

    def set_first_name(self, fname):
        self.__first_name = fname

    def set_last_name(self, lname):
        self.__last_name = lname

    def set_gender(self, gender):
        self.__gender = gender

    def set_dob(self, dob):
        self.__dob = dob

    def set_email(self, email):
        self.__email = email

    def set_password(self, pwd):
        self.__password = pwd

    def set_role(self, role):
        self.__role = role

    def set_url(self, url):
        self.__url = url


class Doctor(User):
    def __init__(self, NRIC, first_name, last_name, gender, dob, email, password, specialization, url):
        super().__init__(NRIC, first_name, last_name, gender, dob, email, password)
        self.__specialization = specialization
        self.__appointment_no = 0
        self.__url = url

    def get_url(self):
        return self.__url

    def set_url(self, url):
        self.__url = url

    def get_specialization(self):
        return self.__specialization

    def set_specialization(self, specialization):
        self.__specialization = specialization

    def get_appointment_no(self):
        return self.__appointment_no

    def set_appointment_no(self, number):
        self.__appointment_no = number
