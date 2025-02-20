from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf # generate tokens
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DataError
import secrets
import os
import warnings
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from models import db, User, Task, Goal
from utils import get_all_tasks, get_archived_tasks, login_user, create_user
from forms import TaskForm, UpdateTaskForm, GoalForm, UpdateGoalForm, SignUpForm, LoginForm
from dotenv import load_dotenv

load_dotenv()

# Flask app instance
app = Flask(__name__)

# Secure secret key generation - session management and CSRF protection
app.secret_key = secrets.token_urlsafe(16)

# Bootstrap initialization - styling
bootstrap = Bootstrap5(app)

# CSRF protection initialisation
csrf = CSRFProtect(app)

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USER:PASSWORD@localhost/Manager' # DB connection url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disables SQLAlchemy event system - performance

db.init_app(app) # SQLAlchemy instance with Flask app - initialises DB object

# Spotify configuration
app.config['SECRET_KEY'] = os.urandom(64)

# Client credentials stored in variables from .env
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
# This is the redirect url for the spotify app
redirect_uri = 'http://localhost:5003/callback'
scope = 'playlist-read-private', 'playlist-read-collaborative'  # add more with commas

""" 
Tells the spotipy library what type of authentication 
we want to use which is the authorization code flow, 
OAuth. Then this sets up a session in Flask and 
stores the access token.
"""
cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
# Creates an instance of the spotify client,
# allowing the app to interact with the Spotify web app
sp = Spotify(auth_manager=sp_oauth)

# An update for Spotipy is needed so it gives a warning which we can ignore for now
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Function to generate CSRF tokens when used outside Flask-WTF forms (for claiming tasks)
def get_token():
    return generate_csrf()

# Login endpoint
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm() # Flask form
    if form.validate_on_submit(): # form validation
        username = form.username.data # username data
        password = form.password.data # password data
        success, message = login_user(username, password)
        if success:
            session['username'] = username
            print('In session') # debugging statement
            return redirect(url_for('app_home'))
        else:
            flash('Invalid username or password')
    else:
        print('Session failed') # debugging statement
    return render_template('login.html', form=form)

# Signup endpoint - redirects to login page if registration successful
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm() # Flask form
    if form.validate_on_submit(): # form validation
        username = form.username.data
        password = form.password.data
        name = form.name.data
        existing_user = User.query.filter_by(username=username).first() # checks db if username already exists
        if existing_user:
            flash('Username already exists. Please choose a different one.')
        else:
            create_user(name, username, password)
            flash('Account created successfully! Please log in.')
            return redirect(url_for('app_home'))
    return render_template('signup.html', form=form)

# Logout endpoint - redirects to login page
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Welcome endpoint - renders app-home.html template (app home page)
@app.route('/app')
def app_home():
    if 'username' not in session: # session validation
        return redirect(url_for('login'))
    return render_template('app-home.html')


# Tasks Overview endpoint - displays all tasks, passes tasks and token to html
@app.route('/overview-tasks', methods=['GET', 'POST'])
def overview_tasks():
    try: # exception handling included to catch SQL Alchemy error
        tasks = get_all_tasks() # from models.py
        csrf_token = get_token() # users can update/claim tasks from this page so tokens added for security and data manipulation
        return render_template('overview-tasks.html', tasks=tasks, csrf_token=csrf_token)
    except SQLAlchemyError as e:
        flash('Error occurred while retrieving tasks') # error message
        return render_template('overview-tasks.html', tasks=tasks, csrf_token=csrf_token)

# Goals Overview endpoint - displays all goals, passes goals to html
@app.route('/overview-goals', methods=['GET', 'POST'])
def overview_goals():
    username = session['username'] # get session username
    try: # exception handling included to catch SQL Alchemy error
        goals = Goal.query.filter_by(goal_owner=username).all() # get current user goals only
        return render_template('overview-goals.html', goals=goals)
    except SQLAlchemyError as e:
        flash('Error occurred while retrieving goals')
        return render_template('overview-goals.html', goals=goals)

# Archived Tasks Overview - displays all archived tasks, passes archived tasks to html
@app.route('/archived-tasks', methods=['GET', 'POST'])
def archived_tasks():
    try: # exception handling included to catch SQL Alchemy error
        archived_tasks = get_archived_tasks()
        return render_template('archived-tasks.html', archived_tasks=archived_tasks)
    except SQLAlchemyError as e:
        flash('Error occurred while retrieving archived tasks')
        return render_template('archived-tasks.html', archived_tasks=archived_tasks)

