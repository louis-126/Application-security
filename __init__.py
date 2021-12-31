from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer  # New (Dont delete this I need this still - Mouse)
import Applicant, appointments,Resend, Cart, review
import smtplib
import send_email
from Forms import *
from datetime import datetime, timedelta
from pyechart import bargraph, applicationbargraph, addressbargraph, agerangebargraph, monthlyQnbargraph, usernumber
from functools import wraps #New
import logging  # New
from datetime import date  # New
from shutil import copyfile  # New
import json  # New
from Crypto.Hash import HMAC, SHA512  # New
from Crypto.PublicKey import RSA  # New
from Crypto.Signature import pkcs1_15  # New
import re  # New
from collections import Counter  # New
import csv  # New
import pandas as pd  # New
from matplotlib import pyplot as plt  # New
from sqlalchemy import text  # New
#from faceRocgn import authFace  # New
from Item import Item
from qns import FAQ
from Users import User
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests import get
import bcrypt  # JXADDED
import os  # JXADDED


app = Flask(__name__, static_url_path='/static')
app = Flask(__name__,instance_path=r'C:\Users\louis\PycharmProjects\AppSec(lastest)\AppSecDone\protected')  # Change this to your own directory
limiter = Limiter(app, key_func=get_remote_address)
app.config["SECRET_KEY"] = b'o5Dg987*&G^@(E&FW)}'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "nypflask123@gmail.com"
app.config["MAIL_PASSWORD"] = "NYPflask123"
app.config["DEFAULT_MAIL_SENDER"] = "nypflask123@gmail.com"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6Lfxq5wbAAAAADxegwNp-91fPbck8Oybuk4LewrF"  # New
app.config["RECAPTCHA_PRIVATE_KEY"] = "6Lfxq5wbAAAAAK6I8ws566Ym4S6o9SCmD_BS5YBE"  # New
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SECURE"] = True  #browser to send a cookie only over protected HTTPS connection
app.config["SESSION_COOKIE_HTTPONLY"] = True  #browser to hide cookie content from javscript code
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'  #Do not allow sending cookies from another sites when doing request other than GET method (to prevent CSRF)

mail = Mail(app)
db = SQLAlchemy(app)
app.config["SESSION_TYPE"] = 'sqlalchemy'
app.config["SESSION_SQLALCHEMY"] = db
sess = Session(app)



# SQL Tables
class Users(db.Model):
    NRIC = db.Column(db.String(10), primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    dob = db.Column(db.DateTime)
    password = db.Column(db.LargeBinary(100), nullable=False)
    password_expiry_date = db.Column(db.DateTime)
    email = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False)
    url = db.Column(db.String(100))

    def __repr__(self):
        return f"NRIC: {self.NRIC}, Name :{self.fname + ' ' + self.lname} , Role: {self.role}"


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    have = db.Column(db.Float, nullable=False)
    want = db.Column(db.Float, nullable=False)
    bio = db.Column(db.String(20))
    picture = db.Column(db.String(20))

    def __repr__(self):
        return f"Name: {self.name},Price: {self.price}"


class FAQs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120))
    answer = db.Column(db.String(120))
    date = db.Column(db.DateTime)

def special_requirement(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if is_admin():
                return f(*args, **kwargs)

            else:
                flash("Access denied", "danger")
                return redirect(url_for('home'))
        except:

            flash("Access denied", "danger")

            #New
            username = "NIL"
            ipaddress = get('https://api.ipify.org').text
            a = customFilter(username, ipaddress)
            logger.addFilter(a)
            logger.error(
                f"User with IP address %s tried to use Special Requirement Functionality: (Only authorized for account T1234987A)",
                ipaddress)

            return redirect(url_for('home'))

    return wrap


@app.route('/protected/<path:filename>')
@special_requirement
def protected(filename):
    try:
            return send_from_directory(os.path.join(app.instance_path, ''), filename)
    except:
        flash("Access denied", "danger")

        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"Unauthorized user with IP address %s tried to access a protected file path", ipaddress)

        return redirect(url_for('home'))

def is_admin():
    if session['user-role'] == 'Admin':
        return True
    else:
        return False


@app.route('/')
def home():
    try:
        user = session['user']
        today = datetime.today().date()
        expire_date = session['user-pwd-expiry']
        expire_date = datetime.strptime(expire_date, '%Y-%m-%d').date()
        expire_time = (expire_date - today).days
        if expire_time <= 0:
            flash(f'Your password has expired,please change to continue!', 'danger')
            return redirect(url_for('change_password'))
        elif expire_time <= 30:
            flash(f'Your password will expire in {expire_time} days! Please change soon!', 'danger')
            return render_template('home.html')
        else:
            return render_template('home.html')
    except KeyError as e:
        return render_template('home.html')


@app.route('/pharmacy', methods=['GET', 'POST'])
@limiter.limit('20 per minute')  # JXADDED
def show_items():
    search = SearchBar(request.form)
    if request.method == 'POST' and search.validate():
        item_list = []
        start_item_list = []
        contain_item_list = []
        items = Items.query.all()
        for i in items:
            item = Item(i.id, i.name, i.price, i.have, i.bio, i.picture)
            item_list.append(item)
            if item.get_item_name().lower().startswith(search.search.data.lower()):
                start_item_list.append(item)
            elif search.search.data.lower() in item.get_item_name().lower():
                contain_item_list.append(item)
            item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)

    item_list = []
    items = Items.query.all()
    for i in items:
        item = Item(i.id, i.name, i.price, i.have, i.bio, i.picture)
        item_list.append(item)

    return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)


@app.route('/purchaseHistory', methods=['GET', 'POST'])
def purchaseHistory():
    try:
        search = SearchBar(request.form)
        user_id = session['user-NRIC']
        if request.method == "POST":
            sort_amount = search.history.data
            if search.search.data != "":
                db = shelve.open('storage.db', 'c')
                cart_dict = db['Paid']

                cart_list = []
                for key in cart_dict:
                    cart = cart_dict[key]
                    if cart.get_owner() == user_id and cart.get_id() == int(search.search.data):
                        cart_list.append(cart)

                return render_template('Pharmacy/purchaseHistory.html', form=search, cart_list=cart_list)
            elif sort_amount is not None:
                db = shelve.open('storage.db', 'c')
                cart_dict = db['Paid']

                cart_list = []
                for key in cart_dict:
                    cart = cart_dict[key]
                    if cart.get_owner() == user_id:
                        cart_list.append(cart)

                reverse_cart_list = list(reversed(cart_list))
                cart_list = []

                for cart in reverse_cart_list:
                    if len(cart_list) < int(sort_amount):
                        cart_list.append(cart)
                    else:
                        break

                return render_template('Pharmacy/purchaseHistory.html', form=search, cart_list=cart_list)
            else:
                return redirect(url_for('purchaseHistory'))

        db = shelve.open('storage.db', 'c')
        cart_dict = db['Paid']

        cart_list = []
        for key in cart_dict:
            cart = cart_dict[key]
            if cart.get_owner() == user_id:
                cart_list.append(cart)

        reverse_cart_list = list(reversed(cart_list))
        cart_list = []

        for cart in reverse_cart_list:
            if len(cart_list) < 10:
                cart_list.append(cart)
            else:
                break

        return render_template('Pharmacy/purchaseHistory.html', form=search, cart_list=cart_list)
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use Purchase History functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        if is_admin():
            total_sales = int()
            general_list = list()
            general_low_list = list()
            prescribed_list = list()
            prescribed_low_list = list()
            paid_list = list()
            pres_list = list()
            db = shelve.open('storage.db', 'r')
            paid_dict = db['Paid']
            pres_dict = db['Prescription']
            item_dict = db['Items']
            db.close()

            for key in paid_dict:
                paid = paid_dict[key]
                total_sales += paid.total()
                paid_list.append(paid)

            reverse_paid_list = reversed(paid_list)
            paid_list = []

            for cart in reverse_paid_list:
                if len(paid_list) < 10:
                    paid_list.append(cart)

            for key in pres_dict:
                pres = pres_dict[key]
                pres_list.append(pres)

            reverse_pres_list = reversed(pres_list)
            pres_list = []

            for cart in reverse_pres_list:
                if len(pres_list) < 10:
                    pres_list.append(cart)

            for key in item_dict:
                item = item_dict[key]
                if not isinstance(item, Item.Prescribed):
                    general_list.append(item)
                    if item.get_item_have() < 100:
                        general_low_list.append(item)
                else:
                    prescribed_list.append(item)
                    if item.get_item_have() < 100:
                        prescribed_low_list.append(item)

            no_paid = len(paid_dict)
            no_items = len(item_dict)
            no_general = len(general_list)
            no_prescribed = len(prescribed_list)
            no_pres = len(pres_dict)

            return render_template('Pharmacy/dashboard.html', pres_list=pres_list, paid_list=paid_list,
                                   glow_list=general_low_list, plow_list=prescribed_low_list, no_general=no_general,
                                   no_prescribed=no_prescribed, no_paid=no_paid, no_items=no_items, no_pres=no_pres,
                                   total=total_sales)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the dashboard functionality without logging in", ipaddress)
        return redirect(url_for('login'))


# CRUD Items
@app.route('/createItem', methods=['GET', 'POST'])
def create_item():
    try:
        if is_admin():
            create_item_form = CreateItemForm(request.form)
            if request.method == 'POST' and create_item_form.validate():
                item_dict = {}
                db = shelve.open('storage.db', 'c')

                try:
                    item_dict = db['Items']
                except:
                    print("Error in retrieving Items from storage.db.")
                    # New
                    username = session["user-NRIC"]
                    ipaddress = get('https://api.ipify.org').text
                    f = customFilter(username, ipaddress)
                    logger.addFilter(f)
                    logger.error(f"Error retrieving Items from storage.db")
                if not create_item_form.prescription.data:
                    item = Item.Item(create_item_form.name.data, round(create_item_form.price.data, 2),
                                     create_item_form.have.data,
                                     create_item_form.bio.data, create_item_form.picture.data)
                else:
                    item = Item.Prescribed(create_item_form.name.data, round(create_item_form.price.data, 2),
                                           create_item_form.have.data,
                                           create_item_form.bio.data, create_item_form.picture.data)
                item.set_item_id(id(item))
                item_dict[item.get_item_id()] = item
                if isinstance(item, Item.Item):
                    item.add_item_tag('new')
                db['Items'] = item_dict

                db.close()

                # New
                username = session["user-NRIC"]
                role = session['user-role']
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.info(f"%s %s has created the item: %s (ID No: %s)", role, username, create_item_form.name.data,
                            item.get_item_id())

                return redirect(url_for('inventory'))
            return render_template('Pharmacy/createItem.html', form=create_item_form)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Create Item functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/inventory')
