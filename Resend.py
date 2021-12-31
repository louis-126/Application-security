class Resend:
    def __init__(self, nric, email, age, gender, nationality, language, phoneno, quali, industry):
        self.__nric = nric
        self.__email = email
        self.__age = age
        self.__gender = gender
        self.__nationality = nationality
        self.__language = language
        self.__phoneno = phoneno
        self.__quali = quali
        self.__industry = industry

    def get_nric(self):
        return self.__nric

    def get_email(self):
        return self.__email

    def get_age(self):
        return self.__age

    def get_gender(self):
        return self.__gender

    def get_nationality(self):
        return self.__nationality

    def get_language(self):
        return self.__language

    def get_phoneno(self):
        return self.__phoneno

    def get_quali(self):
        return self.__quali

    def get_industry(self):
        return self.__industry

    def set_nric(self, nric):
        self.__nric = nric

    def set_email(self, email):
        self.__email = email

    def set_gender(self, gender):
        self.__gender = gender

    def set_nationality(self, nationality):
        self.__nationality = nationality

    def set_langauge(self, language):
        self.__language = language

    def set_phoneno(self, phoneno):
        self.__phoneno = phoneno

    def set_quali(self, quali):
        self.__quali = quali

    def set_industry(self, industry):
        self.__industry = industry
