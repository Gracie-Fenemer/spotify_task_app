from flask_sqlalchemy import SQLAlchemy # manages DB interactions
from sqlalchemy.orm import DeclarativeBase # class to define models in SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# Empty class used as base for all models - extends DeclarativeBase
class Base(DeclarativeBase):
    pass

# SQLAlchemy instance - sets up DB connection and metadata
db = SQLAlchemy(model_class=Base)

# User model
class User(db.Model):
    __tablename__ = 'Users' # table in the DB
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password): # Function to set password
        self.password = generate_password_hash(password) # Hash the password and store it in the database

    def check_password(self, password): # Function to check password
        return check_password_hash(self.password, password) # Check if the provided password matches the stored hash

# Task model - includes columns with constraints
class Task(db.Model):
    __tablename__ = 'Tasks' # table in the DB
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    task_description = db.Column(db.Text, nullable=True)
    task_owner = db.Column(db.String(255), nullable=True)
    task_tag = db.Column(db.Enum('cleaning', 'cooking', 'shopping', 'gardening', 'laundry', 'DIY', 'finance', 'home', 'pets', 'childcare')) # predefined choices
    task_due = db.Column(db.String(100), nullable=True)
    task_status = db.Column(db.Enum('New', 'In Progress', 'Completed')) # predefined choices

# Goal model - includes columns with constraints
class Goal(db.Model):
    __tablename__ = 'Goals' # table in the DB
    goal_id = db.Column(db.Integer, primary_key=True)
    goal_name = db.Column(db.String(255), nullable=False)
    goal_target = db.Column(db.Text, nullable=True)
    goal_progress = db.Column(db.Enum('Achieved', 'Almost Achieved', 'Attempted', 'Not Today'))
    goal_owner = db.Column(db.String(255), nullable=False)

# Archived Tasks model - for completed and archived tasks
class ArchivedTasks(db.Model):
    __tablename__ = 'ArchivedTasks'
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    task_description = db.Column(db.Text, nullable=True)
    task_owner = db.Column(db.String(255), nullable=True)
    task_tag = db.Column(db.Enum('cleaning', 'cooking', 'shopping', 'gardening', 'laundry', 'DIY', 'finance', 'home', 'pets', 'childcare'))
    task_due = db.Column(db.String(100), nullable=True)
    task_status = db.Column(db.Enum('Completed')) # only completed tasks can be archived

