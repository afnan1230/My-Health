"""
routes.py 
contains all the methods for every page/URL for the MyHealth WebApp. 
Is dependent on forms.py and models.py
Last Modified: 01/14/2021
"""
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_app import app, db, bcrypt
from flask_app.models import User, Post, Routine, Workout, Runs, Water, Sleep, HeartRate
from flask_app.forms import RegistrationForm, LoginForm, UpdateAccountForm, RoutineForm, ExerciseForm, RunForm, WaterForm, SleepForm, HeartRate_form
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
from datetime import date,time,datetime,timedelta

@app.route("/")
@app.route("/home")
def home():
    """
    Returns the home welcome page if a user is not logged in yey. Redirects to the dashboard if a user is logged in.

    Args:
        - None
    Returns:
        -Home page or dashboard page
    """
    if(current_user.is_authenticated):
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Page to allow someone to create an account that they can log in with. 

    Args:
        -None

    Returns:
        -Registering page or login page
    """
    if(current_user.is_authenticated):
        return redirect(url_for("dashboard"))
    form = RegistrationForm()
    if (form.validate_on_submit()):
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(first_name=form.name.data, last_name=form.last_name.data, username=form.username.data,
                    email=form.email.data, password=hashed_password, height=form.height.data, weight=form.weight.data)
        db.session.add(user)
        db.session.commit()
        rout = Routine(person=user)
        db.session.add(rout)
        db.session.commit()

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Page that allows a user to login to an already existing account with their email and password. 

    Args:
        -None
    
    Returns:
        - Login page or dashboard page once the user is logged in
    """
    if(current_user.is_authenticated):
        print("hello")
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if (form.validate_on_submit()):
        user = User.query.filter_by(email=form.email.data).first()
        if(user and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if(next_page):
                return redirect(next_page)
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    """
    Logs the user out of the web app. 

    Args:
        - None
    
    Returns:
        -Home page after logging out.
    """
    logout_user()
    return redirect(url_for('home'))


def do_today(current_day, day_started, day):
    difference = (current_day-day_started).days
    if(difference >= 0 and difference % day == 0):
        print("HELLO")
        return True
    else:
        return False


@app.route("/dashboard")
@login_required
def dashboard():
    """
    Returns the dashboard page if the user is currently logged in. 

    Args:
        -None

    Returns:
        - Dashboard page
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    day = date.today()
    r = Routine.query.filter_by(user_id=current_user.id).first()
    r = r.routine
    today = []
    if(r):
        for i in r:
            if((day - r[i][1]).days >= 0  and  (day - r[i][1]).days% r[i][0] == 0):
                today.append(i)
    stuff = len(today)

    return render_template('dashboard.html', title="dashboard", routine=r, day=day,stuff=stuff)


def save_picture(form_picture):
    """
    saves a picture in local files so it can be added as a profile pic

    Args:
        -form_picture: the name of the file of the picture

    returns:
        the path of the picture
    """
    file_name = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = file_name + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    form_picture.save(picture_path)
    return picture_fn


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    """
    Returns the profile page of the web app if a user is currently logged in.
    Also allows a user to update their profile if desired

    Args:
        - None

    Returns:
        - The profue page
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    form = UpdateAccountForm()
    if(form.validate_on_submit()):
        if(form.picture.data):
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.height = form.height.data
        current_user.weight = form.weight.data
        db.session.commit()
        flash('Your account has been update!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.height.data = current_user.height
        form.weight.data = current_user.weight
        form.name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    height_string = str(int(current_user.height//12)) + \
        "'" + str(int(current_user.height % 12)) + '"'
    return render_template('profile.html', title="profile", image_file=image_file, height_string=height_string, form=form)


@app.route('/dashboard/routines')
@login_required
def routines():
    """
    Returns the page that displays all of the user's routines if they are logged in

    Args:
        -None

    Returns:
        - The routines page
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    day = date.today()
    routine = Routine.query.filter_by(user_id=current_user.id).first()
    return render_template('routines.html', title='routines', routine=routine.routine, day=day)


@app.route('/dashboard/routines/add_routine', methods=['GET', 'POST'])
@login_required
def add_routine():
    """
    Returns the page with the form that allows a user to add or update a routine.

    Args:
        - None

    Returns:
        - Page with the form that allows you to update or add a routine.
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    form = RoutineForm()
    if(form.validate_on_submit()):
        r = Routine.query.filter_by(user_id=current_user.id).first()
        r_dict = r.routine
        work = form.workout.data
        days = form.days.data
        r_dict[work] = [days]
        r_dict[work].append(form.start.data)
        db.session.delete(r)
        rout = Routine(routine=r_dict, person=current_user)
        db.session.commit()
        print(Routine.query.filter_by(user_id=current_user.id).first())
        flash('Workout has been added to your routine!', 'success')
        return redirect(url_for('routines'))
    return render_template('add_routine.html', title='add routine', form=form, legend="Add to your Routine")


@app.route('/dashboard/routines/<rout>/edit', methods=["GET", "POST"])
@login_required
def edit_routine(rout):
    """
    Allows a user to edit a current routine they already have

    Args:
        -rout: the routine that the user wants to update or edit.

    Returns:
        - Same form page as add_routine() to add or update a routine.
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    routine = Routine.query.filter_by(user_id=current_user.id).first()
    form = RoutineForm()
    if(form.validate_on_submit()):
        r_dict = routine.routine
        del(r_dict[rout])
        work = form.workout.data
        days = form.days.data
        r_dict[work] = [days]
        r_dict[work].append(form.start.data)
        db.session.delete(routine)
        r = Routine(routine=r_dict, person=current_user)
        db.session.commit()
        flash('Workout has been successfully updated!', 'success')
        return redirect(url_for('routines'))
    elif (request.method == 'GET'):
        form.workout.data = rout
        form.days.data = routine.routine[rout][0]
        form.start.data = routine.routine[rout][1]
    return render_template('add_routine.html', title="edit routine", form=form, legend="Edit Routine")


@app.route('/dashboard/routines/<rout>/delete', methods=["GET", "POST"])
@login_required
def delete_routine(rout):
    """
    Allows a user to delete something off of their routines

    Args:
        - rout: the routine that the user wants to delete.

    Returns:
        - Returns back to the routines page with the desired routine deleted.

    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    routine = Routine.query.filter_by(user_id=current_user.id).first()
    r_dict = routine.routine
    del(r_dict[rout])
    db.session.delete(routine)
    rout = Routine(routine=r_dict, person=current_user)
    db.session.commit()
    flash('Workout has been successfully deleted from your routine!', 'success')
    return redirect(url_for('routines'))


@app.route('/dashboard/exercises')
@login_required
def exercises():
    """
    Returns the page that displays past data of your exercises and workouts

    Args:
        - None

    Returns:
        - The page that displays past workout and run data.
    """
    data = False
    run_data = False
    today = date.today()
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    runs = Runs.query.filter_by(user_id = current_user.id).all()
    for w in workouts:
        if((today - w.date).days < 7):
            data = True
    for r in runs:
        if((today - r.date).days<7):
            run_data = True
    return render_template('exercises.html', title='My Exercises', workouts = workouts, runs = runs,today=today,data = data, run_data = run_data)


@app.route('/dashboard/water')
@login_required
def water():
    """
    Returns the page that displays all past data for water intake

    Args:
        - None

    Returns:
        - Page that displays all past water intake data
    """
    most_water = {}
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    cups_today = 0
    waters = Water.query.filter_by(user_id = current_user.id).all()
    for i in waters:
        if(i.date == date.today()):
            cups_today += i.num_cups
    for i in waters:
        if(i.date not in most_water):
            most_water[i.date]= i.num_cups
        else:
            print("HELLO")
            most_water[i.date] = most_water[i.date] + i.num_cups
    most_water_list = sorted(most_water, reverse = True)
    print(most_water)
    return render_template('water.html', title='Water Intake', waters = waters,cups_today = cups_today,today = date.today(),most_water = most_water,most_water_list = most_water_list)


@app.route('/dashboard/sleep')
@login_required
def sleep():
    """
    Returns page that displays past sleep data

    Args:
        - None

    Returns:
        - Page that displays past sleep data
    """
    today = datetime.today()
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    sleeps = Sleep.query.filter_by(user_id = current_user.id).order_by(Sleep.id.desc()).all()
    return render_template('sleep.html', title="Sleep", sleeps = sleeps,today = today)
@app.route('/dashboard/heart_rate')
@login_required
def heart_rate():
    """
    Page that displays past heart rate data

    Args:
        -None

    Returns:
        -Page with past heart rate data
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    heart_rates = HeartRate.query.filter_by(user_id = current_user.id).order_by(HeartRate.id.desc()).all()
    return render_template('heart_rate.html',title = "Heart Rate", heart_rates = heart_rates)
@app.route('/dashboard/exercises/run_or_workout')
@login_required
def run_or_workout():
    """
    Returns page that prompts user to choose between a run or not a run when adding an exercise 

    Args:
        -None

    Returns:
        -Page to prompt user for either a run or not a run.
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    return render_template('run_or_workout.html', title = "Run or Workout")
@app.route('/dashboard/exercises/add_run', methods = ["GET","POST"])
@login_required
def add_run():
    """
    Page that prompts user with a form that allows them to input data for a past run

    Args:
        - None

    Returns:
        -Page to fill out data for a past run.
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    form = RunForm()
    if(form.validate_on_submit()):
        dis = form.distance.data
        date =form.date.data
        time = form.duration.data
        new_run = Runs(date = date, time = time, distance = dis, user_id = current_user.id)
        db.session.add(new_run)
        db.session.commit()
        return redirect(url_for('exercises'))
    return render_template('run_form.html', title= "Add Run", legend = "Add a Run", form =form)
@app.route('/dashboard/exercises/add_workout', methods = ["GET","POST"])
@login_required
def add_workout():
    """
    Page that prompts user with a form that allows them to input data for a past workout

    Args:
        - None

    Returns:
        -Page to fill out data for a past workout
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    form = ExerciseForm()
    if(form.validate_on_submit()):
        name = form.workout.data
        date = form.date.data
        time = form.duration.data
        work = Workout(exercise = name, date = date, time = time, user_id = current_user.id)
        db.session.add(work)
        db.session.commit()
        return redirect(url_for('exercises'))
    return render_template('workout_form.html', title= "Add Workout", legend = "Add a Workout", form =form)
@app.route('/dashboard/water/add_water', methods = ["GET","POST"])
@login_required
def add_water():
    """
    Page that allows user to fill out data for water intake

    Args:
        -None

    Returns:
        - Page that allows user to fill out data for water intake.
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    form = WaterForm()
    if(form.validate_on_submit()):
        cup = form.num_cups.data
        date = form.date.data
        intake = Water(num_cups = cup, date = date, user_id = current_user.id)
        db.session.add(intake)
        db.session.commit()
        return redirect(url_for('water'))
    return render_template('water_form.html', title= "Add Water", legend = "Add Water Intake", form =form)
@app.route('/dashboard/heart_rate/add_heart', methods = ["GET","POST"])
@login_required
def add_heart():
    """
    Page that a user can fill out data for heart rate measurement

    Args:
        - None

    Returns:
        - A page with a form that allows a user to fill out data for heart rate measurement
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    form = HeartRate_form()
    if(form.validate_on_submit()):
        rate = form.measurement.data
        date = form.date.data
        new_rate = HeartRate(date = date, heartrate = rate, user_id = current_user.id)
        db.session.add(new_rate)
        db.session.commit()
        return redirect(url_for('heart_rate'))
    return render_template('heartrate_form.html', title= "Add Water", legend = "Add Sleep Data", form =form)
@app.route('/dashboard/sleep/add_sleep', methods = ["GET","POST"])
@login_required
def add_sleep():
    """
    Page that a user can fill out data for a past sleep

    Args:
        - None

    Returns:
        - A page with a form that allows a user to fill out data for a past sleep
    """
    if(not current_user.is_authenticated):
        return redirect(url_for('home'))
    form = SleepForm()
    if(form.validate_on_submit()):
        startdate = datetime.strftime(form.start_date.data,"%m/%d/%Y")
        enddate = datetime.strftime(form.end_date.data,"%m/%d/%Y")
        starttime = time.strftime(form.start_time.data,"%I:%M %p")
        endtime = time.strftime(form.end_time.data,"%I:%M %p")
        start = startdate+" "+ starttime
        end = enddate + " " + endtime
        start = datetime.strptime(start,"%m/%d/%Y %H:%M %p")
        end = datetime.strptime(end,"%m/%d/%Y %H:%M %p")
        new_sleep = Sleep(start_time = start, end_time = end, user_id = current_user.id)
        db.session.add(new_sleep)
        db.session.commit()
        return redirect(url_for('sleep'))
    return render_template('sleep_form.html',title= 'Add Sleep', legend = "Add Sleep Data", form = form)
def seconds_to_time(seconds):
    """
    Helper method that take a total amount of seconds and converts it into minutes and seconds

    Args:
        -seconds: total number of seconds

    Returns:
        - Minutes and seconds in format M' S"
    """
    minutes = int(seconds//60)
    seconds = int(round(seconds % 60,0))
    return str(minutes)+"'" +str(seconds).zfill(2) + '"'
def add_times(t1, t2):
    """
    Helper method that adds two time objects together to add hours and minures

    Args:
        - t1: the first time object
        - t2: the second time object

    Returns:
        - The result of adding the hours and minutes of both times
    """
    a = timedelta(hours = t1.hour, minutes=t1.minute, seconds= t1.second)
    b = timedelta(hours = t2.hour, minutes=t2.minute, seconds=t2.second)
    return (a+b).time()
@app.route('/personal_stats')
@login_required
def personal_stats():
    """
    Page that displays all the statistics of the current user which include personal bests in running, workouts, time active, and water intake.
    Also displays all averages having to do with running, active time, water intake, and heart rate measurement

    Args:
        - None
    
    Returns:
        - The page that displays all personal statistics for current user.
    """
    if(not current_user.is_authenticated):
        return redirect(url_for("home"))
    longest_run = [0,date.today()]
    fastest_run = [100000,"format",date.today()]
    most_water = {}
    activity = {}
    most_activity = []
    paces = []
    distances = []
    times = []
    rates = []
    min_date = date.today()
    max_date = date.today()
    min_date2 = date.today()
    total_waters = 0
    avg_water = 0
    avg_activity = 0
    avg_distance = 0
    avg_pace = seconds_to_time(0)
    avg_heartrate = 0
    m = 0
    d = date.today()
    runs = Runs.query.filter_by(user_id = current_user.id).all()
    exercises = Workout.query.filter_by(user_id = current_user.id).all()
    waters = Water.query.filter_by(user_id = current_user.id).all()
    heart_rates = HeartRate.query.filter_by(user_id = current_user.id).all()
    for i in runs:
        distances.append(i.distance)
        if(i.distance > longest_run[0]):
            longest_run[0] = i.distance
            longest_run[1] = i.date
        total_seconds = int(i.time.strftime("%H"))*3600 + int(i.time.strftime("%M"))*60 + int(i.time.strftime("%S"))
        pace = round(total_seconds/i.distance,2)
        paces.append(pace)
        if(pace<fastest_run[0]):
            fastest_run[0] = pace
            fastest_run[1] = seconds_to_time(pace)
            fastest_run[2] = i.date
        if(i.date not in activity):
            activity[i.date] = i.time
        else:
            activity[i.date] = add_times(activity[i.date], i.time)
    if(distances):
        avg_distance = sum(distances)/len(distances)
    print(paces)
    if(paces):
        avg_pace = seconds_to_time(sum(paces)/len(paces))
    for i in waters:
        if(min_date > i.date):
            min_date = i.date
        if(i.date not in most_water):
            most_water[i.date]= i.num_cups
        else:
            print("HELLO")
            most_water[i.date] = most_water[i.date] + i.num_cups
    if(most_water.values()):
        m = max(most_water.values())
        d = date.today()
        for i in most_water:
            if(most_water[i] == m):
                d = i 
                break
        avg_water = round(sum(most_water.values())/((max_date-min_date).days + 1),2)
    for i in exercises:
        if(i.date not in activity):
            activity[i.date] = i.time
        else:
            activity[i.date] = add_times(activity[i.date], i.time)
    if(activity):
        m1 = max(activity.values())
        total_activity = 0
        for i in activity:
            if(i < min_date2):
                min_date2 = i
            total_activity += int(activity[i].strftime("%H"))*3600 + int(activity[i].strftime("%M"))*60 + int(activity[i].strftime("%S"))
            if(activity[i] == m1):
                most_activity.append(m1)
                most_activity.append(i)
        avg_activity = total_activity/((max_date-min_date2).days +1)
    avg_time = time(int(avg_activity//3600), int((avg_activity//60)%60), int(avg_activity%60))
    for i in heart_rates:
        avg_heartrate += i.heartrate
    if(heart_rates):
        avg_heartrate/= len(heart_rates)
    return render_template("personal_stats.html", title = "Personal Statistics", longest_run = longest_run, fastest_run = fastest_run, most_water = m, water_date = d, most_activity=most_activity,avg_distance = avg_distance, avg_pace = avg_pace,avg_water = avg_water, avg_time = avg_time,avg_heartrate = avg_heartrate)
@app.route('/dashboard/exercises/all_exercises')
def all_exercises():
    """
    Page that displays all exercise data 

    Args:
        - None
    
    Return:
        - Page that displays exercise data
    """
    workouts = Workout.query.filter_by(user_id = current_user.id).order_by(Workout.date.desc()).all()
    return render_template("all_exercises.html", title = "All Exercises",workouts=workouts)
@app.route('/dashboard/exercises/all_runs')
def all_runs():
    """
    Page that displays all run data 

    Args:
        - None
    
    Return:
        - Page that displays run data
    """
    runs = Runs.query.filter_by(user_id = current_user.id).order_by(Runs.date.desc()).all()
    return render_template("all_runs.html",title = "All Runs", runs = runs)