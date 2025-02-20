import unittest
from app import app, db, Task, Goal, get_token
from flask import url_for

# Test case class for Flask app testing
class TestApp(unittest.TestCase):

    def setUp(self): # runs before each test method in class, has to be named setUp, sets up environment, creates test data
        app.config['TESTING'] = True # configures app for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USERNAME:PASSWORD@localhost/ManagerTest' # test DB url
        app.config['WTF_CSRF_ENABLED'] = False # disable cross-site request forgery token
        app.config['SERVER_NAME'] = 'localhost:5003'


        self.client = app.test_client() # test client for Flask app to check HTTP responses
        self.app_context = app.app_context() # app context for Flask
        self.app_context.push() # pushes context to the stack

        db.create_all()

        self.username = 'Test User'

        # test task for DB query tests
        test_task = Task(
            task_name='Test Task',
            task_description='Test Description',
            task_owner='Test Owner',
            task_tag='cooking',
            task_due='2024-08-25 18:00:00',
            task_status='New'
        )

        # test goal for DB query tests
        test_goal = Goal(
            goal_name='Test Goal',
            goal_target='Test Target',
            goal_owner=self.username
        )

        db.session.add(test_task)
        db.session.add(test_goal)
        db.session.commit()

    def tearDown(self): # for DB and app context clean up, called automatically after each test method to reset env
        db.session.remove() # clears current session state
        meta = db.metadata # contains DB data
        for table in reversed(meta.sorted_tables): # iterates in reverse if fk_contraints in DB - deletes child tables first
            db.session.execute(table.delete()) # executes sql delete command
        db.session.commit() # commits transaction to DB
        self.app_context.pop() # removes app context from stack - pushed to stack in setUp


    def test_token(self): # token generation test
        with app.test_request_context(): # this is needed to test code without making HTTP request
            token = get_token()
            self.assertIsNotNone(token, 'Token not None') # checks token not None
            self.assertIsInstance(token, str, 'Token is a string') # check token type str

    def test_home(self): # home page response test
        with self.client as client:
            with client.session_transaction() as sess:
                sess['username'] = 'Test User'
            response = self.client.get(url_for('app_home')) # home page get request check
            self.assertEqual(response.status_code, 200) # response status code check
            self.assertIn(b'Welcome to The Manager', response.data) # byte string in response data check - welcome message

    def test_overview_tasks(self): # tasks overview page response test
        response = self.client.get(url_for('overview_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tasks Overview', response.data)

    def test_overview_goals(self): # goals overview page response test
        with self.client as client: # simulate user login
            with client.session_transaction() as sess:
                sess['username'] = self.username
            response = self.client.get(url_for('overview_goals'))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Goals Overview', response.data)

    def test_archived_tasks(self): # archived tasks overview page response test
        response = self.client.get(url_for('archived_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Archived Tasks Overview', response.data)

    def test_add_task(self): # add task test
        response = self.client.post(url_for('add_task'), data={ # posts form data
            'name': 'Test Task Name',
            'description': 'Test Task Description',
            'owner': 'Test Task Owner',
            'tag': 'finance',
            'due': '2024-08-25T18:30',
            'status': 'New'
        })
        self.assertEqual(response.status_code, 302) # redirect - overview tasks
        task = Task.query.filter_by(task_name='Test Task Name').first() # checks DB
        self.assertIsNotNone(task) # checks task not None
        self.assertEqual(task.task_description, 'Test Task Description') # check description data match

    def test_add_goal(self): # add goal test
        with self.client as client:
            with client.session_transaction() as sess:
                sess['username'] = 'Test User'
            response = self.client.post(url_for('add_goal'), data={ # posts form data
                'name': 'Test Goal Name',
                'target': 'Test Goal Target',
                'owner': 'Test User'
            })
            self.assertEqual(response.status_code, 302)
            goal = Goal.query.filter_by(goal_name='Test Goal Name').first() # checks DB
            self.assertIsNotNone(goal) # checks goal not None
            self.assertEqual(goal.goal_target, 'Test Goal Target') # checks target data match
            self.assertEqual(goal.goal_owner, 'Test User')

    def test_update_task(self): # update task test
        task = Task.query.first()
        response = self.client.post(url_for('update_task', task_id=task.task_id), data={ # posts updated task
            'description': 'Updated Task Description',
            'owner': 'Updated Task Owner',
            'status': 'In Progress'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'In Progress', response.data) # byte string in response data check - updated task status

        updated_task = db.session.get(Task, task.task_id) # checks DB
        self.assertEqual(updated_task.task_description, 'Updated Task Description') # checks description data match
        self.assertEqual(updated_task.task_owner, 'Updated Task Owner') # checks owner data match
        self.assertEqual(updated_task.task_status, 'In Progress') # checks status data match

    def test_update_goal(self): # update goal test
        with self.client as client:  # simulate user login
            with client.session_transaction() as sess:
                sess['username'] = self.username
            goal = Goal.query.first()
            response = self.client.post(url_for('update_goal', goal_id=goal.goal_id), data={ # posts updated goal
                'progress': 'Almost Achieved'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Almost Achieved', response.data) # byte string in response data check - updated goal progress

            updated_goal = db.session.get(Goal, goal.goal_id) # checks DB
            self.assertEqual(updated_goal.goal_progress, 'Almost Achieved') # checks progress data match

    def test_claim_task(self): # claim task test
        with self.client as client:  # simulate user login
            with client.session_transaction() as sess:
                sess['username'] = self.username
            task = Task.query.first()
            response = self.client.post(url_for('claim_task', task_id=task.task_id), data={ # posts new owner
                'owner': 'Test User'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test User', response.data) # byte string in response data check - updated task owner
            claimed_task = db.session.get(Task, task.task_id) # checks DB
            self.assertEqual(claimed_task.task_owner, 'Test User') # checks owner data match


if __name__ == '__main__':
    unittest.main()
