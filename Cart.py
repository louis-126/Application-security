import shelve


class Cart:
    def __init__(self,id, cart,owner):
        self.__id = id
        self.__count = 0
        self.__cart = cart
        self.__owner = owner

    def get_cart(self):
        return self.__cart

    def set_cart(self, cart):
        self.__cart = cart

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def add(self, item):
        self.get_cart().append(item)

    def remove(self, item):
        new_cart = list()
        item.set_item_want(0)
        for i in self.get_cart():
            if i.get_item_name() != item.get_item_name():
                new_cart.append(i)

        self.set_cart(new_cart)

    def total(self):
        total = 0
        for item in self.get_cart():
            total += item.get_total_price()
        return total

    def clear_cart(self):
        for item in self.get_cart():
            self.remove(item)

    def checkout(self):
        for item in self.get_cart():
            item.set_item_have(item.get_item_have() - item.get_item_want())

        self.clear_cart()

    def get_count(self):
        for item in self.get_cart():
            self.__count += item.get_item_want()
        return self.__count

    def check(self, item):
        for i in self.get_cart():
            if i.get_item_name() == item.get_item_name():
                return True
        return False

    def get_owner(self):
        return self.__owner

    def set_owner(self, owner):
        self.__owner = owner


class PaidCart:
    def __init__(self, cart):
        PaidCart.id += 1

        db = shelve.open('storage.db', 'c')
        db['PaidID'] = PaidCart.id
        db.close()

        self.__id = PaidCart.id
        self.__count = 0
        self.__cart = cart
        self.__owner = ''

    def get_cart(self):
        return self.__cart

    def set_cart(self, cart):
        self.__cart = cart

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def add(self, item):
        self.get_cart().append(item)

    def remove(self, item):
        new_cart = list()
        item.set_item_want(0)
        for i in self.get_cart():
            if i.get_item_name() != item.get_item_name():
                new_cart.append(i)

        self.set_cart(new_cart)

    def total(self):
        total = 0
        for item in self.get_cart():
            total += item.get_total_price()
        return total

    def clear_cart(self):
        for item in self.get_cart():
            self.remove(item)

    def checkout(self):
        for item in self.get_cart():
            item.set_item_have(item.get_item_have() - item.get_item_want())

        self.clear_cart()

    def get_count(self):
        for item in self.get_cart():
            self.__count += item.get_item_want()
        return self.__count

    def check(self, item):
        for i in self.get_cart():
            if i.get_item_name() == item.get_item_name():
                return True

        return False

    def get_owner(self):
        return self.__owner

    def set_owner(self, owner):
        self.__owner = owner


class Prescription(Cart):
    db = shelve.open('storage.db', 'w')
    id = db['Prescription_ID']
    db.close()

    def __init__(self, cart):
        Prescription.id += 1

        db = shelve.open('storage.db', 'c')
        db['Prescription_ID'] = Prescription.id
        db.close()

        super().__init__(cart)
        self.__id = Prescription.id
        self.__target = ''

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_target(self):
        return self.__target

    def set_target(self, target):
        self.__target = target

