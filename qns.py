class FAQ:
    def __init__(self,id, question, answer, date):
        self.__qns_id = id
        self.__question = question
        self.__answer = answer
        self.__date = date

    def get_qns_id(self):
        return self.__qns_id

    def get_question(self):
        return self.__question

    def get_answer(self):
        return self.__answer

    def get_date(self):
        return self.__date

    def set_qns_id(self, qns_id):
        self.__qns_id = qns_id

    def set_question(self, question):
        self.__question = question

    def set_answer(self, answer):
        self.__answer = answer

    def set_date(self, date):
        self.__date = date