def inventory():
    try:
        if is_admin():
            db = shelve.open('storage.db', 'r')
            item_dict = db['Items']
            db.close()

            item_list = []
            for key in item_dict:
                item = item_dict.get(key)
                item_list.append(item)

            return render_template('Pharmacy/inventory.html', items_list=item_list)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Inventory functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/updateItem/<int:id>/', methods=['GET', 'POST'])
def update_item(id):
    try:
        if is_admin():
            update_item_form = CreateItemForm(request.form)

            if request.method == 'POST' and update_item_form.validate():
                db = shelve.open('storage.db', 'w')
                item_dict = db['Items']

                item = item_dict.get(int(id))
                oldname = item.get_item_name()  # New
                item.set_item_name(update_item_form.name.data)
                item.set_item_price(update_item_form.price.data)
                item.set_item_have(update_item_form.have.data)
                item.set_item_bio(update_item_form.bio.data)
                item.set_item_picture(update_item_form.picture.data)

                db['Items'] = item_dict
                db.close()

                # New
                username = session["user-NRIC"]
                role = session['user-role']
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.info(f"%s %s has updated the item %s to: %s (ID No: %s)", role, username, oldname,
                            update_item_form.name.data, item.get_item_id())

                return redirect(url_for('inventory'))
            else:
                db = shelve.open('storage.db', 'r')
                item_dict = db['Items']
                db.close()

                item = item_dict.get(int(id))
                update_item_form.name.data = item.get_item_name()
                update_item_form.price.data = item.get_item_price()
                update_item_form.have.data = item.get_item_have()
                update_item_form.bio.data = item.get_item_bio()
                update_item_form.picture.data = item.get_item_picture()

                return render_template('Pharmacy/updateItem.html', form=update_item_form)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Update Item functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/deleteItem/<int:id>', methods=['POST'])
def delete_item(id):
    db = shelve.open('storage.db', 'w')
    item_dict = db['Items']

    item_dict.pop(int(id))

    db['Items'] = item_dict
    db.close()

    # New
    username = session["user-NRIC"]
    role = session['user-role']
    item = id
    ipaddress = get('https://api.ipify.org').text
    f = customFilter(username, ipaddress)
    logger.addFilter(f)
    logger.info(f"%s %s has deleted the item: ID No: %s (Item Numbers are not reused)", role, username, item)

    return redirect(url_for('inventory'))


# CRUD Shopping Cart
@app.route('/purchaseItem/<int:id>/', methods=['GET', 'POST'])
def buy_item(id):
    try:
        buy_item_form = BuyItemForm(request.form)

        if request.method == 'POST' and buy_item_form.validate():
            db = shelve.open('storage.db', 'w')
            item_dict = db['Items']
            cart_dict = db['Cart']

            user_id = session['user-NRIC']

            item = item_dict.get(int(id))
            item.set_item_want(buy_item_form.want.data)

            try:
                cart = cart_dict[user_id]

                if item.get_item_want() > item.get_item_have():
                    item.set_item_want(0)
                    flash("Not enough stock at the moment, try again later", 'danger')
                elif cart.check(item):
                    cart.remove(item)
                    item.set_item_want(buy_item_form.want.data)
                    cart.add(item)
                else:
                    cart.add(item)

            except KeyError:
                temp_cart = [item]
                cart = Cart.Cart(temp_cart)
                cart_dict[user_id] = cart

            finally:
                db['Cart'] = cart_dict
                db['Items'] = item_dict
                db.close()

            return redirect(url_for('show_items'))

        else:
            db = shelve.open('storage.db', 'r')
            item_dict = db['Items']
            db.close()

            item = item_dict.get(id)
            buy_item_form.want.data = item.get_item_want()

            return render_template('Pharmacy/buyItem.html', form=buy_item_form, name=item.get_item_name(),
                                   bio=item.get_item_bio(), price=item.get_item_price(),
                                   picture=item.get_item_picture(),
                                   have=item.get_item_have())
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Purchase Item functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/shoppingCart', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # JXADDED
def shopping_cart():
    try:
        search = SearchBar(request.form)
        if request.method == 'POST':
            db = shelve.open('storage.db', 'r')
            cart_dict = db['Cart']
            db.close()

            user_id = session['user-NRIC']

            try:
                cart = cart_dict[user_id]
            except KeyError:
                cart = Cart.Cart([])

            item_list = cart.get_cart()
            total = cart.total()
            count = cart.get_count()

            start_item_list = []
            contain_item_list = []
            for item in cart.get_cart():
                if item.get_item_name().lower().startswith(search.search.data.lower()):
                    start_item_list.append(item)
                elif search.search.data.lower() in item.get_item_name().lower():
                    contain_item_list.append(item)

                item_list = start_item_list + contain_item_list

            return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total,
                                   count=count)
        db = shelve.open('storage.db', 'r')
        cart_dict = db['Cart']
        db.close()

        user_id = session['user-NRIC']

        try:
            cart = cart_dict[user_id]
        except KeyError:
            cart = Cart.Cart([])

        item_list = cart.get_cart()
        total = cart.total()
        count = cart.get_count()

        return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total,
                               count=count)
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Shopping Cart functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/shoppingCart/<int:id>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # JXADDED
def specific_cart(id):
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        cart_dict = db['Paid']
        db.close()

        cart = cart_dict[id]

        item_list = cart.get_cart()
        total = cart.total()
        count = cart.get_count()

        start_item_list = []
        contain_item_list = []
        for item in cart.get_cart():
            if item.get_item_name().lower().startswith(search.search.data.lower()):
                start_item_list.append(item)
            elif search.search.data.lower() in item.get_item_name().lower():
                contain_item_list.append(item)

            item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total,
                               count=count)
    db = shelve.open('storage.db', 'r')
    cart_dict = db['Paid']
    db.close()

    cart = cart_dict[id]

    item_list = cart.get_cart()
    total = cart.total()
    count = cart.get_count()

    return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total, count=count)


@app.route('/checkout', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # JXADDED
def checkout():
    try:
        checkout_form = CheckoutForm(request.form)

        if (request.method == 'POST' and checkout_form.validate()) or session['user-role'] == 'Admin':
            try:
                session['user']
            except KeyError:
                return redirect(url_for('paid'))
            else:
                db = shelve.open('storage.db', 'w')
                cart_dict = db['Cart']
                item_dict = db['Items']
                paid_dict = db['Paid']
                users_dict = db["Users"]

                user_id = session['user-NRIC']
                user = users_dict[user_id]

                cart = cart_dict[user_id]

                paid = Cart.PaidCart(cart.get_cart())

                paid_dict[paid.get_id()] = paid

                paid.set_owner(user_id)

                db['Paid'] = paid_dict

                cart.checkout()
                cart_dict.pop(user_id)

                for key in item_dict:
                    item = item_dict[key]
                    if item.get_item_want() != 0:
                        item.set_item_have(item.get_item_have() - item.get_item_want())
                        item.set_item_want(0)
                        if "hot" not in item.get_item_tag() and not isinstance(item, Item.Prescribed):
                            item.add_item_tag('hot')

                db['Items'] = item_dict
                db['Cart'] = cart_dict
                db.close()

                msg = Message(subject='Nanyang Polyclinic order confirmation',
                              sender=app.config.get("MAIL_USERNAME"),
                              recipients=[user.get_email()],
                              body='Your Purchase with Nanyang Polyclinic has been confirmed \n Cart Number: ' + str(
                                  cart.get_id()))
                mail.send(msg)

                return redirect(url_for('paid'))
        return render_template('Pharmacy/checkout.html', form=checkout_form)
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Checkout functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/removeItem/<int:id>', methods=['POST'])
def remove_item(id):
    db = shelve.open('storage.db', 'c')
    item_dict = db['Items']
    cart_dict = db['Cart']

    user_id = session['user-NRIC']

    cart = cart_dict[user_id]

    item = item_dict.get(id)
    item.set_item_want(0)
    cart.remove(item)

    db['Items'] = item_dict
    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('shopping_cart'))


@app.route('/clearCart', methods=['POST'])
def clear_cart():
    db = shelve.open('storage.db', 'w')
    cart_dict = db['Cart']

    user_id = session['user-NRIC']

    cart = cart_dict[user_id]
    cart.clear_cart()

    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('shopping_cart'))


@app.route('/complete')
def paid():
    return render_template('Pharmacy/complete.html')


# CRUD Prescription
@app.route('/prescription', methods=['GET', 'POST'])
def prescription():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item_list = []
        start_item_list = []
        contain_item_list = []
        for key in item_dict:
            item = item_dict.get(key)
            if isinstance(item, Item.Prescribed):
                if item.get_item_name().lower().startswith(search.search.data.lower()):
                    start_item_list.append(item)
                elif search.search.data.lower() in item.get_item_name().lower():
                    contain_item_list.append(item)

                item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/prescription.html', items_list=item_list, form=search)

    db = shelve.open('storage.db', 'r')
    item_dict = db['Items']
    db.close()

    item_list = []
    for key in item_dict:
        item = item_dict.get(key)
        if isinstance(item, Item.Prescribed):
            item_list.append(item)

    return render_template('Pharmacy/prescription.html', items_list=item_list, form=search)


