from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
     QLineEdit, QPushButton, QComboBox, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
     QVBoxLayout, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class DatabaseConnection:
     def __init__(self, database_file="database.db"):
          self.database_file = database_file

     def connect(self):
          connection = sqlite3.connect(self.database_file)
          return connection


class MainWindow(QMainWindow):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("Student Management System")
          self.setMinimumSize(800, 600)

          self.menuBar().setNativeMenuBar(False)

          file_menu_item = self.menuBar().addMenu("&File")
          help_menu_item = self.menuBar().addMenu("&Help")
          edit_menu_item = self.menuBar().addMenu("&Edit")

          add_student_action = QAction(QIcon("./icons/add.png"),"Add Student", self)
          add_student_action.triggered.connect(self.insert)
          file_menu_item.addAction(add_student_action)

          about_action = QAction("About", self)
          help_menu_item.addAction(about_action)
          # only mac computer
          about_action.setMenuRole(QAction.MenuRole.NoRole)
          about_action.triggered.


          edit_menu_action = QAction(QIcon("./icons/search.png"),"Search", self)
          edit_menu_action.triggered.connect(self.search)
          edit_menu_item.addAction(edit_menu_action)

          self.table = QTableWidget()
          self.table.setColumnCount(4)
          self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
          self.table.verticalHeader().setVisible(False)
          self.setCentralWidget(self.table)

          # Create toolbar and add toolbar elements.
          toolbar = QToolBar()
          toolbar.setMovable(True)
          self.addToolBar(toolbar)
          toolbar.addAction(add_student_action)
          toolbar.addAction(edit_menu_action)

          # Create status bar and add status bar elements.
          self.statusbar = QStatusBar()
          self.setStatusBar(self.statusbar)

          # Detect a cell clicked.
          self.table.cellClicked.connect(self.cell_clicked)

     def cell_clicked(self):
          edit_button = QPushButton("Edit Record")
          edit_button.clicked.connect(self.edit)

          delete_button = QPushButton("Delete Record")
          delete_button.clicked.connect(self.delete)

          # Delete duplicated button whenever clicked.
          children = self.findChildren(QPushButton)
          if children:
               for child in children:
                    self.statusbar.removeWidget(child)

          self.statusbar.addWidget(edit_button)
          self.statusbar.addWidget(delete_button)

     def load_data(self):
          connection = DatabaseConnection().connect()
          result = connection.execute("SELECT * FROM students")
          self.table.setRowCount(0)
          for row_number, row_data in enumerate(result):
               self.table.insertRow(row_number)
               for column_number, data in enumerate(row_data):
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
          connection.close()

     def insert(self):
          dialog = InsertDialog()
          dialog.exec()

     def search(self):
          dialog = SearchDialog()
          dialog.exec()

     def edit(self):
          dialog = EditDialog()
          dialog.exec()

     def delete(self):
          dialog = DeleteDialog()
          dialog.exec()

     def about(self):
          dialog = AboutDialog()
          dialog.exec()

class About(QMessageBox):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("About")
          content = """
          this app was created during the course.
          Feel free to modify it to use practical use.
          """
          self.setText(content)


