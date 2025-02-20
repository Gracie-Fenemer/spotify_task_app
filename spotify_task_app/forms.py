from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeLocalField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length
class GeneralForm(FlaskForm):
    submit = SubmitField('Submit') # all child class forms will have a submit button

class SignUpForm(GeneralForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 255)])
    username = StringField('Username', validators=[DataRequired(), Length(1, 255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 255)])
    submit = SubmitField('Sign up')

class LoginForm(GeneralForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 255)])
    submit = SubmitField('Login')

# Child Class TaskForm - form with fields to add tasks
class TaskForm(GeneralForm):
    name = StringField('Task', validators=[DataRequired(), Length(1, 255)])
    description = StringField('Description')
    owner = StringField('Owner', validators=[Length(0, 255)])
    tag = SelectField('Tag', choices=[
        ('cleaning', 'Cleaning'),
        ('cooking', 'Cooking'),
        ('shopping', 'Shopping'),
        ('gardening', 'Gardening'),
        ('laundry', 'Laundry'),
        ('DIY', 'DIY'),
        ('finance', 'Finance'),
        ('home', 'Home'),
        ('pets', 'Pets'),
        ('childcare', 'Childcare')
    ], validators=[DataRequired()])
    due = DateTimeLocalField('Due', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])


# Child Class UpdateTaskForm - form with fields to update tasks (only certain fields available for update)
class UpdateTaskForm(GeneralForm):
    description = StringField('Description')
    owner = StringField('Owner', validators=[DataRequired(), Length(1, 255)])
    status = SelectField('Status', choices=[
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])


# Child Class GoalForm - form with fields to add goals
class GoalForm(GeneralForm):
    name = StringField('Goal', validators=[DataRequired(), Length(1, 255)])
    target = StringField('Target')
    owner = StringField('Owner', validators=[DataRequired(), Length(1, 255)])


# Child Class UpdateGoalForm - form with fields to update goals (only certain fields available for update)
class UpdateGoalForm(GeneralForm):
    progress = SelectField('Progress', choices=[
        ('Achieved', 'Achieved'),
        ('Almost Achieved', 'Almost Achieved'),
        ('Attempted', 'Attempted'),
        ('Not Today', 'Not Today')
    ], validators=[DataRequired()])