@app.route('/prescribeItem/<int:id>/', methods=['GET', 'POST'])
def prescribe_item(id):
    prescribe_item_form = PrescriptionForm(request.form)

    if request.method == 'POST' and prescribe_item_form.validate():
        db = shelve.open('storage.db', 'w')
        item_dict = db['Items']
        pres_dict = db['Prescription']

        user_id = session['user-NRIC']
        item = item_dict.get(id)

        item.set_item_want(prescribe_item_form.quantity.data)

        item.set_item_dosage(
            str(prescribe_item_form.dosage_times.data) + " Times " + prescribe_item_form.dosage_interval.data)

        try:
            pres = pres_dict[user_id]

            if item.get_item_want() > item.get_item_have():
                item.set_item_want(0)
                flash("Not enough stock at the moment, try again later", 'danger')
            elif pres.check(item):
                pres.remove(item)
                item.set_item_want(prescribe_item_form.quantity.data)
                item.set_item_dosage(
                    str(prescribe_item_form.dosage_times.data) + " times " + prescribe_item_form.dosage_interval.data)
                pres.add(item)
            else:
                pres.add(item)
                db['Items'] = item_dict

        except KeyError:
            temp_cart = [item]
            pres = Cart.Prescription(temp_cart)
            pres_dict[user_id] = pres

        finally:
            db['Prescription'] = pres_dict
            db.close()

        return redirect(url_for('prescription'))

    else:
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item = item_dict.get(id)
        prescribe_item_form.quantity.data = item.get_item_want()

        return render_template('Pharmacy/prescriptionForm.html', form=prescribe_item_form, name=item.get_item_name(),
                               bio=item.get_item_bio(), price=item.get_item_price(), picture=item.get_item_picture(),
                               have=item.get_item_have())


@app.route('/prescription/prescribe', methods=['GET', 'POST'])
def prescription_cart():
    try:
        if is_admin():
            search = SearchBar(request.form)
            if request.method == 'POST':
                db = shelve.open('storage.db', 'r')
                pres_dict = db['Prescription']
                db.close()

                user_id = session['user-NRIC']

                try:
                    pres = pres_dict[user_id]

                except KeyError:
                    pres = Cart.Prescription([])

                item_list = pres.get_cart()
                total = pres.total()
                count = pres.get_count()

                start_item_list = []
                contain_item_list = []
                for item in pres.get_cart():
                    if item.get_item_name().lower().startswith(search.search.data.lower()):
                        start_item_list.append(item)
                    elif search.search.data.lower() in item.get_item_name().lower():
                        contain_item_list.append(item)

                    item_list = start_item_list + contain_item_list

                return render_template('Pharmacy/prescriptionCart.html', items_list=item_list, form=search, total=total,
                                       count=count)
            db = shelve.open('storage.db', 'r')
            pres_dict = db['Prescription']
            db.close()

            user_id = session['user-NRIC']

            try:
                pres = pres_dict[user_id]

            except KeyError:
                pres = Cart.Prescription([])

            item_list = pres.get_cart()
            total = pres.total()
            count = pres.get_count()

            return render_template('Pharmacy/prescriptionCart.html', items_list=item_list, form=search, total=total,
                                   count=count)
        else:
            flash('Access denied', 'danger')
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Prescription Cart functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/prescribe', methods=['GET', 'POST'])
def prescribe():
    prescribe_form = PrescribeForm(request.form)

    if request.method == 'POST' and prescribe_form.validate():
        patient_id = prescribe_form.patient_nric.data
        db = shelve.open('storage.db', 'w')
        pres_dict = db['Prescription']

        user_id = session['user-NRIC']

        pres = pres_dict[user_id]

        pres.set_owner(user_id)

        pres_dict[patient_id] = pres
        pres_dict.pop(user_id)

        db['Prescription'] = pres_dict
        db.close()
        return redirect(url_for('prescription'))
    else:
        return render_template('Pharmacy/prescribe.html', form=prescribe_form)


@app.route('/addToCart', methods=['POST'])
def addPrescription():
    db = shelve.open('storage.db', 'c')
    cart_dict = db['Cart']
    pres_dict = db['Prescription']

    user_ID = session['user-NRIC']

    pres = pres_dict[user_ID]

    cart = []
    for item in pres.get_cart():
        try:
            cart = cart_dict[user_ID]

        except KeyError:
            cart = Cart.Cart([item])

        else:
            cart.add(item)

        finally:
            cart_dict[user_ID] = cart

    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('shopping_cart'))


# Login system
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # JXADDED
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        sql = text("Select * from Users where NRIC = :x")
        c = db.engine.execute(sql, x=form.NRIC.data)
        user = None
        for i in c:
            user = i
        try:
            if form.NRIC.data == user.NRIC:
                # New
                username = form.NRIC.data
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.error(f"Username of %s tried to re-register", form.NRIC.data)
                flash("This NRIC is already in used.You can login to access our service.", "danger")
                return redirect(url_for('register'))
        except AttributeError:
            saltysalt = bcrypt.gensalt()  # JXADDED
            form.Password.data = bcrypt.hashpw(form.Password.data.encode(encoding='UTF-8'), saltysalt)  # JXADDED
            #print(form.Password.data)  # JXADDED (Test for password)
            expiry_time = timedelta(days=90)
            current_date = datetime.today()
            expire_date = (current_date + expiry_time).date()
            user = Users(NRIC=form.NRIC.data, fname=form.FirstName.data, lname=form.LastName.data,
                         gender=form.Gender.data, dob=form.Dob.data,
                         password=form.Password.data, password_expiry_date=expire_date, email=form.Email.data,
                         role="Patient", url="url")
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.FirstName.data} {form.LastName.data}!', 'success')
            username = form.NRIC.data
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.info(f"New account (Username: %s, Role: Patient) has been registered", form.NRIC.data)
            return redirect(url_for('register'))
    return render_template('Login/register.html', form=form)


# Face Recognition Login
@app.route('/login', methods=['GET', 'POST'])  # JXADDED (Edited whole thing)
@limiter.limit("10 per minute")  # JXADDED
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        # Parameterized queries
        sql_username = text("Select * from Users where NRIC = :x")
        c2 = db.engine.execute(sql_username, x=form.NRIC.data)
        # SQLalchemy query
        # user = Users.query.filter_by(NRIC=form.NRIC.data).first()
        user = None
        for i in c2:
            user = i
        try:
            if bcrypt.checkpw(form.Password.data.encode(encoding='UTF-8'), user.password):
                username = user.fname + " " + user.lname
                expirydate = user.password_expiry_date.split()
                expirydate=expirydate[0]
                session["user"] = username
                session["user-role"] = user.role
                session["user-NRIC"] = user.NRIC
                session['user-pwd-expiry'] = expirydate
                if session["user-role"] == "Admin":
                    # face = authFace()
                    # if face == 'WEN HAO':
                    session["user"] = username
                    flash(
                        f'{username} has logged in!',
                        'success')
                    return redirect(url_for('home'))
                # else:
                #     flash('Incorrect username or password', 'danger')

                elif session["user-role"] == "Patient" or session["user-role"] == "Doctor":
                    session["user"] = username
                    flash(
                        f'{username} has logged in!',
                        'success')
                    return redirect(url_for('home'))

            else:
                username = form.NRIC.data
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.error(
                    f"User with IP address %s failed to login into the account with username %s: Incorrect Password",
                    ipaddress, form.NRIC.data)
                flash('Incorrect username or password', 'danger')

        except AttributeError:
            flash('Incorrect username or password', 'danger')
            # New
            username = form.NRIC.data
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(
                f"User with IP address %s failed to login into non-existing account with username %s: Incorrect NRIC",
                ipaddress, form.NRIC.data)

    return render_template('Login/login.html', form=form)


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)


@app.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("home"))


# Profile
@app.route('/profile', methods=["GET", "POST"])
@limiter.limit("10 per minute")  # JXADDED
def profile():
    form = UpdateProfileForm(request.form)
    user = Users.query.filter_by(NRIC=session['user-NRIC']).first()
    userObj = User(user.NRIC,user.fname,user.lname,user.gender,user.dob,user.email,user.password)
    if request.method == "POST" and form.validate():
        user.email = form.Email.data
        user.dob = form.Dob.data
    db.session.commit()
    # New
    username = "NIL"
    ipaddress = get('https://api.ipify.org').text
    f = customFilter(username, ipaddress)
    logger.addFilter(f)
    logger.error(f"User with IP address %s successfully updated their Profile Information", ipaddress)
    return render_template("Login/profile.html", form=form,user=userObj)


# User password management
@app.route('/change_password', methods=["GET", "POST"])
@limiter.limit('3 per day')  # JXADDED
def change_password():
    try:
        user = session['user']
        form = ChangePasswordForm(request.form)
        if request.method == "POST" and form.validate():
            userpwd = Users.query.filter_by(NRIC=session['user-NRIC']).first()
            saltysalt = bcrypt.gensalt()
            form.Password.data = bcrypt.hashpw(form.Password.data.encode(encoding='UTF-8'), saltysalt)
            userpwd.password = form.Password.data
            expiry_time = timedelta(days=90)
            current_date = datetime.today()
            expire_date = (current_date + expiry_time).date()
            userpwd.password_expiry_date = expire_date
            db.session.commit()
            # New
            username = session["user-NRIC"]
            role = session['user-role']
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.info(f"%s %s changed their password", role, username)
            flash('Password changed successfully, please re-login', 'success')
            logout()
            return render_template('home.html')
        else:
            return render_template('Login/change_password.html', form=form)
    except KeyError:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the change password functionality without logging in",ipaddress)
        logger.error(f"User with IP address %s tried to use the change password functionality without logging in",ipaddress)
        return redirect(url_for('login'))


# Helper functions to reset email (METHOD 1) (INSECURE DESERIALIZATION)
# New
def generate_confirmation_token(email):
    global signature
    global keypair
    global macs

    emails = json.dumps(email)

    private_keyfile = "RSA_private.pem"
    keypair = RSA.generate(2048)
    private_key = keypair.export_key()
    privatefile_out = open(private_keyfile, "wb")
    privatefile_out.write(private_key)
    privatefile_out.close()

    private_key = RSA.import_key(open(private_keyfile).read())
    hash_value = SHA512.new(bytes(emails, "utf8"))
    signature = pkcs1_15.new(private_key).sign(hash_value)

    key = b"y/B?E(H+MbQeThWmZq4t7w!z$C&F)J@N"
    macs = HMAC.new(key, digestmod=SHA512)
    macs.update(emails.encode("utf8"))

    # New
    username = "NIL"
    ipaddress = get('https://api.ipify.org').text
    f = customFilter(username, ipaddress)
    logger.addFilter(f)
    logger.info(f"Confirmation token, HMAC, and Digital Signature generated for email's %s password reset", email)

    return emails