class EditDialog(QDialog):

     def __init__(self):
          super().__init__()
          self.setWindowTitle("Update Student Data")
          self.setFixedWidth(300)
          self.setFixedHeight(300)

          layout = QVBoxLayout()

          # Get student name from selected row.
          index = main_window.table.currentRow()
          student_name = main_window.table.item(index, 1).text()

          # Get ID from selected row.
          self.student_id = main_window.table.item(index, 0).text()

          # Add student name.
          self.student_name = QLineEdit(student_name)
          self.student_name.setPlaceholderText("Name")
          layout.addWidget(self.student_name)

          # Add combo box of course
          # course_name below is local variable. differnt from self.course_name.
          course_name = main_window.table.item(index, 2).text()
          self.course_name = QComboBox()
          courses = ["Biology", "Math", "Astronomy", "Physics"]
          self.course_name.addItems(courses)
          self.course_name.setCurrentText(course_name)
          layout.addWidget(self.course_name)

          # Add mobile widget.
          mobile_number = main_window.table.item(index, 3).text()
          self.mobile_number = QLineEdit(mobile_number)
          self.mobile_number.setPlaceholderText("000000000")
          layout.addWidget(self.mobile_number)

          submit_button = QPushButton("Update")
          submit_button.clicked.connect(self.update_student)
          layout.addWidget(submit_button)

          self.setLayout(layout)

     def update_student(self):
          connection = DatabaseConnection().connect()
          cursor = connection.cursor()
          cursor.execute("UPDATE student SET name = ?, course = ?, mobile = ? WHERE id = ?",
                          (self.student_name.text(),
                           self.course_name.itemText(self.course_name.currentIndex()),
                           self.mobile_number.text(),
                           self.student_id))

          connection.commit()
          cursor.close()
          connection.close()
          # Refresh table in main window.
          main_window.load_data()


class DeleteDialog(QDialog):
     
     def __init__(self):
          super().__init__()
          self.setWindowTitle("Delete Student Data")

          layout = QGridLayout()
          confirmation = QLabel("Are you sure you want to delete?")
          yes = QPushButton("Yes")
          no = QPushButton("No")

          layout.addWidget(confirmation, 0, 0, 1, 2)
          layout.addWidget(yes, 1, 0)
          layout.addWidget(no, 1, 1)
          self.setLayout(layout)

          yes.clicked.connect(self.delete_student)


     def delete_student(self):
          index = main_window.table.currentRow()
          student_id = main_window.table.item(index, 0).text()

          connection = DatabaseConnection().connect()
          cursor = connection.cursor()
          cursor.execute("DELETE from students WHERE id = ?",
                          (student_id,))
          connection.commit()
          cursor.close()
          connection.close()

          main_window.load_data()

          self.close()

          confirmation_widget = QMessageBox()
          confirmation_widget.setWindowTitle("Success")
          confirmation_widget.setText("The record was deleted successfully!")
          confirmation_widget.exec()


class InsertDialog(QDialog):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("Insert Student Data")
          self.setFixedWidth(300)
          self.setFixedHeight(300)

          layout = QVBoxLayout()

          self.student_name = QLineEdit()
          self.student_name.setPlaceholderText("Name")
          layout.addWidget(self.student_name)

          self.course_name = QComboBox()
          courses = ["Biology", "Math", "Astronomy", "Physics"]
          self.course_name.addItems(courses)
          layout.addWidget(self.course_name)

          self.mobile_number = QLineEdit()
          self.mobile_number.setPlaceholderText("000-000-0000")
          layout.addWidget(self.mobile_number)

          submit_button = QPushButton("Submit")
          submit_button.clicked.connect(self.add_student)
          layout.addWidget(submit_button)

          self.setLayout(layout)

     def add_student(self):
          name = self.student_name.text()
          course = self.course_name.itemText(self.course_name.currentIndex())
          mobile = self.mobile_number.text()

          connection = DatabaseConnection().connect()
          cursor = connection.cursor()
          cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)", 
                         (name, course, mobile))
          connection.commit()
          cursor.close()
          connection.close()

          main_window.load_data()


class SearchDialog(QDialog):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("Search Student")
          self.setFixedWidth(300)
          self.setFixedHeight(300)

          layout = QVBoxLayout()

          self.student_name = QLineEdit()
          self.student_name.setPlaceholderText("Name")
          layout.addWidget(self.student_name)

          search_button = QPushButton("Search")
          search_button.clicked.connect(self.search_student)
          layout.addWidget(search_button)

          self.setLayout(layout)

     def search_student(self):
          name = self.student_name.text()

          connection = DatabaseConnection().connect()
          cursor = connection.cursor()
          result = cursor.execute("SELECT * FROM students where Name = ?", (name,))

          # rows = list(result)

          items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
          for item in items:
               main_window.table.item(item.row(),1).setSelected(True)

          cursor.close()
          connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())

