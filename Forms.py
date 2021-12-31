from wtforms import Form, StringField, TextAreaField, DecimalField, validators, IntegerField, BooleanField, SubmitField, \
    SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, Length, Email,Regexp, ValidationError
from wtforms.fields.html5 import DateField, EmailField
from flask_wtf import FlaskForm, RecaptchaField  # New
import shelve
from datetime import date
import logging  # New
import __init__  # New
from flask import request  # New
from requests import get


# New
class customFilter(logging.Filter):
    def __init__(self, username, ipaddress):
        self.username = username
        self.ipaddress = ipaddress

    def filter(self, record):
        record.ipaddress = self.ipaddress
        record.username = self.username
        return True


# New
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)-15s : %(name)-8s : %(levelname)-8s : %(ipaddress)-15s : %(username)-9s - %(message)s")
file_handler = logging.FileHandler("protected\Pharmacy.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Online Pharmacy
class CreateItemForm(Form):
    name = StringField('Name: ', [validators.Length(min=1, max=25), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')], default='')
    price = DecimalField('Price($): ', [validators.NumberRange(min=1), validators.DataRequired()], default=0, places=2)
    have = IntegerField('Amount we have in stock: ', [validators.NumberRange(min=1), validators.DataRequired()],
                        default=0)
    picture = StringField('Picture (link): ', [validators.Length(min=1, max=500), validators.DataRequired()],
                          default='')
    bio = TextAreaField('Item Description: ', [validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')], default='')
    prescription = BooleanField('Prescription', default=False)


class BuyItemForm(Form):
    want = IntegerField('Quantity: ', [validators.NumberRange(min=1), validators.DataRequired()], default=0)


class CheckoutForm(Form):
    name = StringField('Name on Card: ', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z@\s]*$',message='Invalid input')], default='')
    card_no = StringField('Card Number: ', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[0-9\s]*$',message='Invalid input')],
                          default='')
    cvn = StringField('Card Verification Number: ', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[0-9]{3}$',message='Invalid input')],
                      default='')
    exp = StringField('Expiry Date', [validators.Length(min=3, max=5), validators.DataRequired(),validators.Regexp('^[0-9\s]*$',message='Invalid input')])
    address = StringField('Address: ', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z#@0-9-\s]*$',message='Invalid input')], default='')
    # Use Sting field as Postal Code needs to be saved as string as integer removes front 0 i.e 081456 = 81456
    postal_code = StringField('Postal Code: ', [validators.Length(min=6, max=6), validators.DataRequired(),validators.Regexp('^[0-9]{6}$',message='Invalid input')], default='')


class PrescriptionForm(Form):
    quantity = IntegerField('', [validators.NumberRange(min=1), validators.DataRequired(),validators.Regexp('^[0-9\s]*$',message='Invalid input')])
    dosage_times = IntegerField('', [validators.NumberRange(min=1), validators.DataRequired()])
    dosage_interval = SelectField('', [validators.DataRequired()],
                                  choices=[('', 'Select'), ("An Hour", "An Hour"), ("A Day", "A Day")], default='')


class PrescribeForm(Form):
    patient_nric = StringField("Patient's NRIC:", [validators.DataRequired()])



# ContactUs Forms
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=150),Regexp('^[A-Za-z@\s]*$',message='Invalid input')])
    email = StringField("Email", validators=[DataRequired(), Email(),Regexp('^[A-Za-z0-9@.\s]*$',message='Invalid input')])
    subject = StringField("Subject", validators=[DataRequired(),Regexp('^[A-Za-z0-9\s]*$',message='Invalid input')])
    enquiries = TextAreaField("Enquiries ", validators=[DataRequired(),Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    submit = SubmitField("Submit")


class FAQ_form(Form):
    question = StringField('Question', [validators.Length(min=1), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    answer = TextAreaField('Answer', [validators.Length(min=1), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    date = DateField('Date', [validators.DataRequired()], format='%Y-%m-%d')

#review forms
class PostReview(Form):
    title = StringField('Title', [validators.Length(min=1), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    content = TextAreaField('Content', [validators.Length(min=1), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    date = DateField('Date',[validators.DataRequired()], format='%Y-%m-%d')


# Search Bar
class SearchBar(Form):
    search = StringField('')
    history = SelectField('', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], default=10)

    def validate_search(form, field):
        for char in field.data:
            if char not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890':
                # New
                try:
                    username = __init__.session["user-NRIC"]
                    role = __init__.session['user-role']
                except KeyError:
                    username = "NIL"
                    ipaddress = get('https://api.ipify.org').text
                    f = customFilter(username, ipaddress)
                    logger.addFilter(f)
                    logger.error(f"Guest %s used invalid input in the search bar: (Input Entered: %s)",ipaddress, field.data)
                    raise ValidationError('Invalid input! Please do not use special characters')
                else:
                    ipaddress = get('https://api.ipify.org').text
                    f = customFilter(username, ipaddress)
                    logger.addFilter(f)
                    logger.error(f"%s %s used invalid input in the search bar: (Input Entered: %s)", role, username, field.data)
                    raise ValidationError('Invalid input! Please do not use special characters')

# Applcation
class CreateApplicationForm(Form):
    fname = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z@\s]*$',message='Invalid input')])
    lname = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z@\s]*$',message='Invalid input')])
    nric = StringField('NRIC / FIN', [validators.Regexp('^[SsTtFfGg][0-9]{7}[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0-9]$', message='Invalid NRIC. e.g.S1234567A'),
                                      validators.DataRequired()])  # need to validate
    email = EmailField('Email', [validators.Length(min=1, max=150), validators.DataRequired(), validators.Email()])
    age = IntegerField('Age', [validators.number_range(min=17, max=70), validators.DataRequired()])
    address = StringField('Address', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    gender = SelectField('Gender', [validators.DataRequired()],
                         choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female')], default='')
    nationality = StringField('Nationality', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z\s]*$',message='Invalid input')])
    language = StringField('Language', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z,.\s]*$',message='Invalid input')])
    phoneno = IntegerField('Phone Number',
                           [validators.number_range(min=60000000, max=999999999,
                                                    message="Singapore's Phone Number must be 8 numbers only"),
                            validators.DataRequired()])  # need to validate
    quali = SelectField('Highest Qualification', [validators.DataRequired()],
                        choices=[('', 'Select'), ("O'Levels", "O'Levels"), ("N'Levels", "N'Levels"),
                                 ("A'Levels", "A'Levels"), ('Diploma', 'Diploma'), ('Bachelor', 'Bachelor'),
                                 ('Master', 'Master')], default='')
    industry = SelectField('Industry', [validators.DataRequired()], choices=[('', 'Select'), ("Tourism", "Toursim"), (
        "BioMedical Science", "BioMedical Science"),
                                                                             ("Logistics", "Logistics"),
                                                                             ('Banking & Finance', 'Banking & Finance'),
                                                                             ('Chemicals', 'Chemicals'),
                                                                             ('Construction', 'Construction'),
                                                                             ('Casino', 'Casino'),
                                                                             ('Healthcare', 'Healthcare'),
                                                                             ('Education', 'Education'),
                                                                             ('ICT & Media', 'ICT & Media'),
                                                                             ('Null', 'Null')], default='')
    comp1 = StringField('Company', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    posi1 = StringField('Position', [validators.Length(min=1, max=150), validators.DataRequired(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    comp2 = StringField('Company (optional)', [validators.Length(min=1, max=150), validators.optional(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    posi2 = StringField('Position (optional)', [validators.Length(min=1, max=150), validators.optional(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    empty1 = StringField('empty', [validators.Length(min=1, max=150), validators.optional(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    empty2 = StringField('empty', [validators.Length(min=1, max=150), validators.optional(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])


class ResendForm(Form):
    nric = RadioField("NRIC/FIN", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    email = RadioField("Email", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    age = RadioField("Age", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    gender = RadioField("Gender", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    nationality = RadioField("Nationality", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    language = RadioField("Language", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    phoneno = RadioField("Phone Number", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    quali = RadioField("Qualification", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    industry = RadioField("Industry", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])


# User Forms
class RegisterForm(Form):
    NRIC = StringField("NRIC", [validators.DataRequired(), Regexp('^[ST][0-9]{7}[ABCDEFGHIZJ]$', message='Invalid NRIC')])
    FirstName = StringField("First Name", [validators.DataRequired(),validators.Length(min=1, max=150),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    LastName = StringField("Last Name", [validators.DataRequired(),validators.Length(min=1, max=150),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])
    Gender = SelectField('Gender', [validators.DataRequired()],
                         choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    Dob = DateField('Date of Birth', [validators.DataRequired()])
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])
    Password = PasswordField("Password", [validators.DataRequired(),Length(min=8, max=30,message="Invalid Password Length")])
    Confirm = PasswordField("Confirm Password", [validators.DataRequired(), validators.EqualTo("Password")])
    URL = StringField("URL", [validators.optional()])
    specialization = StringField("Specialization", [validators.optional(),validators.Regexp('^[A-Za-z0-9,.?!@\s]*$',message='Invalid input')])

    def validate_Password(form, field):
        lower = False
        upper = False
        num = False
        spchar = False
        for char in field.data:
            if char in 'abcdefghijklmnopqrstuvwxyz':
                lower = True
            elif char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                upper = True
            elif char in '1234567890':
                num = True
            else:
                spchar = True
        if not (lower and upper and num and spchar):
            raise ValidationError(
                'Password should have a combination of uppercase and lower case letters,numbers and special characters.')


class OTP(Form):
    otp = StringField('OTP', [validators.DataRequired()])

class LoginForm(Form):
    NRIC = StringField("NRIC", [validators.DataRequired(), validators.Length(min=9, max=9)])
    Password = PasswordField("Password", [validators.DataRequired()])
    recaptcha = RecaptchaField()  # New
    #otp = StringField('OTP',[validators.DataRequired()])

    def validate_NRIC(form, field):
        for char in field.data:
            if char not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890':
                # New
                username = "NIL"
                ipaddress = get('https://api.ipify.org').text
                f = customFilter(username, ipaddress)
                logger.addFilter(f)
                logger.error(f"User with IP address %s used invalid input in the Login Form: (Input Entered: %s)", ipaddress, field.data)
                raise ValidationError('Invalid input!Please do not use any special characters')


class UpdateProfileForm(Form):
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])
    Dob = DateField('Date of Birth', [validators.DataRequired()])


class ChangePasswordForm(Form):
    Password = PasswordField("Password", [validators.DataRequired()])
    Confirm = PasswordField("Confirm Password", [validators.DataRequired(), validators.EqualTo("Password")])

    def validate_Password(form, field):
        lower = False
        upper = False
        num = False
        spchar = False
        for char in field.data:
            if char in 'abcdefghijklmnopqrstuvwxyz':
                lower = True
            elif char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                upper = True
            elif char in '1234567890':
                num = True
            else:
                spchar = True
        if not (lower and upper and num and spchar):
            raise ValidationError(
                'Password should have a combination of uppercase and lower case letters,numbers and special characters.')


class ResetPasswordForm(Form):
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])
    recaptcha = RecaptchaField()  # New


class AdminUpdateForm(Form):
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])
    Password = PasswordField("Password", [validators.DataRequired(),Length(min=8, max=30,message="Invalid Password Length")])
    URL = StringField("URL", [validators.optional()])


# Appointment Form
class AppointmentForm(Form):
    Department = SelectField("Department", [validators.DataRequired()],
                             choices=[('', 'Select'), ('Cardiology', 'Cardiology'),
                                      ('Gastroenterology', 'Gastroenterology'),
                                      ('Haematology', 'Haematology')])
    Date = DateField("Appointment Date", [validators.DataRequired()], format='%Y-%m-%d')
    Time = SelectField("Appointment Time", [validators.DataRequired()],
                       choices=[('', 'Select'), ('8:00:00', '8AM'), ('10:00:00', '10AM'), ('12:00:00', '12PM'),
                                ('14:00:00', '2PM'), ('16:00:00', '4PM'),
                                ('18:00:00', '6PM'), ('20:00:00', '8PM'), ('22:00:00', '10PM')], default='')
    Type = SelectField("Appointment Type", [validators.DataRequired()],
                       choices=[('', 'Select'), ('E-Doctor', 'E-Doctor'), ('Visit', 'Visit')])


db = shelve.open('storage.db', 'c')
user_dict = db["Users"]
patient_list = [('', 'Select')]
for key in user_dict:
    if user_dict[key].get_role() == "Patient":
        patient_info = (user_dict[key].get_name(), user_dict[key].get_name())
        patient_list.append(patient_info)


class DocAppointmentForm(Form):
    Department = SelectField("Department", [validators.DataRequired()],
                             choices=[('', 'Select'), ('Cardiology', 'Cardiology'),
                                      ('Gastroenterology', 'Gastroenterology'),
                                      ('Haematology', 'Haematology')])
    Date = DateField("Appointment Date", [validators.DataRequired()], format='%Y-%m-%d')
    Time = SelectField("Appointment Time", [validators.DataRequired()],
                       choices=[('', 'Select'), ('8:00:00', '8AM'), ('10:00:00', '10AM'), ('12:00:00', '12PM'),
                                ('14:00:00', '2PM'), ('16:00:00', '4PM'),
                                ('18:00:00', '6PM'), ('20:00:00', '8PM'), ('22:00:00', '10PM')], default='')
    Type = SelectField("Appointment Type", [validators.DataRequired()],
                       choices=[('', 'Select'), ('E-Doctor', 'E-Doctor'), ('Visit', 'Visit')])
    Patient = SelectField("Patient", [validators.DataRequired()], choices=patient_list, default='')


class DocCommentForm(Form):
    Department = SelectField("Department", [validators.DataRequired()],
                             choices=[('', 'Select'), ('Cardiology', 'Cardiology'),
                                      ('Gastroenterology', 'Gastroenterology'),
                                      ('Haematology', 'Haematology')])
    Date = DateField("Appointment Date", [validators.DataRequired()], format='%Y-%m-%d')
    Time = SelectField("Appointment Time", [validators.DataRequired()],
                       choices=[('', 'Select'), ('8:00:00', '8AM'), ('10:00:00', '10AM'), ('12:00:00', '12PM'),
                                ('14:00:00', '2PM'), ('16:00:00', '4PM'),
                                ('18:00:00', '6PM'), ('20:00:00', '8PM'), ('22:00:00', '10PM')], default='')
    Type = SelectField("Appointment Type", [validators.DataRequired()],
                       choices=[('', 'Select'), ('E-Doctor', 'E-Doctor'), ('Visit', 'Visit')])
    Patient = SelectField("Patient", [validators.DataRequired()], choices=patient_list, default='')
    Comment = StringField("Comments", [validators.Optional()])