# New
def confirm_token(token):
    reset_password()
    emails = formemail
    try:
        public_keyfile = "RSA_public.pem"

        reset_password()
        token = token[:-1]
        mac = macs

        public_key = keypair.publickey().export_key()
        publicfile_out = open(public_keyfile, "wb")
        publicfile_out.write(public_key)
        publicfile_out.close()

        # Verify
        key = b"y/B?E(H+MbQeThWmZq4t7w!z$C&F)J@N"
        mac_computed = HMAC.new(key, digestmod=SHA512)
        mac_computed.update(token.encode("utf8"))
        try:
            mac_computed.verify(mac.digest())
            # verify
            public_key = RSA.import_key(open(public_keyfile).read())
            hash_value_verify = SHA512.new(bytes(token, "utf8"))
            try:
                pkcs1_15.new(public_key).verify(hash_value_verify, signature)
                try:
                    loademail = json.loads(token)
                    # New
                    username = "NIL"
                    ipaddress = get('https://api.ipify.org').text
                    f = customFilter(username, ipaddress)
                    logger.addFilter(f)
                    logger.info(f"Confirmation token successfully validated for email: %s", emails)
                    return loademail
                except Exception as e:
                    # New
                    username = "NIL"
                    ipaddress = get('https://api.ipify.org').text
                    f = customFilter(username, ipaddress)
                    logger.addFilter(f)
                    logger.error(f"Error deserializing token for email account %s: Error - %s", emails, e)
            except(ValueError, TypeError) as e:
                flash("The token is invalid, do not change its contents!", "danger")
                # New
                username = "NIL"
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.error(f"Token for %s has had its contents changed: Error - %s", emails, e)
        except ValueError as e:
            flash("The token is invalid, do not change its contents!", "danger")
            # New
            username = "NIL"
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(f"Token for %s has had its contents changed: Error - %s", emails, e)
    except Exception as e:
        flash("The token is invalid, do not change its contents!", "danger")
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"Token for %s had a exception during validation: Error - %s %s", emails, e)
        return redirect(url_for('home'))


# New
@app.route('/reset_password', methods=["GET", "POST"])
@limiter.limit('5 per day')  # JXADDED
def reset_password():
    global formemail
    form = ResetPasswordForm(request.form)
    if request.method == "POST" and form.validate():
        db = shelve.open("storage.db")
        user_db = db["Users"]
        for nric, user in user_db.items():
            if form.Email.data == user.get_email():
                formdict = form.Email.data
                token = generate_confirmation_token(formdict)
                formemail = token
                msg = Message(subject="Password reset", recipients=[form.Email.data],
                              body="Link to reset password : {}{}." \
                              .format(request.url_root, url_for("confirm_reset", token=token)),
                              sender="flaskapptest123@gmail.com")
                mail.send(msg)
                session["email"] = form.Email.data

                break
        db.close()

        flash("Successfully entered email, if you have registered an account with us, a reset password email would"
              " be sent to your email", "success")

        return redirect(url_for("home"))

    return render_template("Login/reset_password.html", form=form)


# New
@app.route('/confirm_reset/<token>', methods=["GET", "POST"])
def confirm_reset(token):
    form = ChangePasswordForm(request.form)
    if request.method == "POST" and form.validate():
        user = Users.query.filter_by(email=session['email']).first()
        saltysalt = bcrypt.gensalt()
        form.Password.data = bcrypt.hashpw(form.Password.data.encode(encoding='UTF-8'), saltysalt)
        user.password = form.Password.data
        expiry_time = timedelta(days=90)
        current_date = datetime.today()
        expire_date = (current_date + expiry_time).date()
        user.password_expiry_date = expire_date
        db.session.commit()
        flash("Successfully reset password,please relogin", "success")
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.info(f"User %s (email: %s) has successfully reset their password", username,
                    session["reset_email"])
        del session["reset_email"]
        session.clear()
        return redirect(url_for("login"))

    else:
        email = confirm_token(token)
        if email:
            session["reset_email"] = email
            return render_template("Login/new_password.html", token=token, form=form)
        else:
            flash("Token Invalid, please try again", "danger")
            return redirect(url_for('home'))
# End of METHOD 1 (INSECURE DESERIALIZATION)


# # Helper functions to reset email (METHOD 2) (INSECURE DESERIALIZATION)
# def generate_confirmation_token(email):
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     return serializer.dumps(email, salt=app.config['SECRET_KEY'])
#
#
# def confirm_token(token, expiration=300):
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     try:
#         email = serializer.loads(
#             token,
#             salt=app.config['SECRET_KEY'],
#             max_age=expiration
#         )
#     except:
#         return False
#     return email
#
#
# @app.route('/reset_password', methods=["GET", "POST"])
# def reset_password():
#     form = ResetPasswordForm(request.form)
#     if request.method == "POST" and form.validate():
#         db = shelve.open("storage.db")
#         user_db = db["Users"]
#         for nric, user in user_db.items():
#             if form.Email.data == user.get_email():
#                 token = generate_confirmation_token(form.Email.data)
#                 msg = Message(subject="Password reset", recipients=[form.Email.data],
#                               body="Link to reset password : {}{}. Link valid for only 5 minutes" \
#                               .format(request.url_root, url_for("confirm_reset", token=token)),
#                               sender="nypflask123@gmail.com")
#                 mail.send(msg)
#                 break
#         db.close()
#
#         flash("Successfully entered email, if you have registered an account with us, a reset password email would"
#               " be sent to your email", "success")
#
#         return redirect(url_for("home"))
#
#     return render_template("Login/reset_password.html", form=form)
#
#
# @app.route('/confirm_reset/<token>', methods=["GET", "POST"])
# def confirm_reset(token):
#     form = ChangePasswordForm(request.form)
#     if request.method == "POST" and form.validate():
#         user = Users.query.filter_by(email=session['email']).first()
#         saltysalt = bcrypt.gensalt()
#         form.Password.data = bcrypt.hashpw(form.Password.data.encode(encoding='UTF-8'), saltysalt)
#         user.password = form.Password.data
#         expiry_time = timedelta(days=90)
#         current_date = datetime.today()
#         expire_date = (current_date + expiry_time).date()
#         user.password_expiry_date = expire_date
#         db.session.commit()
#         flash("Successfully reset password,please relogin", "success")
#     else:
#         email = confirm_token(token)
#         if email:
#             session["reset_email"] = email
#             return render_template("Login/new_password.html", token=token, form=form)
#         else:
#             flash("Token expired, please try again", "danger")
#             return redirect(url_for('home'))
# End of METHOD 2 (INSECURE DESERIALIZATION)


# Admin access
@app.route('/all_users')
def admin_all_users():
    try:
        if is_admin():
            all_users = []
            db = shelve.open('storage.db')
            user_db = db["Users"]
            for user in user_db.values():
                if user.get_NRIC() != session["user-NRIC"]:
                    all_users.append(user)

            # New
            username = session["user-NRIC"]
            role = session['user-role']
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.info(f"%s %s has accessed the -all users- admin functionality update page", role, username)

            return render_template("Admin/all_users.html", all_users=all_users)

        else:  # New

            # New
            username = session["user-NRIC"]
            role = session['user-role']
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(f"%s %s attempted to access the -all users- admin functionality update page", role, username)
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the -all users- admin functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/admin_update/<uid>', methods=["GET", "POST"])
def admin_update(uid):
    try:
        if is_admin():
            form = AdminUpdateForm(request.form)
            db = shelve.open("storage.db", flag="w", writeback=True)
            user_db = db["Users"]
            user = user_db[uid]

            if request.method == "POST" and form.validate():
                user.set_email(form.Email.data)
                user.set_password(form.Password.data)
                user.set_url(form.URL.data)
                appointment_dict = db['Appointments']
                for appts in appointment_dict:
                    print(appointment_dict[appts])
                    if appointment_dict[appts].get_doctor() == user.get_first_name() + " " + user.get_last_name():
                        appointment_dict[appts].set_url(user.get_url())

                # New
                username = session["user-NRIC"]
                role = session['user-role']
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.info(
                    f"%s %s has used -admin update- admin functionality to update the information of account %s ",
                    role, username, user.get_NRIC())

                flash("Successfully updated", "success")
                return redirect(url_for("admin_all_users"))

            db.close()

            return render_template("Admin/admin_update.html", user=user, form=form)

        else:
            flash("Access denied", "danger")

            # New
            username = session["user-NRIC"]
            role = session['user-role']
            db = shelve.open("storage.db")
            user_db = db["Users"]
            user = user_db[uid]
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(
                f"%s %s tried to use the -admin update- admin functionality to update the information of account %s ",
                role, username, user.get_NRIC())

            return redirect(url_for("home"))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the -admin update- admin functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/admin_delete/<uid>', methods=["GET"])
def admin_delete(uid):
    try:
        if is_admin():
            db = shelve.open('storage.db')
            user_db = db["Users"]
            del user_db[uid]
            db['Users'] = user_db
            db.close()

            # New
            username = session["user-NRIC"]
            role = session['user-role']
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.info(f"%s %s has used the -admin delete- admin functionality to delete account %s ", role, username, uid)

            flash("Successfully deleted user", "success")

            return redirect(url_for('admin_all_users'))
        else:
            flash("Access denied", "danger")

            # New
            username = session["user-NRIC"]
            role = session['user-role']
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(f"%s %s tried to use the -admin delete- admin functionality to delete account %s ", role, username,
                         uid)

            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the -admin delete- admin functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


