from models import db, User, Task, ArchivedTasks


# Function to return all tasks from Task table
def get_all_tasks():
    return Task.query.all()

# Function to return all archived tasks from ArchivedTasks table
def get_archived_tasks():
    return ArchivedTasks.query.all()

# Function to create a new user in the database
def create_user(name, username, password):
    try:
        # Create a new user instance
        new_user = User(username=username, name=name)
        # Hash the user's password
        new_user.set_password(password)
        # Add the new user to the database session
        db.session.add(new_user)
        # Commit the transaction to save the user to the database
        db.session.commit()
    except Exception as e:
        # Log any exceptions that occur during user creation
        print(f"Error creating user: {e}")
        # Re-raise the exception to be handled by the caller
        raise

def login_user(username, password):
    if not username or not password:
        return False, 'Username and password are required'
    #Find a user based on their unique username and authenticate it with their hashed password
    try:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return True, 'Login has been successful!'
        return False, 'The credentials you have inputted are incorrect, please try again or contact customer support.'
    except Exception as e:
        print(f"Error during login: {e}")
        raise
