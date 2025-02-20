# Engineering 4 Group 2 CFG Degree Project
## The Manager
<a id="readme-top"></a>


<!-- SPOTIFY LOGO Add once file srtucture is known -->
<!-- <br />
<div align="center">
  <a href="">
    <img src="asslocation/Spotify_Icon_RGB_Green.png" alt="Logo" width="80" height="80">
  </a> -->

<h3 align="center">Task and Goal Manager with Spotify Integration</h3>

</div>

<!-- ABOUT THE PROJECT -->
## About The Project

 A task and goal management application built with the Flask web framework and MySQL. This Python application integrates with Spotify's web API to help users stay motivated by recommending a Spotify playlist tailored to their activities and helps users organise and track their household responsibilities and personal goals by adding accountability and motivation. 

###  Features

<ul>
<li><b>Task Management: </b>view, create, claim and update tasks. </li>
<li><b>Goal Management: </b>create, update and track the progress of personal goals.</li>
<li><b>Spotify API Integration: </b>users can select activity tag and are then recommended a playlist.</li>
<li><b>Database Integration: </b>data storage for users, tasks and goals using MySQL database.</li>
<li><b>Exception Handling: </b> incorporates exception handling to manage errors and ensure the reliability of the application and data integrity.</li>
</ul>

###  Spotify API Integration
This integration uses spotipy, a lightweight Python library for the Spotify web API. OAuth 2.0 is implemented using SpotifyOAuth to handle user authentication.

Spotify is integrated with each task or goal entry through selected tags, such as 'cleaning.' When a user selects a task or goal category, the app automatically associates it with a predetermined Spotify playlist that fits the nature of the task. The Spotify API retrieves a link to the playlist, and appends it to the task or goal entry within the database.

The user can then click the link, access the playlist and be motivated without having to think about what to play!

<!-- GETTING STARTED -->
## Getting Started

 Follow these instructions to set up and run the project locally:

### Prerequisites

Ensure you have the following installed:

1. [Python 3](https://www.python.org/downloads/)
2. [MySQL Database](https://dev.mysql.com/downloads/)
3. [Required packages in requirements.txt]()

### Installation

1. Clone the Repository

```sh
git clone git@github.com:Gracie-Fenemer/spotify_task_app.git
cd spotify_task_app
```

2. Set up a virtual environment (recommended)
```sh
python -m .venv
source .venv/bin/activate
```

3. Install dependencies

```sh
pip install -r requirements.txt
```
4. Configure the database

  Create database by running 'manager.sql' script in MySQL

```sh
add password to app.py:

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USERNAME:PASSWORD@localhost/Manager'
```

6. Run the application

```sh
flask run
```


## Testing

To verify that the taks API works as expected, run the `TestApp` tests.

Create database by running 'managertest.sql' script in MySQL

Configure database:

```sh
add password to app_test.py:

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USERNAME:PASSWORD@localhost/ManagerTest'
```

```sh
add password to login_test.py:

cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USERNAME:PASSWORD@localhost/ManagerTest'
```

In the terminal, run the following command:

```sh
python app_test.py
```

```sh
python login_test.py
```

To verify that the Spotify API works as expected, run the `spotify_test.py` tests from the root directory.

In the terminal, run the following commands:

```sh
python -m unittest discover
```

## Authors

👤 **Cherryl** * Github: [@ch3rryl](https://github.com/ch3rryl)

👤 **Mary-Ann** * Github: [@MaryannO1992](https://github.com/MaryannO1992)

👤 **Gracie** * Github: [@Gracie](https://github.com/Gracie-Fenemer)

👤 **Katy** * Github: [@GRubikshtein](https://github.com/Rubikshtein)

👤 **Alicja** * Github: [@GANazaniny](https://github.com/ANazaniny)

👤 **Lidia** * Github: [@LidiaS98)](https://github.com/LidiaS98)

### References:

- https://python-adv-web-apps.readthedocs.io/en/latest/flask_db1.html
- https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/
- https://flask.palletsprojects.com/en/3.0.x/testing/
- https://docs.sqlalchemy.org/en/20/tutorial/data_select.html
- https://pypi.org/project/Flask-SQLAlchemy/
- https://pypi.org/project/flask-unittest/
- https://bootstrap-flask.readthedocs.io/en/stable/advanced/#bootswatch-themes
- https://www.freecodecamp.org/news/how-to-setup-user-authentication-in-flask/
- https://developer.spotify.com/documentation/web-api/concepts/apps

***