# New
@app.route("/log_monitoring")
def log_monitoring():
    try:
        if is_admin():
            try:
                def reader(filename):
                    with open(filename) as f:
                        log = f.read()
                        regexp = r'[:]\s[A-Z]\d{7}[A-Z]'
                        NRIC = re.findall(regexp, log)
                        return NRIC

                def count(NRIC):
                    return Counter(NRIC)

                def write_csv(counter):
                    with open('PharmacyFrequencyMonitoring.csv', 'w') as csvfile:
                        writer = csv.writer(csvfile)

                        header = ['USERNAME (NRIC) ', ' FREQUENCY']

                        writer.writerow(header)

                        for item in counter:
                            writer.writerow((item, counter[item]))

                data = pd.read_csv('PharmacyFrequencyMonitoring.csv')
                df = pd.DataFrame(data)
                X = list(df.iloc[:, 0])
                Y = list(df.iloc[:, 1])

                fig, ax = plt.subplots()
                labels = ax.get_xticklabels()
                plt.setp(labels, horizontalalignment='right')

                plt.barh(X, Y, color='c')
                plt.title("Frequency of logged users")
                plt.xlabel("Usernames")
                plt.ylabel("Frequency")

                write_csv(count(reader('Pharmacy.log')))
                plt.show()

                # New
                username = session["user-NRIC"]
                role = session['user-role']
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.info(f"%s %s has used the -Log Monitoring- admin functionality", role, username)

                return redirect(url_for('home'))
            except Exception as e:
                # New
                username = session["user-NRIC"]
                role = session['user-role']
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.warning(
                    f"%s %s has had an unexpected exception in -Log Monitoring- admin functionality: RuntimeError: main thread is not in main loop",
                    role, username)

                return redirect(url_for('home'))

        else:
            flash("Access denied", "danger")

            # New
            username = session["user-NRIC"]
            role = session['user-role']
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(f"%s %s tried to use the -Log Monitoring- admin functionality", role, username)

            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(
            f"User with IP address %s tried to use the -Log Monitoring- admin functionality without logging in",
            ipaddress)
        return redirect(url_for('login'))


@app.route('/add_doctor', methods=["GET", "POST"])
def add_doctor():
    try:
        if is_admin():
            form = RegisterForm(request.form)
            if request.method == "POST" and form.validate():
                db = shelve.open('storage.db', 'c')
                users_dict = db['Users']

                if form.NRIC.data in users_dict:
                    flash("This NRIC is already in used.You can login to access our service.", "danger")
                    return redirect(url_for('admin_all_users'))
                else:
                    user = Users.Doctor(form.NRIC.data, form.FirstName.data, form.LastName.data, form.Gender.data,
                                        form.Dob.data,
                                        form.Email.data, form.Password.data, form.specialization.data, form.URL.data)
                    user.set_role("Doctor")
                    users_dict[user.get_NRIC()] = user
                    db['Users'] = users_dict
                    flash(f'Account created for {form.FirstName.data} {form.LastName.data}!', 'success')
                    return redirect(url_for('admin_all_users'))
            return render_template("Admin/add_doctor.html", form=form)
        else:
            flash("Access denied", "danger")

            # New
            username = session["user-NRIC"]
            role = session['user-role']
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(f"%s %s tried to use the -add doctor- admin functionality", role, username)

            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the -add doctor- admin functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route("/show_pyecharts1")
def showechart1():
    try:
        if is_admin():
            db = shelve.open('storage.db', 'c')
            users_dict = db['Users']
            user_list = []
            user_count = {'Patients': 0, "Doctors": 0}
            xdata = []
            ydata = []
            for key in users_dict:
                user = users_dict.get(key)
                user_list.append(user)
            for users in user_list:
                if users.get_role() == "Patient":
                    user_count["Patients"] += 1
                elif users.get_role() == "Doctor":
                    print(user_count["Doctors"])
                    user_count["Doctors"] += 1

            for key in user_count:
                xdata.append(key)
                ydata.append(user_count[key])
            print(xdata)
            print(ydata)
            usernumber(xdata, ydata)
            return render_template("Admin/admin_dashboard.html")
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the showchart1 functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


# AppointmentSystem
@app.route('/appointment_list')
def appointment():
    try:
        today = datetime.today().date()
        expire_date = session['user-pwd-expiry']
        expire_date = datetime.strptime(expire_date, '%Y-%m-%d').date()
        expire_time = (expire_date - today).days
        if expire_time <= 0:
            flash(f'Your password has expired,please change to continue!','danger')
            return redirect(url_for('change_password'))
        db = shelve.open('storage.db', 'c')
        appointment_dict = db['Appointments']
        appointment_list = []
        year_month = []
        period = {}
        for key in appointment_dict:
            appointment = appointment_dict.get(key)
            if appointment.get_patient() == session['user'] or appointment.get_doctor() == session['user'] or session[
                'user-role'] == 'Admin':
                appointment_list.append(appointment)
        for appt in appointment_list:
            date = appt.get_date()
            time = appt.get_time()
            appt_date = validate_history(date, time)
            if appt_date:
                appointment_list.remove(appt)
        appointment_list.sort(key=lambda x: x.get_datetime())
        for i in range(len(appointment_list)):
            date = appointment_list[i].get_date()
            appt_date = date.strftime("%Y-%m-%d")
            month = appt_date.split("-")[1]
            year = appt_date.split("-")[0]
            ym = year + "-" + month
            if ym not in year_month:
                year_month.append(ym)
        for i in range(len(year_month)):
            current_month = []
            for appt in appointment_list:
                date = appt.get_date()
                appt_date = date.strftime("%Y-%m-%d")
                month = appt_date.split("-")[1]
                year = appt_date.split("-")[0]
                ym = year + "-" + month
                if ym == year_month[i]:
                    current_month.append(appt)
            period[year_month[i]] = current_month
        return render_template('Appointment/appointment_list.html', period=period, number=len(appointment_list))
    except KeyError:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the appointment list functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/appointment_history')
def appointment_hist():
    try:
        db = shelve.open('storage.db', 'c')
        appointment_dict = db['Appointments']
        appointment_list = []
        appointment_hist = []
        for key in appointment_dict:
            appointment = appointment_dict.get(key)
            if appointment.get_patient() == session['user'] or appointment.get_doctor() == session['user'] or session[
                'user-role'] == 'Admin':
                appointment_list.append(appointment)
        for appt in appointment_list:
            date = appt.get_date()
            time = appt.get_time()
            appt_date = validate_history(date, time)
            if appt_date:
                appointment_hist.append(appt)
        appointment_len = len(appointment_hist)
        return render_template('Appointment/appointment_hist.html', appointment_list=appointment_hist,
                               appointment_len=appointment_len)
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the appointment history functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/appointment_summary')
def appointment_summary():
    try:
        if is_admin():
            global current_month
            db = shelve.open('storage.db', 'c')
            appointment_dict = db['Appointments']
            appointment_list = []
            year_month = []
            period = {}
            for key in appointment_dict:
                appointment = appointment_dict.get(key)
                if appointment.get_patient() == session['user'] or appointment.get_doctor() == session['user'] or \
                        session[
                            'user-role'] == 'Admin':
                    appointment_list.append(appointment)
            appointment_list.sort(key=lambda x: x.get_datetime(), reverse=True)
            for i in range(len(appointment_list)):
                date = appointment_list[i].get_date()
                appt_date = date.strftime("%Y-%m-%d")
                month = appt_date.split("-")[1]
                year = appt_date.split("-")[0]
                ym = year + "-" + month
                if ym not in year_month:
                    year_month.append(ym)
            for i in range(len(year_month)):
                current_month = []
                for appt in appointment_list:
                    date = appt.get_date()
                    appt_date = date.strftime("%Y-%m-%d")
                    month = appt_date.split("-")[1]
                    year = appt_date.split("-")[0]
                    ym = year + "-" + month
                    if ym == year_month[i]:
                        current_month.append(appt)
                period[year_month[i]] = len(current_month)

            return render_template('Appointment/appointment_summary.html', period=period)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Appointment Summary functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route("/show_pyecharts")
def showechart():
    try:
        if is_admin():
            db = shelve.open('storage.db', 'c')
            appointment_dict = db['Appointments']
            appointment_list = []
            time_visitor = {'8AM': 0, "10AM": 0, "12PM": 0, "2PM": 0, "4PM": 0, "6PM": 0, "8PM": 0, "10PM": 0}
            xdata = []
            ydata = []
            for key in appointment_dict:
                appointment = appointment_dict.get(key)
                appointment_list.append(appointment)
            for appt in appointment_list:
                time = appt.get_time()
                if time == "8:00:00":
                    time_visitor['8AM'] += 1
                elif time == "10:00:00":
                    time_visitor['10AM'] += 1
                elif time == "12:00:00":
                    time_visitor['12PM'] += 1
                elif time == "14:00:00":
                    time_visitor['2PM'] += 1
                elif time == "16:00:00":
                    time_visitor['4PM'] += 1
                elif time == "18:00:00":
                    time_visitor['6PM'] += 1
                elif time == "20:00:00":
                    time_visitor['8PM'] += 1
                elif time == "22:00:00":
                    time_visitor['10PM'] += 1
            for key in time_visitor:
                xdata.append(key)
                ydata.append(time_visitor[key])
            print(xdata)
            print(ydata)
            bargraph(xdata, ydata)
            return render_template("Appointment/charts.html")
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the show pyecharts functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/appointment', methods=['GET', 'POST'])
def add_appointment():
    try:
        if session['user'] != None:
            global users_dict
            form = AppointmentForm(request.form)
            if request.method == "POST" and form.validate():
                db = shelve.open('storage.db', 'c')
                appointment_dict = db['Appointments']
                users_dict = db['Users']
                appdate = validate_date(form.Date.data, form.Time.data)
                appt = appointments.Appointment(form.Date.data, form.Time.data, form.Department.data, form.Type.data)
                appt.set_patient(session['user'])
                repeated = validate_repeated(appointment_dict, appt, session['user'])
                if appdate:
                    flash("Invalid Date or Time!", 'danger')
                elif repeated:
                    flash("You can only have 1 appointment at 1 timing!", 'danger')
                else:
                    assignDoctor(appt)
                    appt.set_id(id(appt))
                    appointment_dict[appt.get_id()] = appt
                    db['Appointments'] = appointment_dict
                    flash("Appointment has been booked!View it in appointment list!", 'success')
                    return redirect(url_for('home'))
            return render_template('Appointment/appointment.html', form=form)
    except:
        #New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Add Appointment functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/docappointment', methods=['GET', 'POST'])
