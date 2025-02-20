CREATE DATABASE IF NOT EXISTS ManagerTest;

USE ManagerTest;

-- Users table - used for app sign up and login 

CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- (Playlists) Tags table - used for Stotify API integration

CREATE TABLE IF NOT EXISTS Tags (
    tag_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    tag_name VARCHAR(255)
);

-- Tasks table

CREATE TABLE IF NOT EXISTS Tasks (
    task_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    task_description VARCHAR(255),
    task_owner VARCHAR(255),
    task_tag ENUM('cleaning', 'cooking', 'shopping', 'gardening', 'laundry', 'DIY', 'finance', 'home', 'pets', 'childcare'),
    task_due DATETIME,
    task_status ENUM('New', 'In Progress', 'Completed')
);

-- Archived Tasks table

CREATE TABLE IF NOT EXISTS ArchivedTasks (
	a_id INTEGER AUTO_INCREMENT PRIMARY KEY, 
    task_id INTEGER,
    task_name VARCHAR(255),
    task_description VARCHAR(255),
    task_owner VARCHAR(255),
    task_tag ENUM('cleaning', 'cooking', 'shopping', 'gardening', 'laundry', 'DIY', 'finance', 'home', 'pets', 'childcare'),
    task_due DATETIME, -- add not null?
    task_status ENUM('New', 'In Progress', 'Completed')
);

-- Goals table

CREATE TABLE IF NOT EXISTS Goals (
    goal_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    goal_name VARCHAR(255) NOT NULL,
    goal_target VARCHAR(255),
    goal_progress ENUM('Achieved', 'Almost Achieved', 'Attempted', 'Not Today'),
    goal_owner VARCHAR(255) NOT NULL
);

-- Hobbies table - for future application improvements

CREATE TABLE IF NOT EXISTS Hobbies (
    hobby_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    hobby_name VARCHAR(255) NOT NULL
);

-- Playlists table - for future application improvements

CREATE TABLE IF NOT EXISTS Playlists (
    p_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    p_name VARCHAR(255),
    p_tag VARCHAR(255)
);

-- Task Owner table

CREATE TABLE IF NOT EXISTS TaskOwner (
    task_owner VARCHAR(255) PRIMARY KEY,
    task_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Insert sample data into Tasks table
INSERT INTO Tasks
(task_name, task_description, task_owner, task_tag, task_due, task_status)
VALUES
('Test Task', 'Test Description', 'Katy', 'finance', '2024-08-28', 'New');

-- Insert unassigned task into Tasks table to test claim tasks functionality
INSERT INTO Tasks
(task_name, task_description)
VALUES
('Unasigned Task', 'for claiming');

-- Data checks

SELECT * FROM Tasks;
SELECT * FROM Goals;
SELECT * FROM Tags;
SELECT * FROM Users;

SELECT * FROM Tasks WHERE task_due >= '2024-08-06';


-- Trigger to add completed tasks to ArchivedTasks once updated as completed by user throught the app

DELIMITER //

CREATE TRIGGER archive_tasks
AFTER UPDATE ON Tasks
FOR EACH ROW
BEGIN
    IF NEW.task_status = 'Completed' THEN
        INSERT INTO ArchivedTasks (task_id, task_name, task_description, task_owner, task_tag, task_due, task_status)
        VALUES (NEW.task_id, NEW.task_name, NEW.task_description, NEW.task_owner, NEW.task_tag, NEW.task_due, NEW.task_status);
    END IF;
END //

DELIMITER ;

-- Trigger check

SELECT * FROM ArchivedTasks;
SELECT * FROM Tasks;

-- Stored procedure to delete tasks from Tasks table once archived

DELIMITER //

CREATE PROCEDURE delete_tasks()
BEGIN
	DELETE FROM Tasks
    WHERE task_id IN (SELECT task_id FROM ArchivedTasks);
END //

DELIMITER ;


-- START TRANSACTION;
-- CALL delete_tasks();

-- ROLLBACK;
-- COMMIT;
-- DROP PROCEDURE delete_tasks;


-- Scheduled event to call delete tasks procedure every second 

SET GLOBAL event_scheduler = ON;

DELIMITER //
CREATE EVENT IF NOT EXISTS remove_completed
ON SCHEDULE EVERY 1 SECOND
DO
CALL delete_tasks(); //

DELIMITER ;


