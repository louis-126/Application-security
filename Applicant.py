import datetime
from Users import User


class Applicant(User):
    count_id = 0
    x = datetime.datetime.now()

    def __init__(self, first_name, last_name, nric, email, age, address, gender, nationality, language, phonenumber,
                 qualification,
                 industry, company1,
                 position1, company2, position2, empty1, empty2):
        super().__init__(nric, first_name, last_name, gender, empty1, email, empty2)
        Applicant.count_id += 1
        self.__applicantid = Applicant.count_id
        self.__age = age
        self.__address = address
        self.__phonenumber = phonenumber
        self.__nationality = nationality
        self.__language = language
        self.__qualification = qualification

        self.__industry = industry
        self.__company1 = company1
        self.__position1 = position1
        self.__company2 = company2
        self.__position2 = position2
        self.__date = Applicant.x.strftime("%x")

    def set_applicantid(self, applicant_id):
        self.__applicantid = applicant_id

    def set_age(self, age):
        self.__age = age

    def set_address(self, address):
        self.__address = address

    def set_phonenumber(self, phonenumber):
        self.__phonenumber = phonenumber

    def set_nationality(self, nationality):
        self.__nationality = nationality

    def set_language(self, language):
        self.__language = language

    def set_qualification(self, qualification):
        self.__qualification = qualification

    def set_industry(self, industry):
        self.__industry = industry

    def set_company1(self, company1):
        self.__company1 = company1

    def set_postion1(self, position1):
        self.__position1 = position1

    def set_company2(self, company2):
        self.__company2 = company2

    def set_postion2(self, position2):
        self.__position2 = position2

    def get_applicantid(self):
        return self.__applicantid

    def get_age(self):
        return self.__age

    def get_address(self):
        return self.__address

    def get_phonenumber(self):
        return self.__phonenumber

    def get_nationality(self):
        return self.__nationality

    def get_language(self):
        return self.__language

    def get_qualification(self):
        return self.__qualification

    def get_industry(self):
        return self.__industry

    def get_company1(self):
        return self.__company1

    def get_position1(self):
        return self.__position1

    def get_company2(self):
        return self.__company2

    def get_position2(self):
        return self.__position2

    def get_date(self):
        return self.__date

    def get_pastemployment(self):
        display = "Company: {} | Position: {} \n\nCompany: {} | Position: {}".format(self.__company1, self.__position1,
                                                                                     self.__company2, self.__position2)
        return display


def display_info(person):
    print("Name: {}".format(person.name))
    print("NRIC: {}".format(person.nric))
    print("Email: {}".format(person.email))
    print("Age: {}".format(person.age))
    print("Address {}".format(person.address))
    print("Gender: {}".format(person.get_gender()))
    print("Phone Number: {}".format(person.get_phonenumber()))
    print("Qualification: {}".format(person.get_qualification()))
    print("Past Employment: {}".format(person.get_pastemploymentlist()))