def doc_add_appointment():
    try:
        if session["user-role"] == "Doctor":
            form = DocAppointmentForm(request.form)
            db = shelve.open('storage.db', 'c')
            appointment_dict = db['Appointments']
            user_dict = db["Users"]
            form.Department.data = user_dict[session['user-NRIC']].get_specialization()
            if request.method == "POST" and form.validate():
                appdate = validate_date(form.Date.data, form.Time.data)
                appt = appointments.Appointment(form.Date.data, form.Time.data, form.Department.data, form.Type.data)
                appt.set_patient(form.Patient.data)
                appt.set_doctor(session['user'])
                repeated = validate_repeated(appointment_dict, appt, form.Patient.data)
                if appdate:
                    flash("Invalid Date or Time!", 'danger')
                elif repeated:
                    flash("You can only have 1 appointment at 1 timing!", 'danger')
                else:
                    appt.set_id(id(appt))
                    appointment_dict[appt.get_id()] = appt
                    db['Appointments'] = appointment_dict
                    flash("Appointment has been booked!View it in appointment list!", 'success')
                    return redirect(url_for('home'))
            return render_template('Appointment/docappointment.html', form=form)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(
            f"User with IP address %s tried to use the add doctor appointment functionality without logging in",
            ipaddress)
        return redirect(url_for('login'))


@app.route('/Updateappointment/<id>', methods=['GET', 'POST'])
def update_appointment(id):
    try:
        if session['user'] != None:
            db = shelve.open('storage.db', 'c')
            appointment_dict = db['Appointments']
            appt = appointment_dict[int(id)]
            if session['user'] == appt.get_patient() or session['user-role'] == 'Admin' or session['user'] == appt.get_doctor():
                form = AppointmentForm(request.form)
                if request.method == "POST" and form.validate():
                    newappt = appointments.Appointment(form.Date.data, form.Time.data, form.Department.data,
                                                       form.Type.data)
                else:
                    db = shelve.open('storage.db', 'r')
                    appointment_dict = db['Appointments']
                    db.close()
                    appt = appointment_dict[int(id)]
                    form.Date.data = appt.get_date()
                    form.Time.data = appt.get_time()
                    form.Type.data = appt.get_venue()
                    form.Department.data = appt.get_department()

                    return render_template('Appointment/updateAppointment.html', form=form)
            else:
                flash('Access denied', 'danger')
                return redirect(url_for('home'))
            appdate = validate_date(form.Date.data, form.Time.data)
            repeated = validate_repeated(appointment_dict, newappt, session['user'])
            if appdate:
                flash("Invalid Date!", 'danger')
            elif repeated:
                flash("You can only have 1 appointment at 1 timing!", 'danger')
            else:
                assignDoctor(appt)
                appt.set_date(form.Date.data)
                appt.set_time(form.Time.data)
                appt.set_department(form.Department.data)
                appt.set_venue(form.Type.data)
                appointment_dict[appt.get_id()] = appt

                db['Appointments'] = appointment_dict
                flash("Appointment has been changed!View it in appointment list!", 'success')
                return redirect(url_for('home'))
            return redirect(url_for('update_appointment', id=id))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the update appointment functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/deleteAppointment/<id>', methods=['POST'])
def delete_appointment(id):
    db = shelve.open('storage.db', 'w')
    appointment_dict = db['Appointments']
    appointment_dict.pop(int(id))
    db['Appointments'] = appointment_dict
    flash("Appointment has been deleted", 'danger')
    db.close()
    return redirect(url_for('appointment'))


def validate_date(date, time):
    date = date.strftime("%Y-%m-%d")
    appt_time = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    if now > appt_time:
        return True


def validate_history(date, time):
    date2 = date.strftime("%Y-%m-%d")
    now = datetime.now()
    dt = date2 + " " + time
    appt_time = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    if now > appt_time:
        return True


def validate_repeated(appointment_dict, appt, user):
    for key in appointment_dict:
        if appointment_dict[key].get_patient() == user and appt.get_date() == appointment_dict[
            key].get_date() and appt.get_time() == appointment_dict[key].get_time():
            return True


def assignDoctor(appointment):
    doc_list = []
    appointment_no = 0
    db = shelve.open('storage.db', 'c')
    user_dict = db['Users']
    appointment_dict = db['Appointments']
    for key in user_dict:
        if user_dict[key].get_role() == 'Doctor' and appointment.get_department() == user_dict[
            key].get_specialization():
            doc_list.append(user_dict[key])
    for doctor in doc_list:
        for appts in appointment_dict:
            if appointment_dict[appts].get_doctor() == doctor.get_first_name() + " " + doctor.get_last_name():
                appointment_no += 1
            if appointment_no <= 3:
                appointment.set_doctor(f'{doctor.get_first_name()} {doctor.get_last_name()}')
                appointment.set_url(doctor.get_url())
                break


# Contact Us
@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    form = ContactForm()
    if form.validate_on_submit():
        flash(
            f'You have successfully submitted the form. Please wait 2-3 working days for reply and also check your email.Thank you.',
            'success')
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        enquiries = request.form['enquiries']
        msg = Message(subject,
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[email],
                      body="Hi " + name + ',\n\n Thanks a lot for getting in touch with us. \n \n This is an automatic email just to let you know that we have received your enquiries.\n\n'
                                          'This is the message that you sent.\n' + enquiries)
        mail.send(msg)
        return redirect(url_for('contactus'))
    return render_template('FAQ/contactus.html', title='Contact Us', form=form)


# review
@app.route('/review', methods=['GET', 'POST'])
def new_review():
    if session['user'] is not None:
        form = PostReview(request.form)
        if request.method == 'POST' and form.validate():
            review_dict = {}
            db = shelve.open('storage.db', 'c')
            try:
                review_dict = db['Reviews']
            except:
                # New
                username = session["user-NRIC"]
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.error(f"Error retrieving reviews from storage.db")
                print('Error in retrieving reviews from storage.db')

            reviews = review.Reviews(form.title.data, form.content.data, form.date.data, session['user'])
            reviews.set_review_id(id(reviews))
            review_dict[reviews.get_review_id()] = reviews
            db['Reviews'] = review_dict

            db.close()

            flash('Your review has been created!', 'success')
            return redirect(url_for('new_review'))
        return render_template('review/addReview.html', title='New review', form=form)
    else:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the new review functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/retrieveReview')
def retrieve_review():
    review_dict = {}
    db = shelve.open('storage.db', 'r')
    review_dict = db['Reviews']
    db.close()

    review_list = []
    for key in review_dict:
        rev = review_dict.get(key)
        review_list.append(rev)
    return render_template('review/retrieveReview.html', count=len(review_list), review_list=review_list)


@app.route('/updateReview/<id>', methods=['GET', 'POST'])
def update_review(id):
    try:
        if is_admin():
            form = PostReview(request.form)
            if request.method == 'POST' and form.validate():
                db = shelve.open('storage.db', 'w')
                review_dict = db['Reviews']

                review = review_dict.get(int(id))
                review.set_title(form.title.data)
                review.set_content(form.content.data)
                review.set_date(form.date.data)

                db['Reviews'] = review_dict
                db.close()

                return redirect(url_for('retrieve_review'))
            else:
                db = shelve.open('storage.db', 'r')
                review_dict = db['Reviews']
                db.close()

                review = review_dict.get(int(id))
                form.title.data = review.get_title()
                form.content.data = review.get_content()
                form.date.data = review.get_date()

                return render_template('Review/updateReview.html', form=form)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the update review functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/deleteReview/<id>', methods=['POST'])
def delete_review(id):
    review_dict = {}
    db = shelve.open('storage.db', 'w')
    review_dict = db['Reviews']
    review_dict.pop(int(id))
    db['Reviews'] = review_dict
    db.close()

    return redirect(url_for('retrieve_review'))


# FAQ
@app.route('/faq', methods=['GET', 'POST'])
def create_faq():
    try:
        if is_admin():
            create_faq_form = FAQ_form(request.form)
            if request.method == 'POST' and create_faq_form.validate():
                qn_dict = {}
                db = shelve.open('storage.db', 'c')
                try:
                    qn_dict = db['FAQ']
                except:
                    # New
                    username = session["user-NRIC"]
                    ipaddress = get('https://api.ipify.org').text
                    f = customFilter(username, ipaddress)
                    logger.addFilter(f)
                    logger.error(f"Error retrieving Questions from storage.db")
                    print("Error in retrieving Questions from storage.db.")

                question = FAQ(create_faq_form.question.data, create_faq_form.answer.data,
                                   create_faq_form.date.data)
                question.set_qns_id(id(question))
                qn_dict[question.get_qns_id()] = question
                db['FAQ'] = qn_dict

                db.close()

                return redirect(url_for('create_faq'))
            return render_template('FAQ/faq.html', form=create_faq_form)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the create faq functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


# New
@app.route('/retrieveQns', methods=['GET', 'POST'])
def retrieve_qns():
    search = SearchBar(request.form)
    if request.method == 'POST' and search.validate():
        qns_list = []
        sql = f"Select * from FA_Qs where question like '%{search.search.data}%'"
        questions = db.engine.execute(sql)
        for i in questions:
            item = FAQ(i.id, i.question, i.answer, i.date)
            qns_list.append(item)
        return render_template('FAQ/retrieveQns.html', count=len(qns_list), qn_list=qns_list, form=search)

    qn_list = []
    questions = FAQs.query.all()
    for i in questions:
        item = FAQ(i.id, i.question, i.answer, i.date)
        qn_list.append(item)
    return render_template('FAQ/retrieveQns.html', count=len(qn_list), qn_list=qn_list, form=search)


