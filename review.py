

class Reviews:
    def __init__(self, title, content, date,name):

        self.__review_id = ''
        self.__title = title
        self.__content = content
        self.__date = date
        self.__name = name

    def get_review_id(self):
        return self.__review_id

    def get_title(self):
        return self.__title

    def get_content(self):
        return self.__content

    def get_date(self):
        return self.__date

    def get_name(self):
        return self.__name

    def set_review_id(self,review_id):
        self.__review_id = review_id

    def set_title(self, title):
        self.__title = title

    def set_content(self, content):
        self.__content = content

    def set_date(self, date):
        self.__date = date

    def set_name(self,name):
        self.__name = name