# Add Task endpoint - creates task, redirects to Overview Tasks
@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    form = TaskForm() # Flask form
    if form.validate_on_submit(): # form validation
        try:
            task = Task( # creates new task object
                task_name=form.name.data,
                task_description=form.description.data,
                task_owner=form.owner.data,
                task_tag=form.tag.data,
                task_due=form.due.data,
                task_status=form.status.data
            )
            db.session.add(task) # adds to session
            db.session.commit() # commits to DB
            flash('Task created') # success message
            return redirect(url_for('overview_tasks')) # redirects to tasks overview
        except DataError as e: # exception handling included to catch SQL Alchemy data error
            db.session.rollback() # rollback transaction
            flash('Incorrect data provided') # error message
        except OperationalError as e: # exception handling included to catch SQL Alchemy operational error
            db.session.rollback()
            flash('Database could not be reached')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Database Error: task could not be created')

    return render_template('add-task.html', form=form) # if not redirected

# Add Goal endpoint - creates goal, redirects to Overview Goals
@app.route('/add-goal', methods=['GET', 'POST'])
def add_goal():
    form = GoalForm() # Flask form
    if form.validate_on_submit(): # form validation
        try:
            goal = Goal( # creates new goal object
                goal_name=form.name.data,
                goal_target=form.target.data,
                goal_owner=form.owner.data
            )
            db.session.add(goal) # adds to session
            db.session.commit() # commits to DB
            flash('Goal created') # success message
            return redirect(url_for('overview_goals')) # redirects to goals overview
        except DataError as e: # exception handling included to catch SQL Alchemy data error
            db.session.rollback() # rollback transaction
            flash('Incorrect data provided') # error message
        except OperationalError as e: # exception handling included to catch SQL Alchemy operational error
            db.session.rollback()
            flash('Database could not be reached')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Database Error: goal could not be created')
    return render_template('add-goal.html', form=form) # if not redirected

# Update Task endpoint - updates task, redirects to Overview Tasks
@app.route('/update-task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id) # gets task by id, 404 for debugging
    form = UpdateTaskForm(obj=task) # data added to form
    if form.validate_on_submit(): # form validation
        try:
            task.task_description = form.description.data
            task.task_owner = form.owner.data
            task.task_status = form.status.data
            db.session.commit() # commits update to DB
            flash('Task updated') # success message
            return redirect(url_for('overview_tasks')) # redirects to tasks overview
        except DataError as e: # exception handling included to catch SQL Alchemy data error
            db.session.rollback() # rollback transaction
            flash('Incorrect data provided') # error message
        except OperationalError as e: # exception handling included to catch SQL Alchemy operational error
            db.session.rollback()
            flash('Database could not be reached')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Database Error: task could not be updated')
    return render_template('update-task.html', form=form, task=task) # if not redirected

# Update Goal endpoint - updates goal, redirects to Overview Goals
@app.route('/update-goal/<int:goal_id>', methods=['GET', 'POST'])
def update_goal(goal_id):
    goal = Goal.query.get(goal_id) # gets goal by id
    form = UpdateGoalForm(obj=goal) # data added to form
    if form.validate_on_submit(): # form validation
        try:
            goal.goal_progress = form.progress.data
            db.session.commit() # commits update to DB
            flash('Goal updated') # success message
            return redirect(url_for('overview_goals')) # redirects to goals overview
        except DataError as e: # exception handling included to catch SQL Alchemy data error
            db.session.rollback()
            flash('Incorrect data provided') # error message
        except OperationalError as e: # exception handling included to catch SQL Alchemy operational error
            db.session.rollback() # rollback transaction
            flash('Database could not be reached')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Database Error: goal could not be updated')
    return render_template('update-goal.html', form=form, goal=goal) # if not redirected

# Claim Task endpoint - assigns task to user, redirects to Overview Tasks
@app.route('/claim-task/<int:task_id>', methods=['GET', 'POST'])
def claim_task(task_id):
    task = Task.query.get(task_id) # form data
    username = session['username']
    task.task_owner = username #'Katy' # updates owner
    try: # exception handling included to catch SQL Alchemy error
        db.session.commit() # commits update to DB
        flash('Task claimed') # success message
    except SQLAlchemyError as e:
        db.session.rollback() # rollback transaction
        flash('Database Error: task could not be claimed') # error message
    return redirect(url_for('overview_tasks')) # redirects to tasks overview


# Spotify endpoints
# Spotify login page that automatically opens and allows access to the user's spotify 
# account or allows them to create an account
@app.route('/spotify')
def spotify_home():
    try:
        if not sp_oauth.validate_token(cache_handler.get_cached_token()):
            auth_url = sp_oauth.get_authorize_url()
            return redirect(auth_url)
        return redirect(url_for('home_page'))
    except Exception as e:
        app.logger.error(f'Spotify URL error: {e}')
        flash('Cannot reach Spotify, please refresh the page and try again.')
        return render_template('error.html'), 500


# Callback refreshes the token once it expires, so the user may need to 
# refresh the page if they cannot gain access
@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('home_page'))


# Home page endpoint that shows after login. This is where the user can select the 
# type of task they are doing and it gives them a choice of albums or playlists.
# They can then click on the link and it opens spotify in a new tab in the browser
@app.route('/home_page')
def home_page():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        print('Redirecting to auth URL')
        return redirect(auth_url)

    return render_template('home_page.html')
    # return render_template('error.html') - line for testing error page


