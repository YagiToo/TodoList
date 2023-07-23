from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QListWidget, \
    QWidget, QPushButton, QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QDateEdit, QLabel, \
    QDialog, QInputDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidgetItem
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt
import sys
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
from database import Database


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint)  # Set the WindowStaysOnTopHint flag
        self.database = Database()  # Initialize the Database class
        self.setWindowTitle("Login")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)
        
        self.setLayout(layout)
        
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter a valid username and password.")
            return
        
        user_id = self.database.login_user(username, password)
        if user_id:
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.username_input.clear()
            self.password_input.clear()

    def register(self):
        username, ok = QInputDialog.getText(self, "Register", "Username:")
        if ok:
            password, ok = QInputDialog.getText(self, "Register", "Password:", QLineEdit.Password)
            if ok:
                if self.database.register_user(username, password):
                    QMessageBox.information(self, "Registration Successful", "User registered successfully.")
                    self.username_input.setText(username)
                    self.password_input.setText(password)
                else:
                    QMessageBox.warning(self, "Registration Failed", "Username already exists.")

class MainWindow(QMainWindow):
    def __init__(self, user_id):  # Add user_id as a parameter to the __init__ method
        super().__init__()
        self.logged_in = False  # Flag to check if the user is logged in
        self.user_id = user_id  # Store the user_id
        self.database = Database()  # Initialize the Database class
        self.setWindowTitle("Todo List")
        self.resize(800, 600)

        # Set style and font
        self.set_style()
        
        # Create UI elements
        self.task_input = QLineEdit()
        self.due_date_input = QDateEdit()
        self.priority_combo = QComboBox()
        self.add_button = QPushButton("Add Task")
        self.task_list = QListWidget()
        self.complete_button = QPushButton("Mark as Complete")
        self.delete_button = QPushButton("Delete Task")
        self.filter_combo = QComboBox()
        self.sort_combo = QComboBox()
        
        # Set up layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Todo List"))
        
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("New Task:"))
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(QLabel("Due Date:"))
        input_layout.addWidget(self.due_date_input)
        input_layout.addWidget(QLabel("Priority:"))
        input_layout.addWidget(self.priority_combo)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.complete_button)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addWidget(QLabel("Sort by:"))
        filter_layout.addWidget(self.sort_combo)
        
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.task_list)
        
        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Connect button click events
        self.add_button.clicked.connect(self.add_task)
        self.complete_button.clicked.connect(self.mark_as_complete)
        self.delete_button.clicked.connect(self.delete_task)
        self.filter_combo.currentIndexChanged.connect(self.filter_tasks)
        self.sort_combo.currentIndexChanged.connect(self.sort_tasks)
        
        # Populate priority and filter options
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.filter_combo.addItems(["All", "Incomplete", "Complete"])
        self.sort_combo.addItems(["None", "Due Date", "Priority"])



        # Create the logout button
        logout_button = QPushButton("Logout", self)
        logout_button.clicked.connect(self.logout)

        # Create the save button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_tasks)

        # Create a horizontal layout for the logout and save buttons
        top_button_layout = QHBoxLayout()
        top_button_layout.addWidget(logout_button)
        top_button_layout.addWidget(save_button)

        # Create the buttons for data visualization
        statistics_button = QPushButton("Show Statistics", self)
        statistics_button.clicked.connect(self.show_task_statistics)

        priority_button = QPushButton("Show Priority Distribution", self)
        priority_button.clicked.connect(self.show_priority_distribution)

        # Create a horizontal layout for the data visualization buttons
        data_viz_button_layout = QHBoxLayout()
        data_viz_button_layout.addWidget(statistics_button)
        data_viz_button_layout.addWidget(priority_button)

        # Create a vertical layout for the buttons section
        button_layout = QVBoxLayout()
        button_layout.addLayout(top_button_layout)
        button_layout.addWidget(self.task_list)
        button_layout.addLayout(data_viz_button_layout)

        main_layout.addLayout(button_layout)
        
        self.load_tasks(self.user_id)  # Load tasks for the current user


 
    def set_style(self):
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#f0f0f0"))
        palette.setColor(QPalette.WindowText, QColor("#333333"))
        self.setPalette(palette)
        
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
    def add_task(self):
        task_name = self.task_input.text()
        due_date = self.due_date_input.date().toString(Qt.ISODate)
        priority = self.priority_combo.currentText()
        
        if not task_name:
            QMessageBox.warning(self, "Error", "Please enter a task name.")
            return
        
        self.task_list.addItem(f"{task_name} - Due: {due_date} - Priority: {priority}")
        self.task_input.clear()
        self.due_date_input.setDate(self.due_date_input.minimumDate())
        self.priority_combo.setCurrentIndex(0)
        
    def mark_as_complete(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            text = selected_item.text()
            if " - Complete" not in text:
                selected_item.setText(text + " - Complete")
        
    def delete_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            self.task_list.takeItem(self.task_list.row(selected_item))
        
    def filter_tasks(self, index):
        filter_text = self.filter_combo.currentText()
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if filter_text == "All":
                item.setHidden(False)
            elif filter_text == "Complete" and " - Complete" not in item.text():
                item.setHidden(True)
            elif filter_text == "Incomplete" and " - Complete" in item.text():
                item.setHidden(True)
            else:
                item.setHidden(False)
                
    def sort_tasks(self, index):
        sort_text = self.sort_combo.currentText()
        if sort_text == "None":
            self.task_list.sortItems(Qt.AscendingOrder)
        elif sort_text == "Due Date":
            self.task_list.sortItems(Qt.AscendingOrder)
        elif sort_text == "Priority":
            self.task_list.sortItems(Qt.DescendingOrder)
        
    def save_tasks(self):
        tasks = [self.task_list.item(i).text() for i in range(self.task_list.count())]
        self.database.save_tasks(tasks)
        
        
    def login(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.logged_in = True
            self.show()
        else:
            self.close()

    def event(self, event):
        # Handle close event
        if event.type() == QEvent.Close and not self.logged_in:
            event.ignore()  # Ignore the close event
        return super().event(event)
        
        

    def load_tasks(self, user_id):
        tasks = self.database.load_tasks(user_id)  # Fetch tasks for the current user
        self.task_list.clear()
        for description, due_date, priority, status in tasks:
            item = QListWidgetItem(description + " - Due: " + due_date.strftime("%Y-%m-%d") + " - Priority: " + priority)
            if status:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.task_list.addItem(item)

        
    def show_task_statistics(self):
        tasks = [self.task_list.item(i).text() for i in range(self.task_list.count())]
        complete_tasks = [task for task in tasks if " - Complete" in task]
        incomplete_tasks = [task for task in tasks if " - Complete" not in task]
        num_complete = len(complete_tasks)
        num_incomplete = len(incomplete_tasks)

        # Data Visualization - Task Completion Rate
        labels = ["Complete", "Incomplete"]
        sizes = [num_complete, num_incomplete]
        colors = ["green", "red"]
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
        plt.axis("equal")
        plt.title("Task Completion Rate")
        plt.show()

    def show_priority_distribution(self):
        tasks = [self.task_list.item(i).text() for i in range(self.task_list.count())]
        priorities = [task.split(" - Priority: ")[1] for task in tasks]
        
        # Data Visualization - Priority Distribution
        plt.figure(figsize=(8, 6))
        sns.countplot(x=priorities, order=["Low", "Medium", "High"])
        plt.title("Priority Distribution")
        plt.show()


    def logout(self):
        # Implement the logout functionality here
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to log out?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Hide the main window and show the login dialog
            self.hide()
            login_dialog = LoginDialog()
            if login_dialog.exec_() == QDialog.Accepted:
                self.user_id = login_dialog.database.login_user(login_dialog.username_input.text(), login_dialog.password_input.text())
                if self.user_id:
                    self.show()
                    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        user_id = login_dialog.database.login_user(login_dialog.username_input.text(), login_dialog.password_input.text())
        if user_id:
            window = MainWindow(user_id)
            window.show()
            sys.exit(app.exec_())
    sys.exit()