@app.route('/updateQns/<int:id>/', methods=['GET', 'POST'])
def update_qns(id):
    try:
        if is_admin():
            update_faq_form = FAQ(request.form)
            if request.method == 'POST' and update_faq_form.validate():
                db = shelve.open('storage.db', 'w')
                qn_dict = db['FAQ']

                question = qn_dict.get(int(id))
                question.set_question(update_faq_form.question.data)
                question.set_answer(update_faq_form.answer.data)
                question.set_date(update_faq_form.date.data)

                db['FAQ'] = qn_dict
                db.close()

                return redirect(url_for('retrieve_qns'))
            else:
                db = shelve.open('storage.db', 'r')
                qn_dict = db['FAQ']
                db.close()

                question = qn_dict.get(int(id))
                update_faq_form.question.data = question.get_question()
                update_faq_form.answer.data = question.get_answer()
                update_faq_form.date.data = question.get_date()

                return render_template('FAQ/updateQns.html', form=update_faq_form)
        flash("Access denied", "danger")
        return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the update questions functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/deleteQns/<int:id>', methods=['POST'])
def delete_qns(id):
    qn_dict = {}
    db = shelve.open('storage.db', 'w')
    qn_dict = db['FAQ']

    qn_dict.pop(int(id))

    db['FAQ'] = qn_dict
    db.close()

    return redirect(url_for('retrieve_qns'))


@app.route("/monthlyQn")
def monthly_qn():
    try:
        if session["user-role"] == "Admin":
            db = shelve.open('storage.db', 'c')
            faq_dict = db['FAQ']
            faq_list = []
            month_qn = {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0, "June": 0, "July": 0,
                        "August": 0,
                        "September": 0, "October": 0, "November": 0, "December": 0}
            xdata = []
            ydata = []
            for key in faq_dict:
                faq = faq_dict.get(key)
                faq_list.append(faq)
            for qn in faq_list:
                month = qn.get_date()
                month = month.strftime("%Y-%m-%d")
                if month == "2021-01-01":
                    month_qn['January'] += 1
                elif month == "2021-02-01":
                    month_qn['February'] += 1
                elif month == "2021-03-01":
                    month_qn['March'] += 1
                elif month == "2021-04-01":
                    month_qn['April'] += 1
                elif month == "2021-05-01":
                    month_qn['May'] += 1
                elif month == "2021-06-01":
                    month_qn['June'] += 1
                elif month == "2021-07-01":
                    month_qn['July'] += 1
                elif month == "2021-08-01":
                    month_qn['August'] += 1
                elif month == "2021-09-01":
                    month_qn['September'] += 1
                elif month == "2021-10-01":
                    month_qn['October'] += 1
                elif month == "2021-11-01":
                    month_qn['November'] += 1
                elif month == "2021-12-01":
                    month_qn['December'] += 1

            for key in month_qn:
                xdata.append(key)
                ydata.append(month_qn[key])

            print(xdata)
            print(ydata)
            monthlyQnbargraph(xdata, ydata)
            return render_template("FAQ/monthlyQn.html")
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the Monthly Questions functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


# Application Form
@app.route('/createApplicant', methods=['GET', 'POST'])
def create_applicant():
    create_applicant_form = CreateApplicationForm(request.form)

    if request.method == 'POST' and create_applicant_form.validate():
        applicants_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            applicants_dict = db['Applicant']
        except:
            # New
            username = session["user-NRIC"]
            ipaddress = get('https://api.ipify.org').text
            f = customFilter(username, ipaddress)
            logger.addFilter(f)
            logger.error(f"Error retrieving Applicants from storage.db")
            print("Error in retrieving Applicants from storage.db.")

        # parsing parameters into Application Class in Application.py
        applicant = Applicant.Applicant(create_applicant_form.fname.data, create_applicant_form.lname.data,
                                        create_applicant_form.nric.data,
                                        create_applicant_form.email.data, create_applicant_form.age.data,
                                        create_applicant_form.address.data, create_applicant_form.gender.data,
                                        create_applicant_form.nationality.data, create_applicant_form.language.data,
                                        create_applicant_form.phoneno.data, create_applicant_form.quali.data,
                                        create_applicant_form.industry.data,
                                        create_applicant_form.comp1.data,
                                        create_applicant_form.posi1.data, create_applicant_form.comp2.data,
                                        create_applicant_form.posi2.data, create_applicant_form.empty1.data,
                                        create_applicant_form.empty2.data)
        applicant.set_applicantid(id(applicant))
        applicants_dict[applicant.get_applicantid()] = applicant

        db['Applicant'] = applicants_dict

        # Automatically Send Email Codes
        sender_email = "nypflask123@gmail.com"
        password = "NYPflask123"
        rec_email = create_applicant_form.email.data
        subject = "Application for NYP Polyclinic"
        body = "Hello, we have received your application. Please wait for a few days for us to update you about the status. Thank you."
        message = "Subject: {}\n\n{}".format(subject, body)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        print("Login Success")
        server.sendmail(sender_email, rec_email, message)
        print("Email has been sent to ", rec_email)
        # Automatically Send Email Codes

        db.close()

        session['applicant_created'] = applicant.get_first_name() + ' ' + applicant.get_last_name()
        return redirect(url_for('create_applicant'))
    return render_template('ApplicationForm/applicationForm.html', form=create_applicant_form)


@app.route('/retrieveApplicants')
def retrieve_applicants():
    try:
        if is_admin():
            db = shelve.open('storage.db', 'r')
            applicants_dict = db['Applicant']
            db.close()

            applicants_list = []

            for key in applicants_dict:
                applicants = applicants_dict.get(key)
                applicants_list.append(applicants)

            return render_template('ApplicationForm/retrieveApplicants.html', count=len(applicants_list),
                                   applicants_list=applicants_list)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the retrieve applications functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/updateApplicants/<int:id>/', methods=['GET', 'POST'])
def update_applicants(id):
    try:
        if is_admin():
            update_applicant_form = CreateApplicationForm(request.form)
            if request.method == 'POST' and update_applicant_form.validate():

                db = shelve.open('storage.db', 'w')
                applicants_dict = db['Applicant']

                # after submit, setting the updated inputs.
                # problem now is that updated employment does not display
                applicant = applicants_dict.get(int(id))
                applicant.set_first_name(update_applicant_form.fname.data)
                applicant.set_last_name(update_applicant_form.lname.data)
                applicant.set_NRIC(update_applicant_form.nric.data)
                applicant.set_email(update_applicant_form.email.data)
                applicant.set_age(update_applicant_form.age.data)
                applicant.set_address(update_applicant_form.address.data)
                applicant.set_gender(update_applicant_form.gender.data)
                applicant.set_nationality(update_applicant_form.nationality.data)
                applicant.set_language(update_applicant_form.language.data)
                applicant.set_phonenumber(update_applicant_form.phoneno.data)
                applicant.set_qualification(update_applicant_form.quali.data)
                applicant.set_industry(update_applicant_form.industry.data)
                applicant.set_company1(update_applicant_form.comp1.data)
                applicant.set_postion1(update_applicant_form.posi1.data)
                applicant.set_company2(update_applicant_form.comp2.data)
                applicant.set_postion2(update_applicant_form.posi2.data)
                db['Applicant'] = applicants_dict

                # Automatically Send Email Codes
                sender_email = "nypflask123@gmail.com"
                password = "NYPflask123"
                rec_email = applicant.get_email()
                subject = "Application for NYP Polyclinic"
                body = "Hello, we have your updated application. Please wait for a few days for us to update you about the status. Thank you."
                message = "Subject: {}\n\n{}".format(subject, body)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, password)
                print("Login Success")
                server.sendmail(sender_email, rec_email, message)
                print("Email has been sent to ", rec_email)
                # Automatically Send Email Codes

                db.close()

                session['applicant_updated'] = applicant.get_first_name() + ' ' + applicant.get_last_name()

                return redirect(url_for('home'))

            else:

                db = shelve.open('storage.db', 'r')
                applicants_dict = db['Applicant']
                db.close()

                # get data input and place in in the field
                applicant = applicants_dict.get(int(id))
                update_applicant_form.fname.data = applicant.get_first_name()
                update_applicant_form.lname.data = applicant.get_last_name()
                update_applicant_form.nric.data = applicant.get_NRIC()
                update_applicant_form.email.data = applicant.get_email()
                update_applicant_form.age.data = applicant.get_age()
                update_applicant_form.address.data = applicant.get_address()
                update_applicant_form.gender.data = applicant.get_gender()
                update_applicant_form.nationality.data = applicant.get_nationality()
                update_applicant_form.language.data = applicant.get_language()
                update_applicant_form.phoneno.data = applicant.get_phonenumber()
                update_applicant_form.quali.data = applicant.get_qualification()
                update_applicant_form.industry.data = applicant.get_industry()
                update_applicant_form.comp1.data = applicant.get_company1()
                update_applicant_form.posi1.data = applicant.get_position1()
                update_applicant_form.comp2.data = applicant.get_company2()
                update_applicant_form.posi2.data = applicant.get_position2()

                return render_template('ApplicationForm/updateApplicant.html', form=update_applicant_form)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the update applicants functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/sendApplicants/<int:id>/', methods=['GET', 'POST'])