# Default choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/cleaning')
def album_sza():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    sza_uri = 'spotify:artist:7tYKF4w9nC0nq9CsPZTHyP'
    results = sp.artist_albums(sza_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    albums_html = '<ul>'
    for album in albums:
        album_name = album['name']
        album_url = album['external_urls']['spotify']
        albums_html += f"<li>{album_name}: <a href='{album_url}' target='_blank'>{album_url}</a></li>"
    albums_html += '</ul>'

    return render_template('cleaning.html', albums_html=albums_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/cooking')
def album_sam_smith():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    sam_smith_uri = 'spotify:artist:2wY79sveU1sp5g7SokKOiI'
    results = sp.artist_albums(sam_smith_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    albums_html = '<ul>'
    for album in albums:
        album_name = album['name']
        album_url = album['external_urls']['spotify']
        albums_html += f"<li>{album_name}: <a href='{album_url}' target='_blank'>{album_url}</a></li>"
    albums_html += '</ul>'

    return render_template('cooking.html', albums_html=albums_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/gardening')
def gardening_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    jazz_uris = ['spotify:playlist:37i9dQZF1DZ06evO0Co11u',
                 'spotify:playlist:37i9dQZF1EIeptNKrK95ex',
                 'spotify:playlist:37i9dQZF1DWV7EzJMK2FUI']

    playlist_html = '<ul>'
    for uri in jazz_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li class='a2'>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('gardening.html', playlist_html=playlist_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/shopping')
def shopping_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    shopping_uris = ['spotify:playlist:2P0VBAcUPSzjhgYUsIyjjb',
                     'spotify:playlist:2jMTSDkouGnpYE3JXAuRjy',
                     'spotify:playlist:59bquJNzpBVlzePmksrzZ7']

    playlist_html = '<ul>'
    for uri in shopping_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('shopping.html', playlist_html=playlist_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/laundry')
def laundry_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    laundry_uris = ['spotify:playlist:1ftFIOsNNt5mXJepj3wzuH',
                    'spotify:playlist:37i9dQZF1DWT0IiTU5mrJ9',
                    'spotify:playlist:4muHyvSwG1wP9sI4XihC5w']

    playlist_html = '<ul>'
    for uri in laundry_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('laundry.html', playlist_html=playlist_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/diy')
def diy_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    diy_uris = ['spotify:playlist:2njiabuQAJcRTKC4CDja47',
                'spotify:playlist:4NMom1HAG5Nk2MvlueSsF7',
                'spotify:playlist:3okUIpItRWF127C92YaXQ6']

    playlist_html = '<ul>'
    for uri in diy_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('diy.html', playlist_html=playlist_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/finance')
def finance_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    finance_uris = ['spotify:playlist:6E5WGfx9LF2rU1pqTGQlh5',
                    'spotify:playlist:0ZMw0qV3CyIuBuBObouD1L',
                    'spotify:playlist:31yp6AccQFiIwvC1SPnG7J']

    playlist_html = '<ul>'
    for uri in finance_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('finance.html', playlist_html=playlist_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/home')
def home_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    home_uris = ['spotify:playlist:7BdkdQkR7GANVz11eElkpn',
                 'spotify:playlist:2lB5UHNDgcQlSxafzqlUdq',
                 'spotify:playlist:0kgirc9upn9id02xsxutPT']

    playlist_html = '<ul>'
    for uri in home_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('home.html', playlist_html=playlist_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/pets')
def pets_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    pets_uris = ['spotify:playlist:2uXOLlA9SOwGKAWq8Ur5MH',
                 'spotify:playlist:0tMwcHD10Mw0St4JswNLUI',
                 'spotify:playlist:2R79wZ0MgXLUz33bBbKPIM']

    playlist_html = '<ul>'
    for uri in pets_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('pets.html', playlist_html=playlist_html)


# Choice for pick list, redirects to the page with the specific url's
@app.route('/home_page/childcare')
def childcare_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    childcare_uris = ['spotify:playlist:1CKZs4Atk5gBaL40EUVZRg',
                      'spotify:playlist:37i9dQZF1DWVmLl2r5kAOQ',
                      'spotify:playlist:37i9dQZF1DX2UkbeRPWQqZ']

    playlist_html = '<ul>'
    for uri in childcare_uris:
        results = sp.playlist(uri)
        playlist_name = results['name']
        playlist_url = results['external_urls']['spotify']
        playlist_html += f"<li>{playlist_name}: <a href='{playlist_url}' target='_blank'>{playlist_url}</a></li>"
    playlist_html += '</ul>'

    return render_template('childcare.html', playlist_html=playlist_html)

# Spotify logout endpoint and session clear
@app.route('/home_page/logout')
def spotify_logout():
    session.clear()
    return redirect(url_for('spotify_home'))


if __name__ == '__main__':
    app.run(debug=True, port=5003)
