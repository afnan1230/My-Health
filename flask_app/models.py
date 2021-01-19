"""
models.py
Classes that blueprint all data that will be stored in the sqlite database. Includes a user, routine, workout, run, water intake, sleep data, and heart rate data

Last Modified: 01/14/2021
"""
from datetime import datetime, date
from flask_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    """
    Manages login process
    """
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    """
    Class that models a user of the app. Includes account/login information, physical information (height, weight, etc.), 
    and relationships to workouts, runs, water intake, etc. associated to the user.
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable = False)
    last_name = db.Column(db.String(20), nullable = False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    height = db.Column(db.REAL,nullable = False)
    weight = db.Column(db.REAL,nullable = False)
    num_runs = db.Column(db.Integer,nullable = False, default = 0)
    total_distance = db.Column(db.REAL,nullable = False, default = 0.0)
    posts = db.relationship('Post', backref='author', lazy=True)
    rout = db.relationship('Routine', backref = 'person', lazy = True)
    work = db.relationship('Workout', backref = 'human', lazy = True)
    runs = db.relationship('Runs', backref = 'user', lazy = True)
    water = db.relationship("Water", backref = 'drinker', lazy = True)
    sleep = db.relationship("Sleep",backref = 'sleeper', lazy = True)
    heart = db.relationship("HeartRate", backref = "who", lazy = True)
    def __repr__(self):
        """
        String representation of the User object

        Args:
            -self: the User instance

        Returns:
            String representation of the user
        """
        return f"User('{self.first_name} {self.last_name}', '{self.email}', '{self.height} inches', '{self.weight} pounds')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
class Routine(db.Model):
    """
    Class that models a routine of a user. Includes date of routine, the workouts, and the frequency of the workout, and the user id of the
    user it is associated with
    """
    id = db.Column(db.Integer,primary_key= True)
    date_started = db.Column(db.DateTime,nullable=False, default = date.today())
    routine = db.Column(db.PickleType,nullable = False, default = {})
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)
    
    def __repr__(self):
        """
        String representation of the Routine object

        Args:
            -self: the User instance

        Returns:
            String representation of the routine
        """
        return f"Routine('{self.routine}','{self.date_started}')"
class Workout(db.Model):
    """
    Class that blueprints a workout of a user. Includes data, duration of workout, type of workout, and the user id of the
    user it is associated with.
    """
    id = db.Column(db.Integer, primary_key = True)
    exercise = db.Column(db.String(100))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    def __repr__ (self):
        """
        String representation of the Workout object

        Args:
            -self: the User instance

        Returns:
            String representation of the workout
        """
        return f"Workout('{self.exercise}','{self.date}','{self.time}')"
class Runs(db.Model):
    """
    Class that represents a run of a user. Includes data such as date, duration of run, distance of run, and the user id of the
    user it is associated with
    """
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    distance = db.Column(db.REAL, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    def __repr__ (self):
        """
        String representation of the Runs object

        Args:
            -self: the User instance

        Returns:
            String representation of the runs
        """
        return f"Run('{self.distance}','{self.date}','{self.time}')"
class Water(db.Model):
    """
    Class that represents data of water intake of a user. Includes date of data, number of cups drinken, and the user id of the
    user it is associated with
    """
    id = db.Column(db.Integer, primary_key = True)
    num_cups = db.Column(db.Integer,nullable = False)
    date = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)
    def __repr__ (self):
        """
        String representation of the Water object

        Args:
            -self: the User instance

        Returns:
            String representation of the water intake data
        """
        return f"Water('{self.num_cups}','{self.date}')"
class Sleep(db.Model):
    """
    Class that represents sleep data of a user. Includes start time of sleep, end time of sleep, and the user id of the
    user it is associated with
    """
    id = db.Column(db.Integer,primary_key = True)
    start_time = db.Column(db.DateTime,nullable = False)
    end_time = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    def __repr__ (self):
        """
        String representation of the Sleep object

        Args:
            -self: the User instance

        Returns:
            String representation of the sleep data
        """
        return f"Sleep('{self.start_time}','{self.end_time}')"
class HeartRate(db.Model):
    """
    Class that represents data of a heart rate measruement. Includes date, the measurement, and the user id of the
    user it is associated with
    """
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    heartrate = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)
    def __repr__ (self):
        """
        String representation of the HeartRate object

        Args:
            -self: the User instance

        Returns:
            String representation of the heart rate data
        """
        return f"Heart Rate('{self.date}','{self.heartrate}')"
    
db.create_all()