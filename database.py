import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="todo_list_db"
        )
        self.cursor = self.connection.cursor(buffered=True)
        self.create_tables()
        self.user_id = None  # Add the user_id attribute

    def create_tables(self):
        tasks_table = (
            "CREATE TABLE IF NOT EXISTS tasks ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT,"
            "  task_name VARCHAR(255) NOT NULL,"
            "  due_date DATE NOT NULL,"
            "  priority VARCHAR(50) NOT NULL,"
            "  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE"
            ")"
        )

        users_table = (
            "CREATE TABLE IF NOT EXISTS users ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  username VARCHAR(255) NOT NULL UNIQUE,"
            "  password VARCHAR(255) NOT NULL"
            ")"
        )

        self.cursor.execute(users_table)
        self.cursor.execute(tasks_table)
        self.connection.commit()


    def register_user(self, username, password):
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (username, password))
            self.connection.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def create_user(self, username, password):
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (username, password))
            self.connection.commit()
            return True
        except Error as e:
            print("Error while creating user:", e)
            return False

    def login_user(self, username, password):
        query = "SELECT id FROM users WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def insert_task(self, task):
        query = "INSERT INTO tasks (user_id, description, due_date, priority, status) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.cursor.execute(query, task)
            self.connection.commit()
            return True
        except Error as e:
            print("Error while inserting task:", e)
            return False

    def delete_task(self, user_id, description, due_date, priority):
        query = "DELETE FROM tasks WHERE user_id = %s AND description = %s AND due_date = %s AND priority = %s"
        try:
            self.cursor.execute(query, (user_id, description, due_date, priority))
            self.connection.commit()
            return True
        except Error as e:
            print("Error while deleting task:", e)
            return False

    def load_tasks(self, user_id):
        query = "SELECT description, due_date, priority, status FROM tasks WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()

    def save_tasks(self, tasks):
        if not self.user_id:
            return

        query = "DELETE FROM tasks WHERE user_id = %s"
        self.cursor.execute(query, (self.user_id,))
        for task in tasks:
            query = "INSERT INTO tasks (user_id, task_name, due_date, priority) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (self.user_id, task.split(" - ")[0], task.split(" - Due: ")[1].split(" - Priority: ")[0], task.split(" - Priority: ")[1]))
        self.connection.commit()

    def close_connection(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Connection to the database closed")