def send_applicant(id):
    try:
        if is_admin():
            resend_form = ResendForm(request.form)
            contents = "Hello, Please Resend Your Application Form as there is a certain problem with your inputs. The following inputs with problem are, "
            if request.method == 'POST' and resend_form.validate():
                db = shelve.open('storage.db', 'r')
                applicants_dict = db['Applicant']
                applicant = applicants_dict.get(int(id))

                resend = Resend.Resend(resend_form.nric.data, resend_form.email.data, resend_form.age.data,
                                       resend_form.gender.data, resend_form.nationality.data, resend_form.language.data,
                                       resend_form.phoneno.data, resend_form.quali.data, resend_form.industry.data)

                if resend.get_nric() == "Yes":
                    contents = contents + "NRIC/FIN"
                else:
                    contents = contents

                if resend.get_email() == "Yes":
                    contents = contents + " Email"
                else:
                    contents = contents

                if resend.get_age() == "Yes":
                    contents = contents + " Age"
                else:
                    contents = contents

                if resend.get_gender() == "Yes":
                    contents = contents + " Gender"
                else:
                    contents = contents

                if resend.get_nationality() == "Yes":
                    contents = contents + " Nationality"
                else:
                    contents = contents

                if resend.get_language() == "Yes":
                    contents = contents + " Language"
                else:
                    contents = contents

                if resend.get_phoneno() == "Yes":
                    contents = contents + " Phone Number"
                else:
                    contents = contents

                if resend.get_quali() == "Yes":
                    contents = contents + " Qualification"
                else:
                    contents = contents

                if resend.get_industry() == "Yes":
                    contents = contents + " Industry"
                else:
                    contents = contents

                sender_email = "nypflask123@gmail.com"
                password = "NYPflask123"
                rec_email = applicant.get_email()
                subject = "Application for NYP Polyclinic"
                body = contents + ". Here's the link to update {}{}".format(request.url_root,
                                                                            url_for('update_applicants', id=id))
                message = "Subject: {}\n\n{}".format(subject, body)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, password)
                print("Login Success")
                server.sendmail(sender_email, rec_email, message)
                print("Email has been sent to ", rec_email)
                print(applicant)
                return redirect(url_for('retrieve_applicants'))

            return render_template('ApplicationForm/resendForm.html', form=resend_form)
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the send applicants functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/deleteApplicant/<int:id>', methods=['POST'])
def delete_applicant(id):
    db = shelve.open('storage.db', 'w')
    applicants_dict = db['Applicant']

    applicant = applicants_dict.pop(int(id))

    db['Applicant'] = applicants_dict
    db.close()
    session['applicant_deleted'] = applicant.get_first_name() + ' ' + applicant.get_last_name()
    return redirect(url_for('retrieve_applicants'))


@app.route('/showDashboard')
def show_dashboard():
    try:
        if is_admin():
            db = shelve.open('storage.db', 'c')
            applicants_dict = db['Applicant']
            applicants_list = []
            qualification_level = {"O'Levels": 0, "A'Levels": 0, "N'Levels": 0, "Diploma": 0, "Bachelor": 0,
                                   "Master": 0}
            xdata = []
            ydata = []

            for key in applicants_dict:
                applicant = applicants_dict.get(key)
                applicants_list.append(applicant)

            for people in applicants_list:
                qualification = people.get_qualification()

                if qualification == "O'Levels":
                    qualification_level["O'Levels"] += 1
                elif qualification == "A'Levels":
                    qualification_level["A'Levels"] += 1
                elif qualification == "N'Levels":
                    qualification_level["N'Levels"] += 1
                elif qualification == "Diploma":
                    qualification_level["Diploma"] += 1
                elif qualification == "Bachelor":
                    qualification_level["Bachelor"] += 1
                elif qualification == "Master":
                    qualification_level["Master"] += 1

            for key in qualification_level:
                xdata.append(key)
                ydata.append(qualification_level[key])

            print(xdata)
            print(ydata)
            applicationbargraph(xdata, ydata)
            return render_template("ApplicationForm/dashboard.html")
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the show dashboard functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/showDashboard2')
def show_dashboard2():
    try:
        if is_admin():
            db = shelve.open('storage.db', 'c')
            applicants_dict = db['Applicant']
            applicants_list = []
            regions = {"City": 0, "Central": 0, "South": 0, "East": 0, "North": 0, "West": 0}
            xdata1 = []
            ydata1 = []
            city = ['Boat Quay', 'Chinatown', 'Havelock Road', 'Marina Square', 'Raffles Place', 'Suntec City',
                    'Anson Road',
                    'Chinatown', 'Neil Road', 'Raffles Place', 'Shenton Way', 'Tanjong Pagar']
            central = ['Cairnhill', 'Killiney', 'Leonie Hill', 'Orchard', 'Oxley', 'Balmoral', 'Bukit Timah',
                       'Grange Road',
                       'Holland', 'Orchard Boulevard', 'River Valley', 'Tanglin Road', 'Chancery', 'Bukit Timah',
                       'Dunearn Road', 'Newton', 'Balestier', 'Moulmein', 'Novena', 'Toa Payoh']
            south = ['Alexandra Road', 'Tiong Bahru', 'Queenstown', 'Keppel', 'Mount Faber', 'Sentosa', 'Telok Blangah',
                     'Buona Vista', 'Dover', 'Pasir Panjang', 'West Coast']
            east = ['Potong Pasir', 'Macpherson', 'Eunos', 'Geylang', 'Kembangan', 'Paya Lebar', 'Katong',
                    'Marine Parade',
                    'Siglap', 'Tanjong Rhu', 'Bayshore', 'Bedok', 'Chai Chee', 'Changi', 'Loyang', 'Pasir Ris', 'Simei',
                    'Tampines']
            north = ['Hougang', 'Punggol', 'Sengkang', 'Ang Mo Kio', 'Bishan', 'Braddell Road', 'Thomson', 'Admiralty',
                     'Woodlands', 'Tagore', 'Yio Chu Kang', 'Sembawang', 'Yishun', 'Seletar']
            west = ['Clementi', 'Upper Bukit Timah', 'Hume Avenue', 'Boon Lay', 'Jurong', 'Tuas', 'Bukit Batok',
                    'Choa Chu Kang', 'Hillview Avenue', 'Upper Bukit Timah', 'Kranji', 'Lim Chu Kang', 'Sungei Gedong',
                    'Tengah']

            for key in applicants_dict:
                applicant = applicants_dict.get(key)
                applicants_list.append(applicant)

            for people in applicants_list:
                district = people.get_address()

                for i in city:
                    if i.lower() in district.lower():
                        regions['City'] += 1
                        break
                    else:
                        continue

                for i in central:
                    if i.lower() in district.lower():
                        regions['Central'] += 1
                        break
                    else:
                        continue

                for i in south:
                    if i.lower() in district.lower():
                        regions['South'] += 1
                        break
                    else:
                        continue

                for i in east:
                    if i.lower() in district.lower():
                        regions['East'] += 1
                        break
                    else:

                        continue

                for i in north:
                    if i.lower() in district.lower():
                        regions['North'] += 1
                        break
                    else:
                        continue

                for i in west:
                    if i.lower() in district.lower():
                        regions['West'] += 1
                        break
                    else:
                        continue

            for key in regions:
                xdata1.append(key)
                ydata1.append(regions[key])
            print(xdata1)
            print(ydata1)
            addressbargraph(xdata1, ydata1)
            return render_template("ApplicationForm/dashboard2.html")
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the show dashboards 2 functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.route('/showDashboard3')
def show_dashboard3():
    try:
        if is_admin():
            db = shelve.open('storage.db', 'c')
            applicants_dict = db['Applicant']
            applicants_list = []
            age_ranges = {"17-25": 0, "26-40": 0, "41-50": 0, "51-60": 0, "61-70": 0}
            xdata2 = []
            ydata2 = []

            for key in applicants_dict:
                applicant = applicants_dict.get(key)
                applicants_list.append(applicant)

            for people in applicants_list:
                ages = people.get_age()

                if ages <= 25:
                    age_ranges["17-25"] += 1
                elif 40 >= ages >= 26:
                    age_ranges['26-40'] += 1
                elif 50 >= ages >= 41:
                    age_ranges["41-50"] += 1
                elif 60 >= ages >= 51:
                    age_ranges["51-60"] += 1
                elif 70 >= ages >= 61:
                    age_ranges["61-70"] += 1

            for key in age_ranges:
                xdata2.append(key)
                ydata2.append(age_ranges[key])

            print(xdata2)
            print(ydata2)

            agerangebargraph(xdata2, ydata2)

            return render_template("ApplicationForm/dashboard3.html")
        else:
            flash("Access denied", "danger")
            return redirect(url_for('home'))
    except:
        # New
        username = "NIL"
        ipaddress = get('https://api.ipify.org').text
        f = customFilter(username, ipaddress)
        logger.addFilter(f)
        logger.error(f"User with IP address %s tried to use the show dashboards 3 functionality without logging in",
                     ipaddress)
        return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_handle(e):
    # New
    username = "NIL"
    ipaddress = get('https://api.ipify.org').text
    f = customFilter(username, ipaddress)
    logger.addFilter(f)
    logger.error(f"User with IP address %s has attempted to follow a broken, dead, or non-existent link: Error 404",
                 ipaddress)
    return render_template("error404.html"), 404


@app.errorhandler(429)
def frequent_request(e):
    # New
    username = "NIL"
    ipaddress = get('https://api.ipify.org').text
    f = customFilter(username, ipaddress)
    logger.addFilter(f)
    logger.error(f"User with IP address %s has went over the rate limit allowed: Error 429", ipaddress)
    return render_template('error429.html'),429

@app.after_request
def add_security_headers(resp):
    resp.headers['Content-Security-Policy'] = "script-src" \
                                              "self" \
                                              "https://code.jquery.com/jquery-3.5.1.slim.min.js" \
                                              "https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" \
                                              "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" \
                                              "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" \
                                              "https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js" \
                                              "https://cdn.datatables.net/1.10.23/js/dataTables.bootstrap4.min.js"
    return resp


class customFilter(logging.Filter):
    def __init__(self, username, ipaddress):
        self.username = username
        self.ipaddress = ipaddress

    def filter(self, record):
        record.ipaddress = self.ipaddress
        record.username = self.username
        return True


if __name__ == '__main__':
    # New
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)-15s : %(name)-8s : %(levelname)-8s : %(ipaddress)-15s : %(username)-9s - %(message)s")
    file_handler = logging.FileHandler("protected\Pharmacy.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # New
    date_backup = date.today()
    str_date_backup = str(date_backup).replace('-', '.')

    path_input = r'C:\Users\louis\PycharmProjects\AppSec(lastest)\AppSecDone\protected\Pharmacy.log' # Change to your own directory (Source Path)
    path_output = r'C:\Users\louis\PycharmProjects\AppSec(lastest)\AppSecDone\protected\Admin_LogMonitoring' + '\\' + str_date_backup + ' - Pharmacy Log Backup.log'  # Change to your own directory (Dest Path)

#    copyfile(path_input, path_output)

    app.run()  # JXADDED
