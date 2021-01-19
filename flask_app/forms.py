"""
forms.py
File contains classes for all the forms that are used in the MyHealth Web App. 

Last Modified: 01/14/2021
"""
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,PasswordField, SubmitField, BooleanField, FloatField,IntegerField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_app.models import User
from datetime import date,datetime

class RegistrationForm(FlaskForm):
    """
    Class to model the registration form for a new user. Requires a unique username and email, and first and last name, a password, 
    and height and weight
    """
    name = StringField('First Name',validators=[DataRequired(),Length(min =2, max = 20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2,max=25)])
    username = StringField('Username',validators = [DataRequired(),Length(min = 2, max = 20)])
    
    email = StringField('E-mail', validators = [DataRequired(), Email()])
    height = FloatField('Height (inches)', validators=[DataRequired()])
    weight = FloatField('Weight (lbs)',validators=[DataRequired()])
    
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])

    
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        """
        Validation method to make sure a unique username was entered

        Args:
            -self: the form
            -username: the username textbox
        Returns:
            An error/exception if the username entered is not unique
        """
        user = User.query.filter_by(username = username.data).first()
        if (user):
            raise ValidationError('This username already exists. Please choose a different username.')
    def validate_email(self, email):
        """
        Validation method to make sure a unique email was entered

        Args:
            -self: the form
            -email: the email textbox
        Returns:
            An error/exception if the email entered is not unique
        """
        user = User.query.filter_by(email = email.data).first()
        if (user):
            raise ValidationError('This email already exists. Please choose a different email.')
class LoginForm(FlaskForm):
    """
    Class that represents the form that allows returning users to log back in. Requires their email and password.
    """
    email = StringField('E-mail', validators = [DataRequired(), Email()])
    
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember me?')
    
    submit = SubmitField('Login')
class UpdateAccountForm(FlaskForm):
    """
    Form that allows a user to update their profile. Requires a first and last name, username, email, height, and weight. 
    All the default information is the preexisting information.
    """
    name = StringField('First Name',validators=[DataRequired(),Length(min =2, max = 20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2,max=25)])
    username = StringField('Username',validators = [DataRequired(),Length(min = 2, max = 20)])
    
    email = StringField('E-mail', validators = [DataRequired(), Email()])
    height = FloatField('Height (inches)', validators=[DataRequired()])
    weight = FloatField('Weight (lbs)',validators=[DataRequired()])
    

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        """
        Method that checks to make sure that if the username was updated, it is unique

        Args:
            - self: the form
            - username: the username textbox
        
        Returns:
            - An error/exception if the username is not unique.
        """
        if(username.data != current_user.username):
            user = User.query.filter_by(username = username.data).first()
            if (user):
                raise ValidationError('This username already exists. Please choose a different username.')
    def validate_email(self, email):
        """
        Method that checks to make sure that if the email was updated, it is unique

        Args:
            - self: the form
            - email: the email textbox
        
        Returns:
            - An error/exception if the email is not unique.
        """
        if(email.data != current_user.email):
            user = User.query.filter_by(email = email.data).first()
            if (user):
                raise ValidationError('This email already exists. Please choose a different email.')
class RoutineForm(FlaskForm):
    """
    Form to add a routine to your routines. Requires a workout, the starting date, and frequency (Every how many days)
    """
    workout = StringField("Workout",validators=[DataRequired(),Length(min = 2, max = 1000)])
    days = IntegerField("Every how many days?",validators = [DataRequired()])
    start = DateField('When do you want to start? (mm/dd/YYY)',validators=[DataRequired()], format="%m/%d/%Y")
    submit = SubmitField('Add to Routine')
class ExerciseForm(FlaskForm):
    """
    Form to add a workout to your workouts data. Requires a workout, a date, and a duration.
    """
    workout = StringField("Workout:", validators = [DataRequired(),Length(min = 2, max = 1000)])
    date = DateField("What date? (mm/dd/YYYY)",validators=[DataRequired()],format = "%m/%d/%Y")
    duration = TimeField("For how long?",validators=[DataRequired()],format="%H:%M:%S")
    submit = SubmitField('Add to your Workouts')
class RunForm(FlaskForm):
    """
    Form to add a run to your runs/workouts data. Requires a date, duration, and distance.
    """
    date = DateField("What date? (mm/dd/YYYY)",validators=[DataRequired()],format = "%m/%d/%Y")
    duration = TimeField("For how long?",validators=[DataRequired()],format="%H:%M:%S")
    distance = FloatField("For what distance (miles)?",validators=[DataRequired()])
    submit = SubmitField('Add to your Runs')
class WaterForm(FlaskForm):
    """
    Form to add water intake data for the current user. Requires the date and number of cups drinken
    """
    date = DateField("What date?",format='%Y-%m-%d')
    num_cups = FloatField("How many cups?",validators=[DataRequired()])
    submit = SubmitField("Add to Water Intake")
class SleepForm(FlaskForm):
    """
    Form to add sleep data for the current user. Requires, the date and time you went to sleep and the date and time you woke up.
    """
    start_date = DateField("Date you went to sleep:",validators=[DataRequired()],format='%Y-%m-%d')
    start_time = TimeField("What time did you go to sleep? (HH:MM AM/PM)", validators=[DataRequired()])
    end_date = DateField("Date you woke up:",validators=[DataRequired()],format='%Y-%m-%d')
    end_time = TimeField("What time did you wake up? (HH:MM AM/PM)",validators=[DataRequired()])
    submit = SubmitField("Add to your Sleep Data")
    def validate_start(self, start_time):
        try:
            datetime.strptime(start_time.data,'%I:%M %p')
            print('Hello')
        except ValueError:
            raise ValidationError('Start time is not in the right format')
    def validate_end(self, end_time):
        try:
            datetime.strptime(end_time.data,'%I:%M %p')
            print('Hello')
        except ValueError:
            raise ValidationError('End time is not in the right format')
    def validate_startdate(self,start_date):
        try:
            datetime.strptime(start_date.data,'%m/%d/%Y')
            print('Hello')
        except ValueError:
            raise ValidationError('Start date is not in the right format')
    def validate_enddate(self,end_date):
        try:
            datetime.strptime(end_date.data,'%m/%d/%Y')
            print('Hello')
        except ValueError:
            raise ValidationError('End date is not in the right format')
class HeartRate_form(FlaskForm):
    """
    Form to add heart rate data for the current user. Requires the date and the measurement.
    """
    date = DateField("What date? (mm/dd/YYYY)",validators=[DataRequired()],format='%Y-%m-%d')
    measurement = IntegerField("What heart rate did you measure? (bpm)",validators=[DataRequired()])
    submit = SubmitField("Add to Heart Rate Data")